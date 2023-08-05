import subprocess
from . import config

class bcfViewer (object):
    def __init__ (self, ifile):
        self.ifile = ifile
        call = [config.bcftools_exe, 'view', ifile]
        self.subprocess = subprocess.Popen(call,
                          stdout = subprocess.PIPE,
                          universal_newlines = True)
        self.stream = self.subprocess.stdout

    def __iter__ (self):
        return self

    def __next__ (self):
        return next(self.stream)

    def readline (self):
        return self.stream.readline()

    def close (self):
        self.stream.close()
    
def view (ifile):
    return bcfViewer(ifile)
