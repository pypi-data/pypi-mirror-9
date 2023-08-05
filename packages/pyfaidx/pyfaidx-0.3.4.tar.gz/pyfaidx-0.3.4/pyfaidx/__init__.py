# pylint: disable=R0913, R0914

"""
Fasta file -> Faidx -> Fasta -> FastaRecord -> Sequence
"""

from __future__ import division
import sys
import os
import warnings
from six import PY2, PY3, string_types
from six.moves import zip_longest
try:
    from collections import OrderedDict
except ImportError: #python 2.6
    from ordereddict import OrderedDict
from collections import namedtuple
import re

if PY2:
    import string

dna_bases = re.compile(r'([ACTGNactgYRWSKMDVHBXyrwskmdvhbx]+)')


class FastaIndexingError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class FetchError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class BedError(Exception):
    def __init__(self, msg=None):
        self.msg = 'Malformed BED entry!\n' if not msg else msg

    def __str__(self):
        return repr(self.msg)


class RegionError(Exception):
    def __init__(self, msg=None):
        self.msg = 'Malformed region! Format = rname:start-end.\n' if not msg else msg

    def __str__(self):
        return repr(self.msg)


class Sequence(object):
    """
    name = FASTA entry name
    seq = FASTA sequence
    start, end = coordinates of subsequence (optional)
    comp = boolean switch for complement property
    """
    def __init__(self, name='', seq='', start=None, end=None, comp=False):
        self.name = name
        self.seq = seq
        self.start = start
        self.end = end
        self.comp = comp
        assert isinstance(name, string_types)
        assert isinstance(seq, string_types)

    def __getitem__(self, n):
        if isinstance(n, slice):
            start, stop, step = n.indices(len(self))
            if stop == -1:
                stop = start
            else:
                stop = len(self) - stop
            if self.start and self.end:
                return self.__class__(self.name, self.seq[n.start:n.stop:n.step],
                                  self.start + start, self.end - stop, self.comp)
            else:
                return self.__class__(self.name, self.seq[n.start:n.stop:n.step], self.comp)
        elif isinstance(n, int):
            if n < 0:
                n = len(self) + n
            if self.start:
                return self.__class__(self.name, self.seq[n], self.start + n,
                                  self.start + n, self.comp)
            else:
                return self.__class__(self.name, self.seq[n], self.comp)

    def __str__(self):
        return self.seq

    def __neg__(self):
        """ Returns the reverse compliment of sequence
        >>> x = Sequence(name='chr1', seq='ATCGTA', start=1, end=6)
        >>> -x
        >chr1:6-1 (complement)
        TACGAT
        """
        return self[::-1].complement

    def __repr__(self):
        return '\n'.join([''.join(['>', self.longname]), self.seq])

    def __len__(self):
        """
        >>> len(Sequence('chr1', 'ACT'))
        3
        """
        return len(self.seq)

    @property
    def longname(self):
        """ Return the fancy name for the sequence, including start, end, and complementation.
        >>> x = Sequence(name='chr1', seq='ATCGTA', start=1, end=6, comp=True)
        >>> x.longname
        'chr1:1-6 (complement)'
        """
        name = self.name
        if self.start and self.end:
            name = ':'.join([name, '-'.join([str(self.start), str(self.end)])])
        if self.comp:
            name += ' (complement)'
        return name


    @property
    def complement(self):
        """ Returns the compliment of self.
        >>> x = Sequence(name='chr1', seq='ATCGTA')
        >>> x.complement
        >chr1 (complement)
        TAGCAT
        """
        comp = self.__class__(self.name, complement(self.seq),
                              start=self.start, end=self.end)
        comp.comp = False if self.comp else True
        return comp

    @property
    def reverse(self):
        """ Returns the reverse of self.
        >>> x = Sequence(name='chr1', seq='ATCGTA')
        >>> x.reverse
        >chr1
        ATGCTA
        """
        return self[::-1]

    @property
    def gc(self):
        """ Return the GC content of seq as a float
        >>> x = Sequence(name='chr1', seq='ATCGTA')
        >>> y = round(x.gc, 2)
        >>> y == 0.33
        True
        """
        g = self.seq.count('G')
        g += self.seq.count('g')
        c = self.seq.count('C')
        c += self.seq.count('c')
        return (g + c) / len(self.seq)


class IndexRecord(namedtuple('IndexRecord', ['rlen', 'offset', 'lenc', 'lenb'])):
    __slots__ = ()

    def __getitem__(self, key):
        if type(key) == str:
            return getattr(self, key)
        return tuple.__getitem__(self, key)

    def __str__(self):
        return "{rlen:n}\t{offset:n}\t{lenc:n}\t{lenb:n}\n".format(**self._asdict())


class Faidx(object):
    """ A python implementation of samtools faidx FASTA indexing """
    def __init__(self, filename, default_seq=None, key_function=None,
                 as_raw=False, strict_bounds=False, read_ahead=None,
                 mutable=False, split_char=None):
        """
        filename: name of fasta file
        key_function: optional callback function which should return a unique
          key for the self.index dictionary when given rname.
        as_raw: optional parameter to specify whether to return sequences as a
          Sequence() object or as a raw string.
          Default: False (i.e. return a Sequence() object).
        """
        self.filename = filename
        if mutable:
            self.file = open(filename, 'r+b')
            warnings.warn("FASTA mutability is experimental. Use it carefully!", FutureWarning)
        else:
            self.file = open(filename, 'rb')
        self.indexname = filename + '.fai'
        self.key_function = key_function if key_function else lambda rname: rname
        self.as_raw = as_raw
        self.default_seq = default_seq
        self.strict_bounds = strict_bounds
        self.index = OrderedDict()
        self.buffer = dict((('seq', None), ('name', None), ('start', None), ('end', None)))
        self.read_ahead = read_ahead
        self.mutable = mutable

        if os.path.exists(self.indexname):
            self.read_fai(split_char)
        else:
            try:
                self.build_index()
            except FastaIndexingError as e:
                os.remove(self.indexname)
                raise FastaIndexingError(e)
            self.read_fai(split_char)

    def __contains__(self, region):
        if not self.buffer['name']:
            return False
        name, start, end = region
        if self.buffer['name'] == name and self.buffer['start'] <= start and self.buffer['end'] >= end:
            return True
        else:
            return False

    def __repr__(self):
        return 'Faidx("%s")' % (self.filename)

    def read_fai(self, split_char):
        duplicate_ids = []
        with open(self.indexname) as index:
            for line in index:
                line = line.strip()
                rname, rlen, offset, lenc, lenb = line.split('\t')
                rname = self.key_function(rname).split(split_char)
                for key in rname:
                    if key in self.index and not split_char:
                        raise ValueError('Duplicate key "%s"' % rname)
                    elif key in self.index and split_char:
                        duplicate_ids.append(key)
                        continue
                    else:
                        self.index[key] = IndexRecord(*map(int, (rlen,
                                                                   offset,
                                                                   lenc,
                                                                   lenb)))
            for dup in duplicate_ids:
                self.index.pop(dup, None)

    def build_index(self):
        with open(self.filename, 'r') as fastafile:
            with open(self.indexname, 'w') as indexfile:
                rname = None  # reference sequence name
                offset = 0  # binary offset of end of current line
                rlen = 0  # reference character length
                blen = 0  # binary line length (includes newline)
                clen = 0  # character line length
                short_lines = []  # lines shorter than blen
                line_number = 0
                for line in fastafile:
                    line_blen = len(line)
                    line_clen = len(line.rstrip('\n\r'))
                    if (line[0] == '>') and (rname is None):
                        rname = line.rstrip()[1:].split()[0]
                        offset += line_blen
                        thisoffset = offset
                    elif line[0] != '>':
                        if blen == 0:
                            blen = line_blen
                        # only one short line should be allowed
                        # before we hit the next header
                        elif line_clen == 0:
                            sys.stderr.write("Warning: blank line in >{0} at "
                                             "line {1:n}.".format(rname,
                                                                  line_number +
                                                                  1))
                        elif blen > line_blen:
                            short_lines.append(line_number)
                            if len(short_lines) > 1:
                                raise FastaIndexingError("Line length of fasta"
                                                         " file is not "
                                                         "consistent! "
                                    "Early short line found in >{0} at "
                                    "line {1:n}.".format(rname,
                                                         short_lines[0] + 1))
                        elif blen < line_blen:
                            raise FastaIndexingError("Line length of fasta "
                                                     "file is not consistent! "
                                                     "Long line found in >{0} "
                                                     "at line {1:n}."
                                                     "".format(rname,
                                                               line_number +
                                                               1))
                        offset += line_blen
                        if clen == 0:
                            clen = line_clen
                        rlen += line_clen
                    elif (line[0] == '>') and (rname is not None):
                        indexfile.write("{0}\t{1:d}\t{2:d}\t{3:d}\t{4:d}\n".format(rname, rlen, thisoffset, clen, blen))
                        blen = 0
                        rlen = 0
                        clen = 0
                        short_lines = []
                        rname = line.rstrip()[1:].split()[0]
                        offset += line_blen
                        thisoffset = offset
                    line_number += 1
                indexfile.write("{0}\t{1:d}\t{2:d}\t{3:d}\t{4:d}\n".format(rname, rlen, thisoffset, clen, blen))

    def write_fai(self):
        with open(self.indexname, 'w') as outfile:
            for k, v in self.index.items():
                outfile.write('\t'.join([k, str(v)]))

    def from_buffer(self, start, end):
        i_start = start - self.buffer['start']  # want [0, 1) coordinates from [1, 1] coordinates
        i_end = end - self.buffer['start'] + 1
        return self.buffer['seq'][i_start:i_end]

    def fill_buffer(self, name, start, end):
        try:
            seq = self.from_file(name, start, end)
            self.buffer['seq'] = seq
            self.buffer['start'] = start
            self.buffer['end'] = end
            self.buffer['name'] = name
        except FetchError:
            pass

    def fetch(self, name, start, end):
        if self.read_ahead and not (name, start, end) in self:
            self.fill_buffer(name, start, end + self.read_ahead)

        if (name, start, end) in self:
            seq = self.from_buffer(start, end)
        else:
            seq = self.from_file(name, start, end)

        return self.format_seq(seq, name, start, end)

    def from_file(self, rname, start, end, internals=False):
        """ Fetch the sequence ``[start:end]`` from ``rname`` using 1-based coordinates
        1. Count newlines before start
        2. Count newlines to end
        3. Difference of 1 and 2 is number of newlines in [start:end]
        4. Seek to start position, taking newlines into account
        5. Read to end position, return sequence
        """
        try:
            i = self.index[rname]
        except KeyError:
            raise FetchError("Requested rname {0} does not exist! "
                             "Please check your FASTA file.".format(rname))
        start0 = start - 1  # make coordinates [0,1)
        if start0 < 0:
            raise FetchError("Requested start coordinate must be greater than 1.")
        seq_len = end - start0

        newlines_total = int(i.rlen / i.lenc * (i.lenb - i.lenc))
        newlines_before = int((start0 - 1) / i.lenc *
                              (i.lenb - i.lenc)) if start0 > 0 else 0
        newlines_to_end = int(end / i.lenc * (i.lenb - i.lenc))
        newlines_inside = newlines_to_end - newlines_before
        seq_blen = newlines_inside + seq_len
        bstart = i.offset + newlines_before + start0
        bend = i.offset + newlines_total + i.rlen
        self.file.seek(bstart)

        if bstart + seq_blen > bend and not self.strict_bounds:
            seq_blen = bend - bstart
        elif bstart + seq_blen > bend and self.strict_bounds:
            raise FetchError("Requested end coordinate {0:n} outside of {1}. "
                             "\n".format(end, rname))
        if seq_blen > 0:
            seq = self.file.read(seq_blen).decode()
        elif seq_blen <= 0 and not self.strict_bounds:
            seq = ''
        elif seq_blen <= 0 and self.strict_bounds:
            raise FetchError("Requested coordinates start={0:n} end={1:n} are "
                             "invalid.\n".format(start, end))
        if not internals:
            return seq.replace('\n', '')
        else:
            return (seq, locals())

    def format_seq(self, seq, rname, start, end):
        start0 = start - 1
        if len(seq) < end - start0 and self.default_seq:  # Pad missing positions with default_seq
            pad_len = end - start0 - len(seq)
            seq = ''.join([seq, pad_len * self.default_seq])
        else:  # Return less than requested range
            end = start0 + len(seq)

        if self.as_raw:
            return seq
        else:
            return Sequence(name=rname, start=int(start),
                            end=int(end), seq=seq)

    def to_file(self, rname, start, end, seq):
        """ Write sequence in region from start-end, overwriting current
        contents of the FASTA file. """
        if not self.mutable:
            raise IOError("Write attempted for immutable Faidx instance. Set mutable=True to modify original FASTA.")
        file_seq, internals = self.from_file(rname, start, end, internals=True)
        if len(seq) != len(file_seq) - internals['newlines_inside']:
            raise IOError("Specified replacement sequence needs to have the same length as original.")
        elif len(seq) == len(file_seq) - internals['newlines_inside']:
            line_len = internals['i'].lenc
            self.file.seek(internals['bstart'])
            if internals['newlines_inside'] == 0:
                self.file.write(seq.encode())
            elif internals['newlines_inside'] > 0:
                n = 0
                m = file_seq.index('\n')
                while m < len(seq):
                    self.file.write(''.join([seq[n:m], '\n']).encode())
                    n = m
                    m += line_len
                self.file.write(seq[n:].encode())

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.file.close()


class FastaRecord(object):
    def __init__(self, name, fa):
        self.name = name
        self._fa = fa
        self._len = self._fa.faidx.index[self.name].rlen

    def __getitem__(self, n):
        """Return sequence from region [start, end)

        Coordinates are 0-based, end-exclusive."""
        try:
            if isinstance(n, slice):
                start, stop, step = n.start, n.stop, n.step
                if not start:
                    start = 0
                if not stop:
                    stop = len(self)
                if stop < 0:
                    stop = len(self) + stop
                if start < 0:
                    start = len(self) + start
                return self._fa.get_seq(self.name, start + 1, stop)[::step]

            elif isinstance(n, int):
                if n < 0:
                    n = len(self) + n
                return self._fa.get_seq(self.name, n + 1, n + 1)
        except FetchError:
            raise

    def __iter__(self):
        """ Construct a line-based iterator that respects the original line lengths. """
        line_len = self._fa.faidx.index[self.name].lenc
        start = 0
        while True:
            end = start + line_len
            if end < len(self):
                yield self[start:end]
            else:
                yield self[start:]
                raise StopIteration
            start += line_len

    def __repr__(self):
        return 'FastaRecord("%s")' % (self.name)

    def __len__(self):
        return self._len

    def __str__(self):
        return str(self[:])


class MutableFastaRecord(FastaRecord):
    def __init__(self, name, fa):
        super(MutableFastaRecord, self).__init__(name, fa)

    def __setitem__(self, n, value):
        """Mutate sequence in region [start, end)
        to value.
        Coordinates are 0-based, end-exclusive."""
        try:
            if isinstance(n, slice):
                start, stop, step = n.start, n.stop, n.step
                if step:
                    raise IndexError("Step operator is not implemented.")
                if not start:
                    start = 0
                if not stop:
                    stop = len(self)
                if stop < 0:
                    stop = len(self) + stop
                if start < 0:
                    start = len(self) + start
                self._fa.faidx.to_file(self.name, start + 1, stop, value)

            elif isinstance(n, int):
                if n < 0:
                    n = len(self) + n
                return self._fa.faidx.to_file(self.name, n + 1, n + 1, value)
        except (FetchError, IOError):
            raise


class Fasta(object):
    def __init__(self, filename, default_seq=None, key_function=None, as_raw=False, strict_bounds=False, read_ahead=None, mutable=False, split_char=None):
        """
        An object that provides a pygr compatible interface.
        filename: name of fasta file
        """
        self.filename = filename
        self.mutable = mutable
        self.faidx = Faidx(filename, key_function=key_function, as_raw=as_raw,
                           default_seq=default_seq, strict_bounds=strict_bounds,
                           read_ahead=read_ahead, mutable=mutable, split_char=split_char)
        self.keys = self.faidx.index.keys
        if not self.mutable:
            self.records = dict([(rname, FastaRecord(rname, self)) for rname in self.keys()])
        elif self.mutable:
            self.records = dict([(rname, MutableFastaRecord(rname, self)) for rname in self.keys()])

    def __contains__(self, rname):
        """Return True if genome contains record."""
        return rname in self.faidx.index

    def __getitem__(self, rname):
        """Return a chromosome by its name, or its numerical index."""
        if isinstance(rname, int):
            rname = tuple(self.keys())[rname]
        try:
            return self.records[rname]
        except KeyError:
            raise KeyError("{0} not in {1}.".format(rname, self.filename))

    def __repr__(self):
        return 'Fasta("%s")' % (self.filename)

    def __iter__(self):
        for rname in self.keys():
            yield self[rname]

    def get_seq(self, name, start, end):
        """Return a sequence by record name and interval [start, end).

        Coordinates are 0-based, end-exclusive.
        """
        # Get sequence from real genome object and save result.
        return self.faidx.fetch(name, start, end)

    def close(self):
        self.__exit__()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.faidx.__exit__(*args)


def wrap_sequence(n, sequence, fillvalue=''):
    args = [iter(sequence)] * n
    for line in zip_longest(fillvalue=fillvalue, *args):
        yield ''.join(line + ("\n",))


def complement(seq):
    """ Returns the compliment of seq.
    >>> seq = 'ATCGTA'
    >>> complement(seq)
    'TAGCAT'
    """
    if PY3:
        table = str.maketrans('ACTGNactgYRWSKMDVHBXyrwskmdvhbx', 'TGACNtgacRYWSMKHBDVXrywsmkhbdvx')
    elif PY2:
        table = string.maketrans('ACTGNactgYRWSKMDVHBXyrwskmdvhbx', 'TGACNtgacRYWSMKHBDVXrywsmkhbdvx')
    if len(re.findall(dna_bases, seq)) == 1:  # finds invalid characters if > 1
        return str(seq).translate(table)
    else:
        raise ValueError("Sequence contains non-DNA characters: \n {0}".format(''.join(wrap_sequence(70, seq))))



def translate_chr_name(from_name, to_name):
    chr_name_map = dict(zip(from_name, to_name))

    def map_to_function(rname):
        return chr_name_map[rname]

    return map_to_function


def bed_split(bed_entry):
    try:
        rname, start, end = bed_entry.rstrip().split()[:3]
    except IndexError:
        raise BedError('Malformed BED entry! {0}\n'.format(bed_entry.rstrip()))
    start, end = (int(start), int(end))
    return (rname, start, end)


def ucsc_split(region):
    try:
        rname, interval = region.split(':')
    except ValueError:
        rname = region
        interval = None
    try:
        start, end = interval.split('-')
        start, end = (int(start) - 1, int(end))
    except (AttributeError, ValueError):
        start, end = (None, None)
    return (rname, start, end)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
