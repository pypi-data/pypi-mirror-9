import sys, os
from . import pysamtools

if __name__ == '__main__':
    inputfile = os.path.realpath(os.path.expanduser(sys.argv[1]))
    if not os.path.isfile(inputfile):
        raise FileNotFoundError('File to index does not seem to exist: {0}'.format(inputfile))
    print ()
    print ('running samtools index on', inputfile, '...')
    call, results, errors = pysamtools.index(inputfile, reindex = True)
    print ('command: "{0}" finished.'.format(' '.join(call)))
    print ()
    assert os.path.isfile(inputfile + '.bai'), 'Something unexpected happened. Could not generate index file.'
    print ('index file is at: {0}.bai'.format(inputfile))
