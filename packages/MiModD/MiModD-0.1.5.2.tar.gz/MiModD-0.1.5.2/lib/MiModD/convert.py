import sys
import os
import gzip  # to open compressed fastq files

from collections import namedtuple
from . import mimodd_base, pysamtools, samheader, pysam

# TO DO:
# customize ReHeaderSpecs to do default initialization and argument checking
ReHeaderSpecs = namedtuple('ReHeaderSpecs', ['mode', 'template', 'id_mapping'])

class ReHeader (object):
    def __init__ (self, orifile, t_default = None,
                  rg_specs = ReHeaderSpecs(None, None, {}),
                  sq_specs = ReHeaderSpecs(None, None, {}),
                  co_specs = ReHeaderSpecs(None, None, {}), 
                  rg_mapping = {}, sq_mapping = {}):

        # checks for legal argument combinations
        for spec_name, specs in (('rg_specs', rg_specs), ('sq_specs', sq_specs),
                      ('co_specs', co_specs)):
            if specs.template and not specs.mode:
                raise ValueError(
                    '{0}.template when specified requires {0}.mode'
                    .format(spec_name))
        if t_default and not any((rg_specs.mode, sq_specs.mode, co_specs.mode)):
            raise ValueError(
                't_default requires at least one of rg_specs, sq_specs, co_specs')
        if orifile == '-':
            raise ValueError(
                'Standard input is supported as source only for header templates, not for the original bam format.')

        try:
            ori_header = samheader.Header.frombam(orifile)
        except RuntimeError:
            try:
                ori_header = samheader.Header.fromsam(orifile)
            except RuntimeError:
                raise RuntimeError('Need original file in SAM/BAM format.')

        self.rg_mapping = rg_mapping
        self.sq_mapping = sq_mapping
        self.original = ori_header
        self.new = self.original.copy()
        
        if any(
            param == '-' for param in (t_default, rg_specs.template,
                                       sq_specs.template, co_specs.template)):
            try:
                stdin_hdr = samheader.Header.fromsam('-')
            except RuntimeError:
                raise RuntimeError('Need SAM format from standard input.')
            
        if t_default:
            if t_default == '-':
                hdr_new = stdin_hdr
            else:
                try:
                    hdr_new = t_default if isinstance(t_default, samheader.Header) else samheader.Header.fromsam(t_default)
                except RuntimeError:
                    raise RuntimeError('Need header template in SAM format.')
        else:
            hdr_new = samheader.Header()
        if rg_specs.template:
            if rg_specs.template == '-':
                hdr_rg = stdin_hdr
            else:
                try:
                    hdr_rg = rg_specs.template if isinstance(rg_specs.template, samheader.Header) else samheader.Header.fromsam(rg_specs.template)
                except RuntimeError:
                    raise RuntimeError('Need RG section template in SAM format.')
            hdr_new.merge_rg(hdr_rg, treat = 'replace')
        if sq_specs.template:
            if sq_specs.template == '-':
                hdr_sq = stdin_hdr
            else:
                try:
                    hdr_sq = sq_specs.template if isinstance(sq_specs.template, samheader.Header) else samheader.Header.fromsam(sq_specs.template)
                except RuntimeError:
                    raise RuntimeError('Need SQ section template in SAM format.')
            hdr_new.merge_sq(hdr_sq, treat = 'replace')
        if co_specs.template:
            if co_specs.template == '-':
                hdr_co = stdin_hdr
            else:
                try:
                    hdr_co = co_specs.template if isinstance(co_specs.template, samheader.Header) else samheader.Header.fromsam(co_specs.template)
                except RuntimeError:
                    raise RuntimeError('Need comment section template in SAM format.')
            hdr_new.merge_co(hdr_co, treat = 'replace')
        if rg_specs.mode:
            self.new.merge_rg(hdr_new, treat = rg_specs.mode, mapping = rg_specs.id_mapping)
        if sq_specs.mode:
            self.new.merge_sq(hdr_new, treat = sq_specs.mode, mapping = sq_specs.id_mapping)
        if co_specs.mode:
            self.new.merge_co(hdr_new, treat = co_specs.mode)

        # apply rg_mapping to new header
        if rg_mapping:
            # check that the mapping is valid
            current_rgids = {rg['ID'] for rg in self.new['RG']}
            for _from, _to in rg_mapping.items():
                if _from not in current_rgids:
                    raise KeyError('Could not find ID {0}'.format(_from))
                if _to in current_rgids:
                    raise ValueError(
                        'Cannot change ID {0} to ID {1}. Target ID exists already.'
                        .format(_from, _to))

            # rename rg IDs according to mapping
            self.new.change_values('RG', 'ID', rg_mapping)

        # apply sq_mapping to new header
        if sq_mapping:
            # check that the mapping only contains valid keys
            current_sqnames = {sq['SN'] for sq in self.new['SQ']}
            for _from, _to in sq_mapping.items():
                if _from not in current_sqnames:
                    raise KeyError('Could not find sequence name {0}'.format(_from))
                if _to in current_sqnames:
                    raise ValueError(
                        'Cannot change sequence name {0} to {1}. Target name exists already.'
                        .format(_from, _to))

            # rename rg IDs according to mapping
            self.new.change_values('SQ', 'SN', sq_mapping)
                    
    def needs_per_read_rg_grooming(self):
        return (not {rg['ID'] for rg in self.new['RG']}.issuperset({rg['ID'] for rg in self.original['RG']}))

    def needs_per_read_sq_grooming(self):
        return (not {sq['SN'] for sq in self.new['SQ']}.issuperset({sq['SN'] for sq in self.original['SQ']}))

    def rgids_to_groom(self):
        return {rg['ID'] for rg in self.original['RG']}.difference({rg['ID'] for rg in self.new['RG']})

    def sqids_to_groom(self):
        return {sq['SN'] for sq in self.original['SQ']}.difference({sq['SN'] for sq in self.new['SQ']})

class UnAlignedRead (pysam.AlignedRead):
    """Enables convenient initialization of an unmapped read."""
    
    def __init__ (self, mode = 'single'):
        super(UnAlignedRead, self).__init__()
        self.tid = -1
        self.pos = -1
        self.is_unmapped = True
        self.mapq = 255
        self.cigar = None
        self.tlen = 0
        self.rnext = self.pnext = -1

def new_unaligned_pair ():
    """Creates two UnAlignedRead instances and sets mate-specific flags."""
    
    r1 = UnAlignedRead()
    r2 = UnAlignedRead()
    r1.flag = r1.flag | 73  # set is_paired, is_read1 & mate_is_unmapped bits
    r2.flag = r2.flag | 137 # set is_paired, is_read2 & mate_is_unmapped bits

    return (r1, r2)

def fq2sam (filelist1, filelist2, outputname=None, inputcomp=True, outputcomp=True,
            header = None):
    """Converts fastq format (single- or paired-end) into SAM/BAM format.

    In paired-end mode, expects mate sequences to be specified in two
    separate files with identical read order.
    
    Arguments:
    mode:       'single' or 'paired' to indicate the sequencing mode
    inputfiles: a list of fastq format input files; must have a single element
                with 'single' mode and two elements with 'paired'
    outputname: the name of the SAM/BAM output file
    inputcomp:  True for gzipped fastq input
    outputcomp: True if output should be in BAM instead of SAM format
    header:     the name of an existing SAM file the header of which should be
                used as the header of the output file."""
    
    mode = 'single' if filelist2 is None else 'paired'
    
    if not outputname:
        # redirect to stdout by specifying '-' as the filename in the call to pysam.Samfile
        outputname = '-'

    # concatenate files
    # input decompression as needed
    if inputcomp:
        input1 = cat_read(filelist1, gzip.open, 'rb')
        if mode == "paired":
            input2 = cat_read(filelist2, gzip.open, 'rb')
    else:
        input1 = cat_read(filelist1, open, 'rb')
        if mode == "paired":
            input2 = cat_read(filelist2, open, 'rb')
    
    # wrap file objects into fastq.Fastq_Raw_Reader instances
    # for convenient access to fastq sequence entries as tuples
    fqr1 = fastqReader(input1)
    if mode == "paired":
        fqr2 = fastqReader(input2)


    # generate a SAM header or modify and use an existing one
    if header:
        if isinstance (header, samheader.Header):
            new_header = header
        else:
            try:
                new_header = samheader.Header.fromsam(header)
            except RuntimeError:
                raise RuntimeError('The header file must have SAM format.')
    else:
        new_header = samheader.Header()

    # add yourself to the @PG lines
    # new_header['PG'].append(
    #                {'ID':'MiModD', 'PN':'mimodd convert',
    #                 'CL': ' '.join(sys.argv),
    #                 'VN': str(mimodd_base.__version__)
    #                })
    # if no read group was specified, use default
    if not new_header['RG']:
        new_header['RG']=[{'ID':'000'}]

    # open output file and start writing
    w_mode = 'wb' if outputcomp else 'wh'
    try:
        outfile = pysam.Samfile(outputname, w_mode, header = new_header)

        if mode == "single":
            ar1 = UnAlignedRead()
            for read1 in fqr1:
                ar1.qname = read1[0][1:].split(None, 1)[0]
                ar1.seq = read1[1].strip()
                ar1.qual = read1[2].strip()
                ar1.tags = [('RG', new_header['RG'][0]['ID']), ('PG', 'MiModD')]
                outfile.write(ar1) 
        else:
            # in paired mode read from two files at a time
            ar1, ar2 = new_unaligned_pair()
            for read1, read2 in zip(fqr1, fqr2):
                ar1.qname = read1[0][1:].split(None, 1)[0]
                ar1.seq = read1[1].strip()
                ar1.qual = read1[2].strip()

                ar2.qname = read2[0][1:].split(None, 1)[0]
                ar2.seq = read2[1].strip()
                ar2.qual = read2[2].strip()

                ar1.tags = [('RG', new_header['RG'][0]['ID']), ('PG', 'MiModD')]
                ar2.tags = [('RG', new_header['RG'][0]['ID']), ('PG', 'MiModD')]

                outfile.write(ar1)
                outfile.write(ar2)
    finally:
        try:
            input1.close()
        finally:
            try:
                if mode == "paired":
                    input2.close()
            finally:
                outfile.close()

def sam2bam (infile, ofile=None, iformat='sam', oformat='bam', reheader = None):
    if reheader:
        needs_per_read_rg_grooming = reheader.needs_per_read_rg_grooming()
        needs_per_read_sq_grooming = reheader.needs_per_read_sq_grooming()
        if not needs_per_read_rg_grooming and not needs_per_read_sq_grooming:
            if iformat == oformat == 'bam':
                # a simple case of samtools-style reheadering
                call, results, errors = pysamtools.reheader(reheader.new, infile, ofile)
                if errors:
                    print(errors)
                return
                    
        r_mode = 'rb' if iformat == 'bam' else 'r'
        w_mode = 'wb' if oformat == 'bam' else 'wh'
        if not ofile:
            ofile = '-'

        with pysam.Samfile(infile, r_mode, check_sq = False) as ifo, \
             pysam.Samfile(ofile, w_mode, header = reheader.new) as ofo:
            if not needs_per_read_rg_grooming and not needs_per_read_sq_grooming:
                for read in ifo:
                    ofo.write(read)
            else:
                rgids_to_groom = reheader.rgids_to_groom()
                sqnos_to_groom = {no: sn for no, sn in enumerate(ifo.references) if sn in reheader.sqids_to_groom()}
                sqids_to_groom = {v: k for k,v in sqnos_to_groom.items()}
                for read in ifo:
                    if needs_per_read_sq_grooming and read.tid in sqnos_to_groom:
                        new_rname = reheader.sq_mapping.get(sqnos_to_groom[read.tid])
                        if new_rname is None:
                            raise RuntimeError (
                                'Cannot remove sequence "{0}" from header because it is referenced in file body. Reheader operation aborted.'
                                .format(sqnos_to_groom[read.tid]))
                        read.tid = sqids_to_groom[new_rname]
                    if needs_per_read_rg_grooming:
                        rg_infos = ((n, tag[1]) for n, tag in enumerate(read.tags) if tag[0] == 'RG'
                                         and tag[1] in rgids_to_groom)
                        for rg_info in rg_infos:
                            new_rgid = reheader.rg_mapping.get(rg_info[1])
                            if new_rgid is None:
                                raise RuntimeError (
                                    'Cannot remove read-group with ID "{0}" from header because it is referenced in file body. Reheader operation aborted.'
                                    .format(rg_info[1]))
                            tags = read.tags[:]
                            tags[rg_info[0]] = ('RG', new_rgid)
                            read.tags = tags
                    ofo.write(read)
    else:
        call, results, errors = pysamtools.view(infile, iformat, ofile, oformat)
        if errors:
            print(errors)

def convert (input1, input2 = None, iformat = 'bam', oformat = 'sam',
              outputname = None, header = None):
    supported = {'fastq':('sam', 'bam'),
                 'gz':('sam', 'bam'),
                 'sam':('sam', 'bam',),
                 'bam':('sam', 'bam')}
    if iformat not in supported:
        raise ValueError('Unknown input format {0}. Acceptable values: {1}'.
		 format(iformat, ', '.join(sorted(supported))))
    if oformat not in supported[iformat]:
        raise ValueError('Conversion from {0} to {1} is not currently supported.'.format(iformat, oformat))

    if iformat in ('fastq', 'gz'):
        kwargs={'inputcomp' : iformat == 'gz',
                'outputcomp' : oformat == 'bam',
                'header' : header}
        fq2sam (input1, input2, outputname, **kwargs)
    elif iformat in ('sam', 'bam'):
        if len(input1) > 1 or input2 is not None:
            raise ValueError('Can do SAM <-> BAM conversions only with single input files.')
        if header:
            raise ValueError('header argument is not allowed with SAM/BAM input. Use the reheader tool to change header information.')
        sam2bam(input1[0], outputname, iformat, oformat)
    else:
        raise AssertionError('Oh oh, this looks like a bug')

def reheader (inputfile, rg_specs, sq_specs, co_specs,
              template = None, outputfile = None,  
              rg_mapping = {}, sq_mapping = {}, header_only = False,
              verbose = False):
    reheader = ReHeader(inputfile, template, rg_specs = rg_specs,
                        sq_specs = sq_specs, co_specs = co_specs,
                        rg_mapping = rg_mapping, sq_mapping = sq_mapping)
    if header_only:
        if outputfile:
            with open(outputfile, 'w') as output:
                output.write(str(reheader.new)+'\n')
        else:
            print (reheader.new)
    else:
        sam2bam (inputfile, outputfile, iformat = 'bam', oformat = 'bam', reheader = reheader)
    
def fastqReader(inputFile):
    """A fast and robust fastq parser.

    Deals with multiline sequences and quality scores.
    Allows arbitrary numbers of empty lines anywhere in the file.
    Performs (only) the following file format checks while parsing:
    - each title line MUST start with @ symbol
    - each record MUST have a sequence
    - sequence and quality score of each record MUST be of equal length
    No alphabet checks are done on sequences or quality scores."""

    title_token = ord('@')
    sep_token = ord('+')
    while True:
        title = next(inputFile) # will raise StopIteration if there are no more records
        if not title[0] == title_token:
           if not title.rstrip(): continue # empty lines allowed between records
           raise AssertionError('Invalid file format: Title line not starting with @')
        title = title.rstrip()
        line_tmp = []
        try: # from here on any StopIteration means an incomplete record
            while True:
                currentLine = next(inputFile)
                # we are accepting arbitrary numbers of empty lines anywhere
                if currentLine[0] == sep_token: break
                line_tmp.append(currentLine.rstrip())
            seq = b''.join(line_tmp)
            seqlen = len(seq)
            if seqlen == 0:
                raise AssertionError('Invalid file format: Record without sequence')
            quallen = 0
            line_tmp = []
            while seqlen > quallen:
                currentLine = next(inputFile).rstrip()
                # again we are accepting any number of empty lines
                line_tmp.append(currentLine)
                quallen += len(currentLine)
        except StopIteration:
            raise AssertionError('Invalid file format: Truncated record at end of file')
        if seqlen < quallen:
            raise AssertionError('Invalid file format: Inconsistent lengths of sequence and quality score')
        qual = b''.join(line_tmp)
        yield title, seq, qual

def cat_read (filelist, open_function, mode):
    """Line-based iteration across multiple input files."""
    
    for file in filelist:
        with open_function(file, mode) as ifo:
            for line in ifo:
                yield line

def clparse_convert(**args):
    """Command line parsing to make the convert function usable from the terminal."""
    
    # split the input file list into two in case of paired-end data
    if args.get('iformat') in ('fastq_pe', 'gz_pe'):
        if len(args['input1']) < 2:
            raise ValueError('At least two input files are required with paired-end input.')
        args['input1'], args['input2'] = args['input1'][::2], args['input1'][1::2]
        args['iformat'] = args['iformat'][:-3]

    convert(**args)

def clparse_reheader(**args):
    """Command line parsing to make the reheader function usable from the terminal."""

    # split --rg, --sq and --co option values and
    # remap them to new keyword arguments
    # while filtering out 'ignore' values
    # also check for the following invalid arguments/argument combinations:
    # - any value other than the keywords ignore, replace or update
    #   following the --rg, --sq or --co
    # - template file names following an initial 'ignore' value
    specs = {}
    for argname in ('rg', 'sq', 'co'):
        if not args.get(argname):
            if args.get('template'):
                args[argname] = ['replace']
            else:
                args[argname] = ['ignore']
        mode = template = None
        id_mapping = {}
        if args[argname][0] not in ('ignore', 'replace', 'update'):
            raise ValueError ('Unknown --sq option value. Expected one of: ignore, replace, update')
        if args[argname][0] != 'ignore':
            mode = args[argname][0]
            if len(args[argname]) == 2:
                template = args[argname][1]
                specs[argname] = ReHeaderSpecs(mode, template, id_mapping)
                del args[argname]
                continue
        elif len(args[argname]) > 1:
            raise ValueError (
                'Invalid combination of --{0} ignore and {0} template file'.format(argname))
        if argname == 'co' and len(args[argname]) > 2:
            raise ValueError (
                'Unexpected arguments to --co option: {0}'
                .format(', '.join(args[argname][2:])))
        if argname in ('rg', 'sq') and len(args[argname]) > 2:
            if len(args[argname]) % 3 == 2:
                template = args[argname][1]
                id_mapping = parse_idmapping(args[argname][2:])
            else:
                id_mapping = parse_idmapping(args[argname][1:])
        specs[argname] = ReHeaderSpecs(mode, template, id_mapping)
        del args[argname]
        
    # check that there is at least one argument that can be used to modify the input file header
    if not any((args.get('template'), specs['rg'].template,
                specs['sq'].template, specs['co'].template,
                args.get('rg_mapping'), args.get('sq_mapping'))):
        raise ValueError(
            'At least one template file or a readgroup ID or sequence name mapping has to be specified along with the input file.')
    if args.get('template') and not any((specs['rg'].mode, specs['sq'].mode,
                                         specs['co'].mode)):
        raise ValueError(
            'Specifying a template file requires at least one of --rg, --sq, --co to be set to update or replace.')

    args['rg_mapping'] = parse_idmapping(args.get('rg_mapping', []))
    args['sq_mapping'] = parse_idmapping(args.get('sq_mapping', []))

    reheader(rg_specs = specs['rg'], sq_specs = specs['sq'],
             co_specs = specs['co'], **args)

def parse_idmapping (cl_idlist):
    modlen = len(cl_idlist) % 3
    if modlen:
        raise ValueError(
            'Encountered truncated list of id mappings. Incomplete mapping: "{0}"'
            .format(''.join(cl_idlist[-modlen:])))
    old_ids = cl_idlist[::3]
    seps = cl_idlist[1::3]
    new_ids = cl_idlist[2::3]
    for index, sep in enumerate(seps):
        if sep != ':':
            raise ValueError(
                'Expected "OLD_ID":"NEW_ID" mapping format. Found: "{0}{1}{2}"'
                .format(old_ids[index], sep, new_ids[index]))
    mapping = dict(zip(old_ids, new_ids))
    return mapping
