"""A collection of wrappers that provide a functional programming interface
to the csamtools software suite."""

import subprocess
import glob
import os
import signal
import tempfile
from collections import namedtuple
from . import config, mimodd_base, tmpfiles

SamtoolsReturnValue = namedtuple('SamtoolsReturnValue', ['call', 'results', 'errors'])

class Command (object):
    """Object representation of a samtools subcommand call.

    To be used by faidx, _iheader, index, reheader, sort, cat and view.
    Not yet ready for use."""

    def __init__ (self, subcommand, parameters, o_redirect = False, fatal_strings=[]):
        pass

    def execute (self):
        if o_redirect:
            proc = subprocess.Popen(self.call, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            results, errors = (s.decode() for s in proc.communicate())
        else:
            # output is going to stdout, so better don't PIPE it !!
            proc = subprocess.Popen(self.call, shell = True, stderr = subprocess.PIPE)
            results, errors = None, proc.communicate()[1].decode()            
        if proc.returncode or any([msg in errors for msg in self.fatal_strings]):
            # can't rely on return code alone here because some samtools subcommands, e.g. samtools sort, inappropriately
            # return 0 with some errors
            raise RuntimeError ('{0} failed with: {1}'.format(self.call, errors or 'no error message'))
        return SamtoolsReturnValue(self.call, results, errors)
    
def faidx (ref_genome):
    """Wrapper around samtools faidx."""
    
    call = [config.samtools_legacy_exe, 'faidx', ref_genome]
    results, errors = (s.decode() for s in subprocess.Popen(call, bufsize = -1, stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate())

    if errors:
        raise RuntimeError ("ERROR raised by samtools faidx:\n" + errors)

    return SamtoolsReturnValue(call, results, errors)

def header (inputfile, iformat):
    """Wrapper around samtools view -H.

    Yields an iterator over the header lines of a sam/bam file."""

    if iformat == "sam":
        call = [config.samtools_legacy_exe, 'view', '-H', '-S', inputfile]
    elif iformat == "bam":
        call = [config.samtools_legacy_exe, 'view', '-H', inputfile]
    
    results, errors = (s.decode() for s in subprocess.Popen(call, stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate())

    if not results:
        if errors:
            msg = 'Could not obtain header information from the {0} input file.'.format(iformat.upper())
            msg += '\n{0} failed with: {1}'.format(' '.join(call), errors)
            raise RuntimeError(msg)
        else:
            return
    
    for line in results.strip().split('\n'):
        yield line
    
def index (inputfile, reindex = False):
    """Wrapper around samtools index."""

    if os.path.exists(inputfile+'.bai') and not reindex:
        return SamtoolsReturnValue('', '', '')
    call = [config.samtools_legacy_exe, 'index', inputfile]
    results, errors = (s.decode() for s in subprocess.Popen(call, bufsize = -1, stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate())
    if errors:
        raise RuntimeError('{0}\nfailed with the following error from samtools index:\n{1}'.format(' '.join(call), errors))
    return SamtoolsReturnValue(call, results, errors)

def reheader (template, inputfile, outputfile = None, verbose = False):
    """Wrapper around samtools reheader."""

    if isinstance (template, str):        
        call = [config.samtools_legacy_exe, 'reheader', template, inputfile]
        stdin_pipe = None
        input_bytes = None
    elif isinstance (template, dict):
        call = [config.samtools_legacy_exe, 'reheader', '-', inputfile]
        stdin_pipe = subprocess.PIPE
        input_bytes = str(template).encode()
    if outputfile:
        stdout_pipe = open(outputfile, 'wb')
    else:
        stdout_pipe = None
    if verbose:
        print ('generating new bam from {0} with new header from template {1}'.format(inputfile, template))

    p = subprocess.Popen(call, stdout = stdout_pipe, stderr = subprocess.PIPE, stdin = stdin_pipe)
    results, errors = None, p.communicate(input = input_bytes)[1].decode()
    if outputfile:
        stdout_pipe.close()
    if errors:
        raise RuntimeError('{0}\nfailed with:\n{1}'.format(' '.join(call), errors))

    return SamtoolsReturnValue(call, results, errors)
    
def sort (inbam, outfile = None, oformat = 'bam', maxmem = None, threads = None, by_read_name = False, compression_level = None):
    """Wrapper around samtools sort.

    Improvements over wrapped tool:
    - samtools sort adds an extra '.bam' to the final output file, here we don't;
    - ensures cleanup of temporary files upon unexpected termination of samtools,
      where samtools would leave them behind;
    - never pollutes the final output directory with temporary files;
    - treats errors more consistently than samtools;
    - enables output in SAM format;
    - simpler call signature.
    """

    # define samtools sort stderr output signatures that indicate an error despite a 0 return code
    fatal_strings = ['No such file or directory']
    
    if not threads:
        threads = config.multithreading_level

    maxmem = (maxmem or config.max_memory)*10**9 / threads
        
    tmp_output = tmpfiles.unique_tmpfile_name ('MiModD_sort','')
    if oformat == 'bam':
        call = 'sort {0} {1} -@ {2} -m {3} -o "{4}" "{5}"'.format('-n' if by_read_name else '',
                                                                  '-l {0}'.format(compression_level) if compression_level else '',
                                                                  threads, maxmem, inbam, tmp_output)
    elif oformat == 'sam':
        call = 'sort {0} -@ {1} -m {2} -o "{3}" "{4}" | {5} view -h -'.format('-n' if by_read_name else '',
                                                                              threads, maxmem,
                                                                              inbam, tmp_output,
                                                                              config.samtools_legacy_exe)
        # piping the bam to samtools view this way raises
        # '[bam_header_read] EOF marker is absent. The input is probably truncated.',
        # but it seems to be ok to ignore this
    else:
        raise ValueError ('unknown output format {0}. Valid formats are bam and sam'.format(oformat))

    if outfile:
        call = '{0} > "{1}"'.format(call, outfile)
        
    call = '{0} {1}'.format(config.samtools_legacy_exe, call)
    signal.signal(signal.SIGTERM, mimodd_base.catch_sigterm)
    try:
        # we may need to delete temporary files created by samtools
        if outfile:
            proc = subprocess.Popen(call, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            results, errors = (s.decode() for s in proc.communicate())
        else:
            # output is going to stdout, so better don't PIPE it !!
            proc = subprocess.Popen(call, shell = True, stderr = subprocess.PIPE)
            results, errors = None, proc.communicate()[1].decode()            
        if proc.returncode or any([msg in errors for msg in fatal_strings]):
            # can't rely on return code alone here because samtools sort inappropriately returns 0 with
            # some errors
            raise RuntimeError ('{0} failed with: {1}'.format(call, errors or 'no error message'))
    except:
        # try to remove temporary files created by samtools and may have been left behind
        for file in glob.iglob(tmp_output+'.*.bam'):
            try:
                os.remove(file)
            except:
                pass
    return SamtoolsReturnValue(call, results, errors)


def cat (infiles, outfile, oformat, headerfile = None):
    """Wrapper around samtools cat, but with additional header management."""

    if oformat not in ('sam', 'bam'):
        raise ValueError ('unknown output format {0}. Valid formats are bam and sam'.format(oformat))

    if len(infiles) > 1:
        # calling samtools cat
        command_strings = ['cat']
        if headerfile:
            command_strings += ['-h "{0}"'.format(headerfile)]
        if oformat == 'bam':
            command_strings += ['-o "{0}"'.format(outfile)]
        for file in infiles:
            command_strings.append('"{0}"'.format(file))
        if oformat == 'sam':
            command_strings += ['| {0} view -h -o "{1}" -'.format(config.samtools_legacy_exe, outfile)]
        call = ' '.join(command_strings)
        call = '{0} {1}'.format(config.samtools_legacy_exe, call)
        results, errors = (s.decode() for s in subprocess.Popen(call, shell = True, bufsize = -1, stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate())
        if errors:
            raise RuntimeError('{0}\nfailed with the following samtools error:\n{1}'.format(call, errors))

        return SamtoolsReturnValue(call, results, errors)
    else:
        # with only one file just rewrite it using samtools view, but respect output format
        ret = view (infiles[0], 'bam', outfile, oformat)
        return ret
    
def view (infile, iformat, outfile, oformat):
    """Simple wrapper around samtools view."""

    fatal_strings = []
    call = [config.samtools_exe, 'view']
    if oformat == 'bam':
        call.append('-b')
    elif oformat == 'sam':
        call.append('-h')
    if iformat == 'sam':
        call.append('-S')
    if outfile:
        call.extend(['-o', outfile])
    call.append(infile)

    if outfile:
        proc = subprocess.Popen(call, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        results, errors = (s.decode() for s in proc.communicate())
    else:
        # output is going to stdout, so better don't PIPE it !!
        proc = subprocess.Popen(call, stderr = subprocess.PIPE)
        results, errors = None, proc.communicate()[1].decode()            
    if proc.returncode or any([msg in errors for msg in fatal_strings]):
        # see sort() for rationale behind this
        raise RuntimeError ('{0} failed with: {1}'.format(' '.join(call), errors or 'no error message'))

    return SamtoolsReturnValue(call, results, errors)
