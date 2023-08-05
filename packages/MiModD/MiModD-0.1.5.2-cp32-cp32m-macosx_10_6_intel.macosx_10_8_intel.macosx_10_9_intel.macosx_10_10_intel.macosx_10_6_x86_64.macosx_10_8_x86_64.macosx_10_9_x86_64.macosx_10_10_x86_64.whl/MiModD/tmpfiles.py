import os.path
import shutil
import random
from .config import tmpfiles_path

def tmp_hardlink (ifile, prefix, suffix, fallback = 'symbolic'):
    """Generate a temporary hard link to an input file.

    Uses unique_tmpfile_name to obtain a randomized name for the link.
    If a hard link cannot be generated because ifile and hard_link point
    to different physical storage devices, a symbolic link or a copy is
    generated instead depending on the fallback argument."""
    
    supported_fallbacks = ('symbolic', 'copy')
    if fallback not in supported_fallbacks:
        raise ValueError ('Unsupported fallback behavior. Only {0} accepted'.format(supported_fallbacks))
    hard_link = unique_tmpfile_name(prefix, suffix)
    ifile = os.path.abspath(ifile) # an abspath is required just in case we need to soft-link
    try:
        try:
            os.link(ifile, hard_link)
        except OSError as e:
            if e.errno == 18: # catch Invalid cross-device link
                if fallback == 'symbolic':
                    os.symlink(ifile, hard_link)
                elif fallback == 'copy':
                    shutil.copyfile(ifile, hard_link)
            else:
                raise
            
        return hard_link
    except:
        try:
            # unsafe in the (very) exceptional situation of a race condition
            # involving the random file name returned from unique_tmpfile_name
            os.remove(hard_link)
        except:
            pass
        raise # could use raise from None in Python 3.3+ 

def unique_tmpfile_name (prefix='', suffix=''):
    """Generate a random temporary file name with fixed prefix and suffix.

    Adds a random number between 1 and 10000 between prefix and suffix and
    prepends the name with the temporary file path set in MiModD.config."""
    
    tmp_output_prefix = os.path.join(tmpfiles_path, prefix)
    while True:
        tmp_name = '{0}{1}{2}'.format(tmp_output_prefix, random.randint(1,10000), suffix)
        if not os.path.exists(tmp_name):
            return tmp_name
