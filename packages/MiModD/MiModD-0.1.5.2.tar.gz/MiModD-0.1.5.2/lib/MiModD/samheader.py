"""An interface for working with SAM/BAM headers.

The Header class defined here serves as an object representation of a SAM/BAM
header.
The middleware generator function validate_header_lines can be used to validate
iterable text-based header sources.
The sam_header function generates and returns a Header instance from its
arguments and is called by the command line interface function run_as_main."""

import sys
import os
import datetime
from collections import OrderedDict

from . import pysamtools

class Header (dict):
    defined_tags = {
                    'HD': {'required': {('VN', )},
                           'optional': {('SO', )}},
                    'SQ': {'required': {('SN', 'LN')},
                           'optional': {('AS', 'M5', 'SP', 'UR')}},
                    'RG': {'required': {('ID', )},
                           'optional': {('CN', 'DS', 'DT', 'FO', 'KS', 'LB', 
                                         'PG', 'PI', 'PL', 'PU', 'SM')}},
                    'PG': {'required': {('ID', )},
                           'optional': {('PN', 'CL', 'PP', 'DS', 'VN')}}}
    tag_priorities = {
                    'HD': {'VN': 1, 'SO': 2},
                    'SQ': {'SN': 1, 'LN': 2, 'AS': 3, 'M5': 4, 'SP': 5, 'UR': 6},
                    'RG': {'ID': 1, 'SM': 2, 'DS': 3, 'CN': 4, 'DT': 5, 'FO': 6,
                           'KS': 7, 'LB': 8, 'PG': 9, 'PI': 10, 'PL': 11, 'PU': 12},
                    'PG': {'ID': 1, 'PN': 2, 'VN': 3, 'CL': 4, 'DS': 5, 'PP': 6}}
    
    @classmethod
    def fromfile (cls, seqfile, fileformat):
        try:
            if fileformat == 'fasta':
                return cls.fromfasta(seqfile)
            elif fileformat == 'vcf':
                return cls.fromvcf(seqfile)
            elif fileformat == 'sam':
                return cls.fromsam(seqfile)
            elif fileformat == 'bam':
                return cls.frombam(seqfile)
            else:
                raise NotImplementedError()
        except NotImplementedError:
            raise RuntimeError ('Unsupported file format for SAM header construction: {0}'
                                .format(fileformat))
    @classmethod
    def fromsam (cls, seqfile):
        return cls(pysamtools.header(seqfile, 'sam'))

    @classmethod
    def frombam (cls, seqfile):
        return cls(pysamtools.header(seqfile, 'bam'))
    
    @classmethod
    def fromfasta (cls, seqfile):
        raise NotImplementedError()
        # info_dict = get_info_from_fasta(seqfile)
        # hdr = cls.__new__()
        # hdr.merge_sq(info_dict)
        # return hdr

    @classmethod
    def fromvcf (cls, seqfile):
        raise NotImplementedError()
        # info_dict = get_info_from_vcf(seqfile)    
        # hdr = cls.__new__()
        # hdr.merge_rg(info_dict)
        # hdr.merge_sq(info_dict)
        # return hdr
    
    def __init__ (self, headerlines = []):
        dict.__init__(self)
        self['HD'] = {'VN':'1.5'}
        self['SQ']=[]
        self['RG']=[]
        self['PG']=[]
        self['CO']=[]
        
        if headerlines:
            for line in validate_header_lines(headerlines):
                line_tag, *line_content = line.split("\t")
                if line_tag == '@CO':
                    self['CO'].append('\t'.join(line_content))
                else:
                    line_fields = [field.split(':', 1) for field in line_content]
                    if line_tag == '@HD':
                        self['HD'] = {tag:value for tag, value in line_fields}
                    elif line_tag == '@SQ':
                        self['SQ'].append(dict((tag, int(value)) if tag == 'LN' else (tag, value) for tag, value in line_fields))
                    elif line_tag == '@RG':
                        self['RG'].append({tag:value for tag, value in line_fields})
                    elif line_tag == '@PG':
                        self['PG'].append({tag:value for tag, value in line_fields})
                    else:
                        # we don't know the record type, but samtools did not complain, so we accept it
                        self.setdefault(line_tag[1:], []).append(OrderedDict((tag, value) for tag, value in line_fields))
        
    def merge_rg (self, other, treat = 'update', mapping = {}):
        # check for valid mapping
        selfids = {rg['ID'] for rg in self['RG']}
        otherids = {rg['ID'] for rg in other['RG']}
        for _from, _to in mapping.items():
            if _from not in selfids:
                raise KeyError (
                    'ID {0} not found in original header'.format(_from))
            if _to not in otherids:
                raise ValueError (
                    'ID {0} not found in modifying header'.format(_to))
        
        otherids = {rg['ID']: index for index, rg in enumerate(other['RG'])}
        new_rgs = []

        for rg in self['RG']:
            newid = mapping.get(rg['ID']) or (rg['ID'] if rg['ID'] in otherids else None)
            if newid is None:
                if treat == 'update':
                    new_rgs.append(rg)
            else:
                if treat == 'update':
                    new_rg = {k: v for k, v in rg.items()}
                    new_rg.update(other['RG'][otherids[newid]])
                    new_rg['ID'] = rg['ID']
                    new_rgs.append(new_rg)
                elif treat == 'replace':
                    new_rg = {k: v for k, v in other['RG'][otherids[newid]].items()}
                    new_rg['ID'] = rg['ID']
                    new_rgs.append(new_rg)
        treated_ids = {rg['ID'] for rg in new_rgs} | {rgid for rgid in mapping.values()}
        self['RG'] = new_rgs + \
                     [rg for rg in other['RG'] if rg['ID'] not in treated_ids]

    def merge_sq (self, other, treat = 'update', mapping = {}):
        # check for valid mapping
        selfsns = {sq['SN'] for sq in self['SQ']}
        othersns = {sq['SN'] for sq in other['SQ']}
        for _from, _to in mapping.items():
            if _from not in selfsns:
                raise KeyError (
                    'Sequence name {0} not found in original header'
                    .format(_from))
            if _to not in othersns:
                raise ValueError (
                    'Sequence name {0} not found in modifying header'
                    .format(_to))
        
        othersqs = {sq['SN']: index for index, sq in enumerate(other['SQ'])}
        new_sqs = []

        for sq in self['SQ']:
            newsn = mapping.get(sq['SN']) or (sq['SN'] if sq['SN'] in othersqs else None)
            if newsn is None:
                if treat == 'update':
                    new_sqs.append(sq)
            else:
                if treat == 'update':
                    # MD5 sum information and length are never updated
                    new_sq = {k: v for k, v in sq.items()}
                    for k, v in other['SQ'][othersqs[newsn]].items():
                        if k not in ('SN', 'M5', 'LN'):
                            new_sq[k] = v
                    new_sqs.append(new_sq)
                elif treat == 'replace':
                    new_sq = {k: v for k, v in other['SQ'][othersqs[newsn]].items()}
                    new_sq['SN'] = sq['SN']
                    new_sqs.append(new_sq)
        treated_sns = {sq['SN'] for sq in new_sqs} | {sn for sn in mapping.values()}
        self['SQ'] = new_sqs + \
                     [sq for sq in other['SQ'] if sq['SN'] not in treated_sns]

    def merge_co (self, other, treat = 'update'):
        if treat == 'update':
            self['CO'] += other['CO']
        elif treat == 'replace':
            self['CO'] = other['CO']
        else:
            raise ValueError('Unexpected value for treat_rg')

    def change_values (self, record_type, tag, name_mapping):
        """Change the values of the specified tag in the given record type
        according to name_mapping."""
        
        changes_to_make = len(name_mapping)
        for record in self[record_type]:
            if changes_to_make == 0:
                break
            try:
                if record[tag] in name_mapping:
                    record[tag] = name_mapping[record[tag]]
                    changes_to_make -= 1
            except KeyError:
                # not all tags have to be present in all records
                pass
    
    def uniquify_sm (self):
        """Ensure unique sample names in the header.

        Attaches the RG ID to each RG SM entry to avoid sample name collisions
        between read groups."""

        for rg in self['RG']:
            # change all SM entries to <old_sm>_RG<rg_id>
            rg['SM'] = '{0}_RG{1}'.format(rg['SM'],rg['ID'])

    def lines (self):
        yield '@HD\t' + '\t'.join((':'.join((tag, value)) for tag, value in sorted(self['HD'].items(), key = lambda item: self.tag_priorities['HD'][item[0]])))
        for rg in self['RG']:
            yield '@RG\t' + '\t'.join((':'.join((tag, value)) for tag, value in sorted(rg.items(), key = lambda item: self.tag_priorities['RG'][item[0]])))
        for sq in self['SQ']:
            yield '@SQ\t' + '\t'.join((':'.join((tag, str(value))) for tag, value in sorted(sq.items(), key = lambda item: self.tag_priorities['SQ'][item[0]])))
        for pg in self['PG']:
            yield '@PG\t' + '\t'.join((':'.join((tag, value)) for tag, value in sorted(pg.items(), key = lambda item: self.tag_priorities['PG'][item[0]])))
        std_hdr = Header()
        for unknown_record_type in (record_type for record_type in self if record_type not in std_hdr):
            for record in self[unknown_record_type]:
                yield '@' + unknown_record_type + '\t' + '\t'.join((':'.join((tag, value)) for tag, value in record.items()))
        for co in self['CO']:
            yield '@CO\t' + co
    
    def validate (self):
        _ = [_ for _ in validate_header_lines(self.lines())]
        
    def __str__ (self):
        ret = '\n'.join(self.lines())
        return ret

    def copy (self):
        return Header(self.lines())
    
def validate_header_lines (hlines):
    ids_seen = { '@RG': set(),
                 '@PG': set(),
                 '@SQ': set() }
    for line_no, line in enumerate(hlines, 1):
        include_line = True
        line_tag, *line_content = line.split("\t")
        
        if not (line_tag.startswith('@') and len(line_tag) == 3 and line_tag[1:].isalpha()):
            raise RuntimeError('Invalid record type: "{0}" at line {1}.\nExpected format: @XY separated from rest of line by TAB.'.format(line_tag, line_no))
        if line_tag != '@CO':
            if line_tag == '@HD' and line_no > 1:
                raise RuntimeError('"@HD" tag found at line {0}, but allowed only on first line.'.format(line_no)) 
            line_fields = [field.split(':', 1) for field in line_content]
            if any(len(field) == 1 for field in line_fields):
                raise RuntimeError('Invalid "{0}" record at line {1}. Expected line to consist of tab-separated TAG:VALUE pairs.'.format(line_tag, line_no))
            if line_tag in Header.defined_tags:
                tags = {field[0] for field in line_fields}
                if not tags.issuperset(Header.defined_tags[line_tag]['required']):
                    raise RuntimeError('Required tag(s) {0} missing from "{1}" record type at line {2}.'.format(Header.defined_tags[line_tag]['required'] - tags, line_tag, line_no))
                if not tags.issubset(Header.defined_tags[line_tag]['required'] | Header.defined_tags[line_tag]['optional']):
                    raise RuntimeError('Unknown tag(s) {0} found for standard record type "{1}" at line {2}.'.format(tags - (Header.defined_tags[line_tag]['required'] | Header.defined_tags[line_tag]['optional']), line_tag, line_no)) 
            for tag, value in line_fields:
                if not (len(tag) == 2 and tag[0].isalpha() and tag[1].isalnum()):
                    raise RuntimeError('Invalid header tag "{0}" at line {1}.\nExpected two-letter tag of format [A-Za-z][A-Za-z0-9] separated from value by ":".'.format(tag, line_no))
                if not value:
                    if line_tag == '@SQ' and tag == 'SN':
                        # ensure backwards compatibility
                        # MiModD versions < 0.1.4 used "@SQ\tSN:\tLN:0"
                        # in the absence of other @SQ record lines
                        # skip such placeholder lines when constructing
                        # headers in MiModD versions > 0.1.4
                        include_line = False
                        break
                    raise RuntimeError('Missing value for header tag "{0}" at line {1}.'.format(tag, line_no))
                if any(not(32 <= ord(c) <= 126) for c in value):
                    raise RuntimeError('Invalid header value "{0}" at line {1}.\nOnly characters wih ASCII codes between 32 and 126 [ -~] are allowed.'.format(value, line_no))
                if (line_tag in ('@RG', '@PG') and tag == 'ID') or (line_tag == 'SQ' and tag == 'SN'):
                    if value in ids_seen[line_tag]:
                        raise RuntimeError('"{0}" field of record type "{1}" must specify a unique identifier, but found second occurence of "{0}:{2}" at line {3}.'.format(tag, line_tag, value, line_no))
                    ids_seen[line_tag].add(value)
        if include_line:
            yield line

def sam_header(rg_id, comments = [], optional_sm = False, **optionals):
    """Generates a Header instance from its arguments.

    All arguments must be iterables.
    For the optional argument comments, each element in the iterable
    is translated into a separate @CO header line.
    To support header generation for multi-sample sam files,
    the remaining iterables must yield an equal number n of elements
    (but possibly containing None as placeholder),
    which are used to generate n @RG lines, where the ith line is generated
    from the ith elements of all iterables.
		
    Required arguments:
    rg_id: list of read-group IDs
    rg_sm: list of read-group samples, use pool names where a pool is being sequenced

    Optional arguments:
    rg_cn: list of names of sequencing centers
    rg_ds: list of read-group descriptions
    rg_dt: list of dates the runs were produced
    rg_lb: list of read-group libraries
    rg_pl: list of platforms/technologies used to produce the reads
    rg_pi: list of predicted median insert sizes
    rg_pu: list of platform units; unique identifiers
    comments: list of one-line text comments."""

    optional_tags = {'rg_sm':'SM',
                     'rg_cn':'CN',
                     'rg_ds':'DS',
                     'rg_dt':'DT',
                     'rg_lb':'LB',
                     'rg_pi':'PI',
                     'rg_pl':'PL',
                     'rg_pu':'PU'
                     }
                     
    # argument validation: 
    # - there have to be as many sample names as read groups
    # - no empty elements are allowed in the list of read groups or sample names
    # - there cannot be more elements in any optional tag list than there are read groups

    rg_no = len(rg_id)
    if not all(rg_id):
        raise ValueError('No empty value allowed in rg_id.')
    if not optional_sm:
        if not optionals.get('rg_sm'):
            if rg_id:
                raise ValueError ('Sample names are required by default along with RG IDs, but none are provided.')
        elif not all(optionals['rg_sm']):
            raise ValueError('No empty value allowed in rg_sm.')
    
    for arg in optionals:
        if len(optionals[arg]) != rg_no:
            raise ValueError (
                'Number of elements passed in "{0}" argument does not match the number of read groups.'
                .format(arg))

        if optional_tags[arg] == 'DT':
            # we need an extra format check for the DT tag because
            # the Header class does not currently check it
            try:
                for dstring in optionals[arg]:
                    if dstring is not None:
                        d = datetime.datetime.strptime(dstring, "%Y-%m-%d")
            except ValueError:
                raise RuntimeError('Bad date format "{0}". Expected YYYY-MM-DD'.format(dstring))

    header = Header()
    header['RG'] = [{'ID': i} for i in rg_id]
    for no, rg in enumerate(header['RG']):
        for arg in optionals:
            value = optionals[arg][no]
            if value is not None:
                rg[optional_tags[arg]] = optionals[arg][no]
                           
    if comments:
        header['CO'] = [i.rstrip() for i in comments]
        
    # validate the Header instance before returning it
    header.validate()
    return header

def cat (infiles, outfile, oformat):
    """Wrapper around pysamtools.cat with additional header management."""
    
    if len(infiles) > 1:
        new_header = Header.frombam(infiles[0])
        for no, hdr in enumerate(Header.frombam(file) for file in infiles[1:]):
            new_header.merge_rg(hdr)
            new_header.merge_sq(hdr)

        headerfile = os.path.join(os.path.dirname(infiles[0]), 'tmph.sam')
        try:
            with open(headerfile, 'w') as ofo:
                ofo.write(str(new_header))
    
            return pysamtools.cat(infiles, outfile, oformat, headerfile)
        finally:
            try:
                os.remove(headerfile)
            except:
                pass
    else:
        return pysamtools.cat(infiles, outfile, oformat)

def run_as_main(**args):
    """Wrapper around sam_header for scripting.

    Uses clparse to parse command line arguments.
    Writes the header object returned by sam_header to disk or prints it."""
    
    call_args = args.copy()
    if 'outputfile' in call_args:
        del call_args['outputfile']

    header = sam_header (**call_args)

    if 'outputfile' in args:
        with open(args['outputfile'], 'w') as output:
            output.write(str(header)+'\n')
    else:
        print (header)
