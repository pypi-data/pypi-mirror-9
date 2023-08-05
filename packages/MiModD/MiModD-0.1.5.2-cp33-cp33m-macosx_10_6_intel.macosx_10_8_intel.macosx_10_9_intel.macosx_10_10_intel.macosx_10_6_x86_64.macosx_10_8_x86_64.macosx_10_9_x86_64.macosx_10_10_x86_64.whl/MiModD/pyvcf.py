import sys
import io
import gzip
import copy
from collections import OrderedDict

from . import pybcftools

class VCFcols:
    chrom, pos, id, ref, alt, qual, filter, info, format, first_sample = range(10)
    names = 'CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO'
    format_name = 'FORMAT'
    
class VCFEntry (object):
    """Object-based equivalent of a single body line of a vcf file.

    Tab-separated fields of the input line are stored as instance attributes.
    chrom:         CHROM field as string
    pos:           POS field as integer
    id:            ID field as string (None if undefined, i.e., '.' in vcf)
    ref:           REF field as string
    alt:           ALT field as string (None if undefined)
    qual:          QUAL field as float (None if undefined)
    filter:        FILTER field as string (None if undefined)
    info:          INFO field as OrderedDict of tag:value pairs, flags are represented by entries with a None value
    sampleinfo:    sample-specific fields; organized in an OrderedDict with keys taken from the FORMAT field and
                   values being dictionaries of sample names:sample-specific information."""
    
    na = '.'
    
    def __init__(self, vcfline, samplenames):
        """Generate a VCFEntry instance from a vcf line string.

        samplenames should be an ordered iterable of the sample names present
        in the vcf file. The genotype fields extracted from the vcfline string
        get stored internally under these names. None objects in samplenames
        signify that the corresponding genotype field should be ignored in the
        generation of the VCFEntry instance."""
        
        fields = vcfline.rstrip('\t\r\n').split('\t')
        self.samplenames = tuple(name for name in samplenames if name is not None)
        try:
            self.chrom = fields[0]
            self.pos = int(fields[1])
            self.id = fields[2] if fields[2]!='.' else None
            self.ref = fields[3]
            self.alt = fields[4] if fields[4]!='.' else None
            self.qual = float(fields[5]) if fields[5]!='.' else None
            self.filter = fields[6] if fields[6]!='.' else None
            # the INFO field needs conditional parsing for key/value pairs and flags (which have no '=')
            self.info = OrderedDict(kvpair if len(kvpair)>1 else (kvpair[0], None) for kvpair in (elem.split('=') for elem in fields[7].split(';')))

            if any(samplenames):
                formatkeys = fields[8].split(':')
                self.sampleinfo = OrderedDict(zip(formatkeys, ({} for i in formatkeys)))
                for sample, item in zip(samplenames, fields[9:]):
                    if samplenames is not None:
                        for no, info in enumerate(item.split(':')):
                            self.sampleinfo[formatkeys[no]][sample] = info
            else:
                self.sampleinfo = OrderedDict()
        except IndexError:
            # this line does not have the right number of columns
            # or some other parsing problem, 
            # however, we want to check the possibility that it is
            # a blank line or a line consisting of whitespace only.
            # If that is the case, then we want to raise a fatal error
            # only if the line is followed by any non-empty content.
            # This has to be detected at a higher level so
            # here we just transform the error to make it unique.
            if vcfline.strip():
                raise
            else:
                raise RuntimeError ('Unexpected blank line in VCF file body.')


    @property
    def alt_list(self):
        if self.alt:
            return self.alt.split(',')
        else:
            return []

    @alt_list.setter
    def alt_list(self, allele_list):
        seen = set()
        self.alt = ','.join(al for al in allele_list if al not in seen and not seen.add(al))

    def alt_as_num(self, allele):
        return self.alt_list.index(allele)+1

    def alt_from_num(self, num):
        return self.alt_list[num-1]
    
    def __str__(self):
        # None values need to be replaced by '.', and flags in the INFO field need special treatment again
        items_to_join = [self.chrom, str(self.pos), self.id or self.na, self.ref, self.alt or self.na, str(self.qual or self.na),
                         self.filter or self.na, ';'.join(k if v is None else '='.join((k,v)) for k,v in self.info.items())]
        if any(self.samplenames):
            items_to_join.extend([':'.join(k for k in self.sampleinfo)])
            items_to_join.extend([':'.join(d[sample] for d in self.sampleinfo.values()) for sample in self.samplenames])
        return '\t'.join(items_to_join)

    def copy (self):
        copy_of_self = copy.copy(self)
        copy_of_self.info = copy_of_self.info.copy()
        copy_of_self.sampleinfo = copy_of_self.sampleinfo.copy()
        return copy_of_self
    
    def sample_slice (self, samples):
        """Return a fake slice of the VCFEntry instance by samples.
        Original data is preserved, but the str representation looks like a slice."""

        for sample in samples:
            if sample not in self.samplenames:
                raise KeyError('{0} is not a valid sample in the input'.format(sample))

        vcf_slice = self.copy()
        vcf_slice.samplenames = samples
        return vcf_slice
        
class Info (object):
    def __init__(self, ifo=None):
        self.comments = OrderedDict()
        self.sample_names = ('', ) # an awkward default, look into improving it
        if ifo:
            while True:
                header_line = ifo.readline()
                if header_line[0:2] != '##':
                    break
                key, value = header_line.strip()[2:].split("=",1)
                self.comments.setdefault(key,[]).append(value)            

            if not header_line or header_line[0] != '#':
                raise RuntimeError(
                    'Could not parse vcf header information: Expected header line to start with #.')
            header_fields = header_line[1:].rstrip('\t\r\n').split('\t')
            if VCFcols.names != tuple(header_fields[0:8]):
                raise RuntimeError(
                    'Could not parse vcf header information: Unrecognized header fields.')
            if len(header_fields) > 8:
                if header_fields[8] != 'FORMAT':
                    raise RuntimeError(
                        'Could not parse vcf header information: unrecognized column title {0} instead of FORMAT.'
                        .format(header_fields[8]))
                self.sample_names = tuple(header_fields[9:])
                if not self.sample_names:
                    raise RuntimeError(
                        'Could not parse vcf header information: FORMAT column must be followed by at least one additional column.')
                # TO DO: check for duplicate sample names,
                # but make sure this does not break any MiModD vcf handling
            # contigs, samples and comment lines have direct counterparts
            # in the SAM/BAM header format and are parsed specially for
            # easier access
            self.contigs = OrderedDict()
            self.rginfo = OrderedDict()
            self.co= []
            # parse contigs into an ordered {ID: length} dictionary
            for value in self.comments.get('contig', []):
                contents = value[1:-1].split(',')
                d = dict(content.split('=') for content in contents)
                try:
                    self.contigs[d['ID']] = int(d['length'])
                except KeyError:
                    # ignore malformatted contig lines that have no
                    # 'ID' or/and no 'length' element
                    pass
            # parse mimodd-specific header lines (these get written by varcall)
            # parse rg information back into an 
            # ordered {ID: {key: value, ...}} dictionary
            # first step: synchronization of rginfo elements and sample names
            # TO DO: should be kept synchronous throughout the lifetime of an
            # Info instance
            if any(self.sample_names):
                for value in self.comments.get('rginfo', []):
                    contents = value[1:-1].split(',')
                    d = dict(content.split('=') for content in contents)
                    if d.get('Name'):
                        # in a genuine MiModD file every rginfo element
                        # should contain a Name element,
                        # so the above is really just protecting against
                        # other software using rginfo with a different tag structure
                        if d['Name'] in self.sample_names:
                            # only use rginfo if a corresponding sample name exists
                            # other rginfo is silently ignored
                            # TO DO: maybe a warning should be generated instead ?
                            self.rginfo[d['Name']] = {k:v for k,v in d.items() if k != 'Name'}
                # now check the sample names for names without associated rginfo
                # add these to rginfo too
                for name in self.sample_names:
                    if name and name not in self.rginfo:
                        self.rginfo[name] = {}
            elif len(self.comments.get('rginfo', [])) == 1:
                # if there are no sample names defined in the vcf,
                # but there is exactly one rginfo element, then
                # parse this element
                contents = self.comments['rginfo'][0][1:-1].split(',')
                d = dict(content.split('=') for content in contents)
                if d.get('Name'):
                    self.rginfo[d['Name']] = {k:v for k,v in d.items() if k != 'Name'}
            # parse comment lines
            self.co = [value[1:-1].split('=') for value in self.comments.get('comment', [])]
        else:
            self.comments['fileformat'] = 'VCFv4.2'
            
    def __str__(self):
        lines = []
        for key, valuelist in self.comments.items():
            for value in valuelist:
                lines.append('##' + '='.join((key, value)))
        ret = '\n'.join(lines)
        ret = '\n'.join((ret, '#'+'\t'.join(VCFcols.names)))
        if any(self.sample_names):
            optional_header = '\t{0}\t{1}'.format(VCFcols.format_name, '\t'.join(self.sample_names))
            ret += optional_header 
        return ret

    def sample_slice(self, samples):
        for sample in samples:
            if sample not in self.sample_names:
                raise KeyError('"{0}" is not a valid sample in the input'.format(sample))
        info_slice = copy.copy(self)
        info_slice.sample_names = samples
        return info_slice

   
class VCFReader (object):
    def __init__(self, ifo):
        try:
            ifo.seek(0)
        except:
            self.ifo_isseekable = False
        else:
            self.ifo_isseekable = True
        self.info = Info(ifo)
        if self.ifo_isseekable:
            self.body_start = ifo.tell()
        self.ifo = ifo
        
    def __iter__ (self):
        return self
    
    def __next__(self):
        try:
            return VCFEntry(next(self.ifo), self.info.sample_names)
        except StopIteration:
            # regular end of input
            raise
        except RuntimeError:
            # VCFEntry uses RuntimeError to signal a blank line in the input, 
            # but we consider this only an error if the line is followed
            # by additonal non-blank lines, so let's check this
            for line in self.ifo:
                if line.strip():
                    raise
            raise StopIteration
        except:
            # all other errors indicate a parsing problem 
            raise RuntimeError ('Malformed VCF file body.')
            

    def raw_iter (self):
        for line in self.ifo:
            yield line

    def cov_iter (self):
        """A specialized iterator providing fast access to per-sample coverage.

        Returns a tuple of (chrom, pos, {sample: coverage , ...}).
        Skips INDELs."""

        sample_names = self.info.sample_names
        dp_dict = {}
        for line in self.ifo:
            fields = line.split()
            for elem in fields[7].split(';'):
                if elem == 'INDEL':
                    break
            else:
                chrom = fields[0]
                pos = int(fields[1])
                dp_index = fields[8].split(':').index('DP')
                for c, sample in enumerate(sample_names, 9):
                    dp_dict[sample] = int(fields[c].split(':')[dp_index])
                yield chrom, pos, dp_dict

    def expand_samples (self):
        if any(self.info.sample_names):
            for e in self:
                for sample in e.samplenames:
                    if e.sampleinfo['GT'][sample] in ('0/1', '1/1'):
                        yield sample, e
        else:
            # this is not a multi-sample vcf, just yield everything
            for e in self:
                yield '', e
                    
    def by_sample (self):
        if not self.ifo_isseekable:
            raise NotImplementedError ('by_sample method is currently implemented only for real files in vcf format')
        if any(self.info.sample_names):
            for sample in self.info.sample_names:
                self.seek(0)
                for e in self:
                    if e.sampleinfo['GT'][sample] in ('0/1', '1/1'):
                        yield sample, e
        else:
            # this is not a multi-sample vcf, just yield everything
            for e in self:
                yield '', e

    def sample_slice (self, samples):
        # WARNING: this method is not doing what it is supposed to do
        # and will be removed or rewritten soon
        # -> do NOT use it !!
        reader_slice = copy.copy(self)
        reader_slice.info = reader_slice.info.sample_slice(samples)
        return reader_slice
    
    def filter (self, h_filters, v_filters = None):
        """An iterator over the lines of a vcf file that pass a user-defined genotype filter.

        The filters argument must be a dictionary of sample names:accepted genotypes, where
        the keys must be strings matching sample names declared in the vcf header line, and
        the values must be filter dictionaries of the form:
        {
        'GT' : values valid vcf genotype strings (e.g., '1/1', '0/1') or tuples thereof,
        'DP' : depth of coverage,
        'GQ' : genotype quality}
        
        that specify eligible values for the samples genotype.

        Example filters:
        {'Sample1':'1/1'} yields all entries where Sample1's genotype is 1/1
        {'Sample1':'1/1', 'Sample2':('0/1','0/0')} yields entries where
            Sample1's genotype is 1/1 and Sample2's genotype is either 0/1 or 0/0."""
        
        if not any(self.info.sample_names):
            raise RuntimeError('filter: sample-specific information missing from the vcf input.')

        for v in self:
            try:
                for samplekey in h_filters:
                    for fieldkey in h_filters[samplekey]:
                        if not v.sampleinfo.get(fieldkey):
                            raise RuntimeError('VCF entry without "{0}" field'.format(fieldkey))
                    if 'GT' in h_filters[samplekey]:
                        if v.sampleinfo['GT'][samplekey] not in h_filters[samplekey]['GT']:
                            break
                    if 'DP' in h_filters[samplekey]:
                        if v.sampleinfo['DP'][samplekey] == '.':
                            coverage_for_sample = 0
                        else:
                            coverage_for_sample = int(v.sampleinfo['DP'][samplekey])
                        if coverage_for_sample < h_filters[samplekey]['DP']:
                            break
                    if 'GQ' in h_filters[samplekey]:
                        if v.sampleinfo['GQ'][samplekey] == '.':
                            quality_for_sample = 0
                        else:
                            quality_for_sample = int(v.sampleinfo['GQ'][samplekey])
                        if quality_for_sample < h_filters[samplekey]['GQ']:
                            break                
                else:
                    if v_filters:
                        yield v.sample_slice(v_filters)
                    else:
                        yield v
            except KeyError:
                raise RuntimeError('VCF file has no sample named "{0}".'.format(samplekey))

    def split_affected (self):
        """Iterator for splitting a vcf file into separate files for each sample.

        Returns a tuple of the same length and in the same order as the samples in the vcf file.
        In it, each element is either a VCFEntry instance representing the current line or None.
        A VCFEntry instance signifies that the corresponding sample has a non-wt genotype at the site."""

        if not any(self.info.sample_names):
            raise RuntimeError('This is not a multi-sample vcf file. Nothing to split.')
        for v in self:
            yield tuple((v if v.sampleinfo['GT'][sample] != '0/0' else None
                         for sample in self.info.sample_names))
        
    def __enter__(self):
        return self

    def __exit__(self, *error_desc):
        self.close()
        
    def seek (self, offset):
        if not self.ifo_isseekable:
            raise NotImplementedError ('Seek method is currently implemented only for real files in vcf format')
        return self.ifo.seek(self.body_start + offset)

    def close (self):
        if self.ifo is not sys.stdout:
            if hasattr(self.ifo, 'close'):
                self.ifo.close()

def open (file, mode = 'r'):
    if mode == 'r':
        return VCFReader(io.open(file, mode))
    elif mode == 'rb':
        bcf_magic_string = b'BCF'
        test = gzip.open(file)
        try:
            if test.read(3) != bcf_magic_string:
                raise RuntimeError()
        except:
            test.close()
            test = io.open(file, 'rb')
            try:
                if test.read(3) != bcf_magic_string:
                    raise RuntimeError()
            except:
                raise RuntimeError('{0} does not seem to be a bcf file.'.format(file))
        finally:
            test.close()            
        return VCFReader(pybcftools.view(file))
    else:
        raise ValueError('Unsupported value for mode: "{0}"'.format(mode))

