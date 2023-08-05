"""Facilitates the use of the SNAP aligner.

The module's core function is snap_call, which provides an enhanced
interface to SNAP correcting many of the shortcomings of the current version
(0.15) of SNAP.
snap_batch provides a user-friendly way to run several SNAP jobs
and to merge the results into a single output file organized in several read
groups. This function is used by the GALAXY interface of MiModD.
"""

import sys, os
import shlex
import signal
import shutil
import subprocess
import argparse
import gzip
import platform

from collections import Counter

from . import config, mimodd_base, pysamtools, samheader, pysam, tmpfiles
from .decox import parachute, FuncInfo
from .fasta import FastaReader

tempfile_dir = config.tmpfiles_path
snap_exe = config.snap_exe

# raise an error on SIGTERM throughout this module
signal.signal(signal.SIGTERM, mimodd_base.catch_sigterm)

def snap_call (mode, refgenome_or_indexdir, inputfiles, iformat = 'fastq', oformat = 'sam', verbose = False, quiet = True, **other_options):
    """Functional interface to the SNAP aligner.

    Bundles calls to snap index and the SNAP aligner in one function call.
    Extends the useful input file spectrum of SNAP by decompressing gzipped
    fastq files and converting BAM to SAM files before calling the aligner.
    Removes the .sam file extension restriction of SNAP on SAM format input.
    Ensures the correct use of input header information and proper RG tags
    in aligned reads.
    Enables exclusion of overlapping mate pairs in paired-end mode.
    Extends SNAP's output file spectrum to include BAM.

    Arguments:
    mode: 'single' or 'paired'; used to specify the aligner call
    refgenome_or_indexdir: if a directory, it is used as the index-dir argument
                           in the underlying call to snap
                           if a filename, it is used in a call to snap index to
                           generate the index-dir at the location specified by
                           idx_out
    inputfiles: an iterable of input files; used as the inputfile(s) argument
                in the underlying call to snap
    outputfile: output destination
    iformat: 'fastq', 'sam' or 'bam' to specify the format of the input files;
             care is taken of format conversion and calling snap correctly
    oformat: 'sam' or 'bam' to specify the output format;
             the function takes care of format conversion
    idx_out: specifies the location for the index directory;
             used as the output-dir argument in an underlying call to
             snap index; default: config.tmpfiles_path/outfileprefix+'_index'
    idx_seedsize: the -s parameter for snap index
    idx_slack: the -h parameter for snap index
    idx_ofactor: the -O parameter for snap index
    """
    
    # snap_call_argcheck does basic argument validation and returns a flattened dictionary of all arguments for convenience
    args = snap_call_argcheck(FuncInfo(func = snap_call, innerscope = True), locals())
        
    # --------------------- OS X 10.10 Yosemite --------------------
    #   emergency action until bug-fix for SNAP becomes available
    #
    # SNAP produces corrupt multi-threaded output under Yosemite
    # => run it with single thread (slow, but stable)
    
    platform_description = platform.uname()
    if platform_description[0] == 'Darwin' and platform_description[2].split('.')[0] == '14':
        # kernel version 14.x.x indicates Yosemite
        args['threads'] = 1
    # --------------------------------------------------------------
    
    # read defaults from config.py
    if 'threads' not in args:
        args['threads'] = config.multithreading_level
    input_header = args['header']
    # if the rg does not specify a sample name, reuse the ID
    # the previous call of snap_call_argcheck makes sure that
    # there is only one rg entry in the header
    if not 'SM' in input_header['RG'][0]:
        input_header['RG'][0]['SM'] = input_header['RG'][0]['ID']

    # args['outputfile'] specifies where snap output should go
    outfileprefix = os.path.basename(args['outputfile']).split('.')[0] # the outputfile's name without extension

    snap_output, sorted_output = tmpfiles.unique_tmpfile_name(outfileprefix, '.tmp'), args['outputfile']
    amended_output = snap_output+'_unsorted' if args.get('sort') is not None else sorted_output
    args['outputfile'] = snap_output # currently this is needed to generate correct snap call

    # PREPARE SNAP SUBPROCESS CALL

    # if the sort option was specified, determine whether it was accompanied by
    # a memory indication. If not use default from config.py
    if 'sort' in args:
        args['sort'] = args['sort'] or config.max_memory
    # set default value for --spacing in paired-end mode
    if mode == 'paired' and 'spacing' not in args:
        args['spacing'] = [100, 10000]
        
    option_table = {'outputfile':'-o',
                    'maxseeds':'-n',
                    'maxhits':'-h',
                    'maxdist':'-d',
                    'confdiff':'-c',
                    'confadapt':'-a',
                    'selectivity':'-S',
                    'filter_output':'-F',
                    'threads':'-t',
                    'gap_penalty':'-G'
                    }
    sticky_table = {'clipping':'-C'}
    bool_table = {'mmatch_notation':'-M',
                  'error_rep':'-e',
                  'no_prefetch':'-P',
                  'bind_threads':'-b',
                  'explore':'-x',
                  'stop_on_first':'-f',
                  'ignore': '-I'
                  }
    iter_table = {'spacing':'-s'}
    
    snap_args = []
    for option in option_table:
        if args.get(option):
            snap_args += [option_table[option], str(args[option])]
    for option in sticky_table:
        if args.get(option):
            snap_args.append(''.join([sticky_table[option],str(args[option])]))
    for option in bool_table:
        if args.get(option):
            snap_args.append(bool_table[option])
    for option in iter_table:
        if args.get(option):
            snap_args.append(iter_table[option])
            snap_args += [str(v) for v in args[option]]
            
    # this list keeps track whether any input file is a temporary file that needs to be removed before finishing
    inputfiles_remove = [False for file in inputfiles]

    # starting IO, make sure we clean up
    try:
        try:
            # EXTENSION OF SNAP INPUT FILE SPECTRUM
            # decompress .gz
            if verbose:
                print ('Preparing input files for alignment ..')
            if args.get("iformat") == "gz":
                for n, file in enumerate(inputfiles):
                    inputfiles[n] = tmpfiles.unique_tmpfile_name(outfileprefix, '.fastq')
                    inputfiles_remove[n] = True
                    with gzip.open(file, 'rb') as comp_data:
                        with open(inputfiles[n], 'wb') as uncomp_data:
                            shutil.copyfileobj(comp_data, uncomp_data)
                    if verbose:
                        print ('Decompressed input file {0} to {1}.'.format(file, inputfiles[n]))
            # convert BAM to SAM
            elif args.get('iformat') == 'bam':
                comp_file = inputfiles[0]
                inputfiles[0] = tmpfiles.unique_tmpfile_name(outfileprefix, '.sam')
                inputfiles_remove[0] = True
                pysamtools.view(comp_file, 'bam', inputfiles[0], 'sam')
                if verbose:
                    print ('Decompressed input file {0} to {1}.'.format(comp_file, inputfiles[0]))
            elif args.get("iformat") == "sam" and (inputfiles[0].split('.')[-1] != 'sam'):
                # .sam hard link for SAM files with wrong extension
                # SNAP relies on the .sam suffix to use sam files,
                # but we fool it with a hard link
                # SNAP cannot use symbolic links, so if no hard link
                # can be generated, we have to go for a copy of the file
                hard_link = tmpfiles.tmp_hardlink(inputfiles[0], outfileprefix, '.sam', fallback = 'copy')
                if verbose:
                    print ('Generated hard link {0} for input file {1}.'.format(hard_link, inputfiles[0]))
                inputfiles[0] = hard_link
                inputfiles_remove[0] = True
            if verbose:
                print ()

            # CALLING SNAP
            if os.path.isdir(refgenome_or_indexdir):
                ref_index = refgenome_or_indexdir
                idx_remove = False
            else:
                # build the call to snap index
                if args.get('idx_out'):
                    ref_index = args['idx_out']
                    idx_remove = False
                else:
                    ref_index = os.path.join(tempfile_dir, outfileprefix + '_index')
                    idx_remove = True
                call, results, errors = snap_index(
                                            refgenome_or_indexdir, ref_index,
                                            args.get('idx_seedsize'), args.get('idx_slack'),
                                            args.get('idx_ofactor'), args.get('threads'),
                                            verbose = verbose, quiet = quiet)
            # get the md5sums of all sequences just indexed
            with open(os.path.join(ref_index, 'md5sums'), 'r') as ifo:
                md5dict = {seqtitle: md5 for seqtitle, md5 in (line.strip().split('\t') for line in ifo)}
            # build the call to snap single|paired
            snap_align = [snap_exe, mode, ref_index] + inputfiles + snap_args
            # aligning
            if verbose:
                print ("Calling SNAP with:")
                print (' '.join(snap_align))
                print ()

            results, errors = (s.decode() for s in subprocess.Popen(snap_align, bufsize = -1, stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate())
            if not quiet:
                print (results)
            if errors:
                raise RuntimeError (
                    'The following error message was raised by SNAP:\n{0}\n{1}'.format(
                        errors, 'Check if the input is really paired-end and sorted by read names (not coordinates)' if 'Unmatched read IDs' in errors else ''))
        finally: # alignment done, remove flagged index and input files
            try:
                if idx_remove: 
                    shutil.rmtree(ref_index) # remove the whole index directory
            except UnboundLocalError:
                # error occurred before idx_remove was set, i.e. also before indexing
                pass
            finally:
                for file, flag in zip(inputfiles, inputfiles_remove): # remove any temporary input files
                    if flag:
                        try:
                            os.remove(file)
                        except:
                            pass
                        
        # OUTPUT POSTPROCESSING
        # this section takes care of:
        # i)   reheadering the original SNAP output making sure that RG and other
        #      information is preserved from the input
        # ii)  retagging of all reads to correct their read group information
        # iii) filtering out overlapping mate pairs (if allow_mate_overlap is set to False)
        # iv)  optional BAM format output
        # v)   optional sorted output                

        if verbose:
            print ('Postprocessing alignment ..')
            print ()
        if args.get('oformat') == 'bam':
            write_mode = 'wb'
        else:
            write_mode = 'wh'

        # generate the new header object
        snap_header = samheader.Header.fromsam(snap_output)
        header = input_header                     # mostly revert the header to what it was in the input file
        header['SQ'] = snap_header['SQ']          # SNAP gets the sequences right,
        for sq in header['SQ']:                   # but we want to add MD5 tags to them
            sq['M5'] = md5dict[sq['SN']]
        # modify and add SNAP's PG header line
        for pg in snap_header['PG']:
            if pg['ID'] == 'SNAP':
                pg['PN'] = 'MiModD snap'
                pg['VN'] = str(mimodd_base.__version__)
        header['PG'].extend(snap_header['PG'])
            
        rg_id = header['RG'][0]['ID'] # we need the RG ID value to write it to each read's tag list below

        # rewrite the data with new header information
        # filtering out overlapping mate pairs and
        # correcting read group information for each read
        with pysam.Samfile(snap_output, "r") as tmp_data:
            with pysam.Samfile(amended_output, write_mode, header = header) as out_final:
                if mode == 'paired':
                    tmp_data = purge_overlapping(tmp_data, args['max_mate_overlap'])
                for read in tmp_data:
                    read.tags = [e if e[0]!='RG' else ('RG', rg_id) for e in read.tags]
                    out_final.write(read)
        # optional coordinate sorting 
        if args.get('sort'):
            pysamtools.sort(amended_output, sorted_output, args.get('oformat'), args['sort'])
            
    finally: # we are done, now remove all temporary files
        try:
            os.remove(snap_output)   # remove the intermediate sam output
        except:
            pass
        if args.get('sort') is not None:
            # with sorting the final output is in sorted_output
            # so we need to get rid of the amended_output file
            try:
                os.remove(amended_output)
            except:
                pass

def purge_overlapping (ifo, max_mate_overlap):
    """Yield only non-overlapping mate pairs from pair-sorted SAM iterable.
    
    Used by snap_call (with allow_mate_overlap=False) to purify the original
    SNAP output from read pairs that provide duplicate information.
    """

    fraction = 1-max_mate_overlap
    for r1 in ifo:
        while True:
            r2 = next(ifo)
            if r1.qname == r2.qname:
                if not r1.flag & 2:
                    yield r1
                    yield r2
                else:
                    max_alen = max(r1.alen, r2.alen)
                    if fraction*(r1.alen+r2.alen-max_alen)+max_alen <= abs(r1.tlen):
                        yield r1
                        yield r2
                break
            if r1.flag & 2:
                raise RuntimeError ('{0} and\n{1}\nnot sorted by read pairs'.format(r1,r2))
            yield r1
            r1 = r2


@parachute
def snap_call_argcheck(**args):
    """Checks if an argument dictionary is safe to use in a call to snap_call.

    The parachute wrapper does basic argument validation and returns
    a flattened dictionary of all arguments for convenience.
    The function itself performs further sanity checks on the arguments.
    If no errors are found, the verified args dictionary gets
    returned to the caller."""
    
    allowed_params = {'mode': ('single', 'paired'),
                      'input_formats': ("fastq", "gz", "sam",  "bam"),
                      'output_formats': ("sam", "bam"),
                      'clipping': ("-+", "+-", "++", "--", None),
                      'out_filter': ('a', 's', 'u', None)
                      }
        
    ref = args.get('refgenome_or_indexdir')
    if not ref:
        raise TypeError('A reference genome or index directory is required.')
    if not os.path.exists(ref):
        raise TypeError('Invalid reference genome or index directory: {0} does not exist.'.format(ref))
    if os.path.isdir(ref) and any((args.get('idx_seedsize'), args.get('idx_slack'), args.get('idx_out'))):
        raise TypeError('Indexing parameters cannot be used with existing index directory.')
    if not args.get('outputfile'):
        raise TypeError('An output file needs to be specified.')
    if args['iformat'] not in allowed_params['input_formats']:
        raise ValueError("Invalid input format; allowed values are: {}".format(', '.join(allowed_params['input_formats'])))
    if args['oformat'] not in allowed_params['output_formats']:
        raise ValueError("Invalid output format; allowed values are: {}".format(', '.join(allowed_params['output_formats'])))
    if args['mode'] not in allowed_params['mode']:
        raise ValueError("Parameter 'mode' was set to an invalid value. Choose one of the following values: 'single' for single-end or 'paired' for paired-end mode.")
    if args['mode'] == 'paired' and len(args['inputfiles'])>2:
        raise ValueError("Maximally 2 inputfiles are allowed in paired-end mode")
    if args['mode'] == 'single' and len(args['inputfiles'])>1:
        raise TypeError("Only 1 inputfile is allowed in single-end mode")
    if args['mode'] == 'single' and 'spacing' in args:
        raise TypeError("Parameter -s / --spacing is only allowed in paired-end mode")
    for file in args['inputfiles']:
        if not os.path.exists(file):
            raise TypeError('Invalid input file: {0} does not exist.'.format(file))
    if args.get('clipping') not in allowed_params['clipping']:
        raise ValueError("Parameter 'clipping' was set to an invalid value; allowed values are: '-+' (back only), '+-' (front only), '++' (back and front) or '--' (no clipping).")
    if args.get('out_filter') not in allowed_params['out_filter']:
        raise ValueError("Parameter 'out_filter' was set to an invalid value. Choose one of the valid values: 'a' (aligned ones), 's' (single aligned ones), 'u' (unaligned ones) or 'off' (no filtering), or leave out the parameter to use default value 'False'")
    if args.get('selectivity') is not None and args.get('selectivity') < 2:
        del args['selectivity']
    if not args.get('max_mate_overlap'):
        args['max_mate_overlap'] = 0
    else:
        if not 0 <= args['max_mate_overlap'] <= 1:
            raise ValueError("Paramter 'max_mate_overlap' must be a fraction between 0 and 1")
    # validate input headers and
    # make sure each job has its header as a Header instance in args['header']
    header = {}
    if args['iformat'] in ('sam', 'bam'):
        try:
            header = samheader.Header.fromfile(args['inputfiles'][0], args.get('iformat'))
        except RuntimeError:
            # this causes misleading errors with wrong iformat and
            # other general failures => improve !!
            pass
        if len(header.get('RG', [])) > 1:
            raise RuntimeError('Multiple read groups declared in input file {0}. Such input is not currently supported.'
                               .format(args['inputfiles'][0]))
    if args.get('header'):
        custom_header = args['header']
        if not isinstance (custom_header, samheader.Header):
            try:
                custom_header = samheader.Header.fromsam(custom_header)
            except RuntimeError:
                raise ValueError('Unable to get header information from custom header argument for file {0}.'
                                 .format(args['inputfiles'][0]))
        if len(custom_header['RG']) != 1:
            raise ValueError('The header specified by the custom header argument must contain exactly one read group; {0} found.'
                             .format(len(custom_header['RG'])))
        args['header'] = header or samheader.Header()
        args['header'].merge_rg(custom_header, 'replace')
    else:
        if not header:
            if args['iformat'] in ('sam', 'bam'):
                raise ValueError('Could not get header information from input file {0}.\nYou may want to provide a separate header through the custom header parameter.'
                                 .format(args['inputfiles'][0]))
            else:
                raise ValueError('Missing header information for input file {0}. {1} files require custom header information.'
                                 .format(args['inputfiles'][0], args['iformat']))
        if len(header['RG']) == 0:
            raise ValueError('Could not find read group information in the header of the input file {0}.\nYou may want to provide a separate header through the custom header parameter.'
                             .format(args['inputfiles'][0]))
        args['header'] = header
    
    return args

def snap_batch (job_arglist):
    """Run several snap alignment jobs and merge the results into a single SAM/BAM file.

    Takes a list of snap_call argument dictionaries (as generated, e.g.,
    by make_snap_argdictlist) and acts as a wrapper around the corresponding
    calls to snap_call, essentially treating the individual results files as
    temporary data to be merged into a single SAM/BAM file.
    Note: in the current version, the first argument dictionary in the list
    determines sorting, format (SAM or BAM) and name of the merged file."""

    # first job's parameters determine whether the final output should be
    # sorted, the output file name and the output format
    if 'sort' in job_arglist[0]:
        this_batch_sort = True
        sort_memory = job_arglist[0]['sort'] or config.max_memory
    else:
        this_batch_sort = False
    this_batch_output = job_arglist[0]['outputfile']
    this_batch_oformat = job_arglist[0]['oformat']

    # get and secure (by creating an empty base file) a unique file prefix for this entire batch
    unique_output_prefix = tmpfiles.unique_tmpfile_name('batch_'+os.path.basename(this_batch_output).split('.')[0])
    with open(unique_output_prefix, 'w'):
        pass
            
    tmp_files = []
    refgenomes = Counter()
    
    # determine the indexing actions required by the different jobs
    for job_args in job_arglist:
        if not os.path.isdir(job_args['refgenome_or_indexdir']):
            idx_settings = (job_args['refgenome_or_indexdir'], job_args.get('idx_out'), job_args.get('idx_seedsize'), job_args.get('idx_slack'))
            refgenomes[(idx_settings[0], idx_settings[1] or '_'.join((unique_output_prefix, os.path.basename(idx_settings[0]).split('.')[0], str(idx_settings[2] or 0), str(idx_settings[3] or 0))),
                        idx_settings[2], idx_settings[3], False if idx_settings[1] else True)] += 1

    try:
        for job_no, job_args in enumerate(job_arglist, 1):
            # overwrite some parameters in the argument dictionary
            if 'sort' in job_args:
                del job_args['sort']
            job_args['oformat'] = 'bam'
            job_args['outputfile'] = os.path.join(tempfile_dir, unique_output_prefix + str(job_no)) # create a temporary output file for each job
            # index reference genomes only if necessary
            if not os.path.isdir(job_args['refgenome_or_indexdir']):
                idx_settings = (job_args['refgenome_or_indexdir'], job_args.get('idx_out'), job_args.get('idx_seedsize'), job_args.get('idx_slack'))
                idx_key = (idx_settings[0], idx_settings[1] or '_'.join((unique_output_prefix, os.path.basename(idx_settings[0]).split('.')[0], str(idx_settings[2] or 0), str(idx_settings[3] or 0))),
                           idx_settings[2], idx_settings[3], False if idx_settings[1] else True)
                if not os.path.exists(idx_key[1]):
                    call, results, errors = snap_index(*idx_key[:-1], ofactor = job_args.get('idx_ofactor'), threads = job_args.get('threads'), verbose = job_args["verbose"], quiet = job_args["quiet"])
                refgenomes[idx_key] -= 1
                job_args['refgenome_or_indexdir'] = idx_key[1]
                for param in ('idx_out', 'idx_seedsize', 'idx_slack', 'idx_ofactor'):
                    if param in job_args:
                        del job_args[param]
            # keep track of temporary files generated
            tmp_files.append(job_args['outputfile'])
            # do the alignment for this job
            snap_call(**job_args)
            # remove index directories that are not used anymore
            if idx_key[4] and refgenomes[idx_key] == 0:
                shutil.rmtree(idx_key[1])
    
    # combining individual temporary files to one output file
        if this_batch_sort:
            if len(tmp_files) > 1:
                tmpcatfile = os.path.join(tempfile_dir, unique_output_prefix+'_unsorted')
                samheader.cat(tmp_files, tmpcatfile, 'bam')
                for file in tmp_files:
                    try:
                        os.remove(file)
                    except:
                        pass                
            else:
                tmpcatfile = tmp_files[0]
            pysamtools.sort(tmpcatfile, this_batch_output, this_batch_oformat, sort_memory)
        else:
            samheader.cat(tmp_files, this_batch_output, this_batch_oformat)

    finally:
        # make sure temporary index directories are always removed
        for idx_key in refgenomes:
            if idx_key[4]:
                try:
                    shutil.rmtree(idx_key[1])
                except:
                    pass

        #deleting temporary files
        for file in tmp_files:
            try:
                os.remove(file)
            except:
                pass
        try:
            os.remove(tmpcatfile)
        except:
            pass
        try:
            os.remove(unique_output_prefix) # remove the base file we generated as a lock for the temporary file names of this batch
        except:
            pass

def make_snap_argdictlist (commands=None, ifile=None):
    """Populate snap_call() argument dictionaries from command lines.

    Takes an iterator over command line calls to snap_call and parses the
    arguments into a list of verified argument dictionaries, each of which
    can be used in a simple snap_call(**argdict) function call. The list can
    be used as the argument to snap_batch.
    Uses clparse and snap_call_argcheck for parsing and verifying that the
    argument dictionaries are safe to use with snap_call."""
    
    job_arglist = []
    try:
        if not commands:
            if not ifile:
                raise ValueError(
                    'Either the commands or the ifile argument MUST be specified.')
            commands = (line for line in open(ifile) if line.strip())
        for line_no, command in enumerate(commands, 1):
            try:
                # here we transform the command line to function call parameters, validate these parameters and map them to snap_caller arguments !!
                args = clparse(shlex.split(command)[1:])
                job_arglist.append(snap_call_argcheck(FuncInfo(func=snap_call, innerscope = False), **args))
            except SystemExit:
                break    # somewhat complicated construct to reduce traceback
        else:
            # check all headers for compatibility
            # currently, the only requirement is that if a read group is
            # found more than once, its associated sample names have to match
            all_headers = [job['header'] for job in job_arglist]
            rg_sm_mapping = {}
            for hdr in all_headers:
                for rg in hdr['RG']:
                    if rg['ID'] in rg_sm_mapping:
                         if rg_sm_mapping[rg['ID']] != rg['SM']:
                             raise RuntimeError('The input files declare the read group {0} more than once with different sample names.'.format(rg['ID']))
                    else:
                        rg_sm_mapping[rg['ID']] = rg['SM']
            return job_arglist
        
        raise TypeError("""
Error parsing command line {0}:
{1}
Not a valid snap call.""".format(line_no, command))
    finally:
        try:
            commands.close()
        except:
            pass
    return job_arglist


SnapCLParser = argparse.ArgumentParser(prog='mimodd snap', add_help = False, conflict_handler = 'resolve')
# mandatories (positional arguments)
SnapCLParser.add_argument('mode', metavar = 'sequencing mode', choices = ('single', 'paired'), help = 'specify "single" or "paired" to indicate the sequencing mode')
SnapCLParser.add_argument('refgenome_or_indexdir', metavar = 'reference genome or index directory', help = 'an existing index directory generated by snap_index or a fasta reference genome (will be used to create the index)')
SnapCLParser.add_argument("inputfiles", metavar = 'input file(s)', nargs = "+", help = "one or two (in 'paired' mode with 'fastq' input format) input files")
# optionals (optional arguments)
# defaulting to argparse.SUPPRESS prevents function definition defaults from being overwritten
SnapCLParser.add_argument("-o", "--ofile", metavar = 'OFILE', dest = 'outputfile', required = True, default = argparse.SUPPRESS, help = 'name of the output file (required)')
SnapCLParser.add_argument("--iformat", default = "bam", help = 'input file format; must be fastq, gz, sam or bam (default: bam)')
SnapCLParser.add_argument("--oformat", default = "bam", help = 'output file format (sam or bam; default: bam)')
SnapCLParser.add_argument('--header', default = argparse.SUPPRESS, help = 'a SAM file providing header information to be used for the output (required for input in fastq format and with unheadered SAM/BAM input, optional for headered SAM/BAM input; replaces header information found in the input file')
SnapCLParser.add_argument("-d", "--maxdist", metavar = 'EDIT DISTANCE', type = int, default = 8, help = 'maximum edit distance allowed per read or pair (default: 8)')
SnapCLParser.add_argument("-n", "--maxseeds", metavar = 'SEEDS', type = int, default = argparse.SUPPRESS, help = 'number of seeds to use per read (default: 25)')
SnapCLParser.add_argument("-h", "--maxhits", metavar = 'HITS', type = int, default = argparse.SUPPRESS, help = 'maximum hits to consider per seed (default: 250)')
SnapCLParser.add_argument("-c", "--confdiff", metavar = 'THRESHOLD', type = int, default = 2, help = 'confidence threshold (default: 2)')
SnapCLParser.add_argument("-a", "--confadapt", metavar = 'THRESHOLD', type = int, default = 7, help = 'confidence adaptation threshold (default: 7)')
SnapCLParser.add_argument("-t", "--threads", type = int, default = argparse.SUPPRESS, help = 'number of threads to use (overrides config setting)')
SnapCLParser.add_argument("-b", "--bind-threads", dest = 'bind_threads', action = 'store_true', default = argparse.SUPPRESS, help = 'bind each thread to its processor (off by default)')
SnapCLParser.add_argument("-e", "--error-rep", dest = 'error_rep', action = 'store_true', default = argparse.SUPPRESS, help = 'compute error rate assuming wgsim-generated reads')
SnapCLParser.add_argument('-P', '--no-prefetch', dest = 'no_prefetch', action = 'store_true', default = False, help = 'disables cache prefetching in the genome; may be helpful for machines with small caches or lots of cores/cache')
SnapCLParser.add_argument('--sort', '--so', metavar = 'MEMORY', nargs = '?', type = int, const=0, default = argparse.SUPPRESS, help = 'sort output file by alignment location; may be followed by the memory to use in Gb')
SnapCLParser.add_argument("-x", "--explore", action = 'store_true', default = argparse.SUPPRESS, help = 'explore some hits of overly popular seeds (useful for filtering)')
SnapCLParser.add_argument("-f", '--stop-on-first', dest = 'stop_on_first', action = 'store_true', default = argparse.SUPPRESS, help = 'stop on first match within edit distance limit (filtering mode)')
SnapCLParser.add_argument("-F", "--filter-output", dest = 'filter_output', metavar = 'FILTER', default = argparse.SUPPRESS, help = 'retain only certain read classes in output (a=aligned only, s=single hit only, u=unaligned only)')
SnapCLParser.add_argument("-I", "--ignore", action = 'store_true', default = argparse.SUPPRESS, help = 'ignore non-matching IDs in the paired-end aligner')
SnapCLParser.add_argument("-S", "--selectivity", type = int, default = argparse.SUPPRESS, help = 'selectivity; randomly choose 1/selectivity of the reads to score')
SnapCLParser.add_argument("-C", "--clipping", metavar = '++|+-|-+|--', default = argparse.SUPPRESS, help = 'specify a combination of two + or - symbols to indicate whether to clip low-quality bases from the front and back of reads respectively; default: back only (-C-+)')
SnapCLParser.add_argument("-M", "--mmatch-notation", dest = 'mmatch_notation', action = 'store_true', default = argparse.SUPPRESS, help = 'indicates that CIGAR strings in the generated SAM file should use M (alignment match) rather than = and X (sequence (mis-)match)')
SnapCLParser.add_argument("-G", "--gap-penalty", dest = 'gap_penalty', metavar = 'PENALTY', type = int, default = argparse.SUPPRESS, help = 'specify a gap penalty to use when generating CIGAR strings')
SnapCLParser.add_argument("-s", "--spacing", nargs = 2, metavar = ('MIN','MAX'), default = argparse.SUPPRESS, help = 'min and max spacing to allow between paired ends (default: 100 10000)')
SnapCLParser.add_argument('--max-mate-overlap', '--mmo', dest = 'max_mate_overlap', metavar = 'FRACTION', type = float, default = argparse.SUPPRESS, help = 'for paired-end reads only retain reads with maximally this fraction of their length overlap with their mate; default: 0 (no overlap allowed)')
SnapCLParser.add_argument('-q', '--quiet', action = 'store_true', default = False, help = 'suppress original messages from SNAP')
SnapCLParser.add_argument('-v', '--verbose', action = 'store_true', default = False, help = 'verbose output (independent of SNAP)')
idx_group = SnapCLParser.add_argument_group('optional arguments affecting indexing')
idx_group.add_argument("--idx-seedsize", dest = 'idx_seedsize', metavar = 'SEED SIZE', type = int, default = argparse.SUPPRESS, help = 'Seed size used in building the index (default: 20)')
idx_group.add_argument("--idx-slack", dest = 'idx_slack', metavar = 'SLACK', type = float, default = argparse.SUPPRESS, help = 'Hash table slack for indexing (default: 0.3)')
idx_group.add_argument('--idx-overflow', dest ='idx_ofactor', metavar = 'FACTOR', type = int, default = argparse.SUPPRESS, help = 'factor (between 1 and 1000) to set the size of the index build overflow space (default: 40)')
idx_group.add_argument('--idx-out', metavar = 'INDEX DIR', dest = 'idx_out', default = argparse.SUPPRESS, help = 'name of the index directory to be created; if given, the index directory will be permanent, otherwise a temporary directory will be used')

def clparse(args = None):
    """Command line parsing to make snap_call() usable from the terminal."""
    
    return vars(SnapCLParser.parse_args(args)).copy()


def snap_index (ref_genome, index_out, seedsize = None, slack = None, ofactor = None, threads = None, verbose = False, quiet = True):
    """A simple wrapper around SNAP index."""
    
    # --------------------- OS X 10.10 Yosemite --------------------
    #   emergency action until bug-fix for SNAP becomes available
    #
    # SNAP produces corrupt multi-threaded output under Yosemite
    # => run it with single thread (slow, but stable)
    
    platform_description = platform.uname()
    if platform_description[0] == 'Darwin' and platform_description[2].split('.')[0] == '14':
        # kernel version 14.x.x indicates Yosemite
        threads = 1
    # --------------------------------------------------------------

    if not threads:
        threads = config.multithreading_level
    if ofactor is not None:
        if ofactor < 1:
            ofactor = 1
        elif ofactor > 1000:
            ofactor = 1000
    with open(ref_genome, 'r') as ifo:
        md5sums = [md5 for md5 in FastaReader(ifo).md5sums()]
    call = [snap_exe, "index", ref_genome, index_out, '-t{0}'.format(threads)]
    if seedsize:
        call += ['-s', str(seedsize)]
    if slack:
        call += ['-h', str(slack)]
    if ofactor:
        call += ['-O{0}'.format(ofactor)]
    if verbose:
        print('Calling snap index with:')
        print(' '.join(call))
        print()

    results, errors = (s.decode() for s in subprocess.Popen(call, bufsize = -1, stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate())

    if not quiet:
        print ('\n'.join(n for n in results.split('\n') if not n.startswith('HashTable[')))
    if not errors:
        with open(os.path.join(index_out, 'md5sums'), 'w') as md5_out:
            for seqtitle, md5 in md5sums:
                # replace spaces with underscores just like SNAP
                seqtitle = '_'.join(seqtitle.split(' '))
                md5_out.write('{0}\t{1}\n'.format(seqtitle, md5))
    else:
        raise RuntimeError ("The following error message was raised by SNAP index:\n" + errors)

    return call, results, errors

