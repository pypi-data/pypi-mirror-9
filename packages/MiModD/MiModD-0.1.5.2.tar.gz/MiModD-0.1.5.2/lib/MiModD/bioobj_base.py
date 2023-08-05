import random

class Chromosome (object):
    """An object representation of a chromosome.

    Uses 1-based coordinates."""
    
    def __init__ (self, name, length=0):
        self.name = name
        self.length = length

    def randpos (self, start=1, end=None, relpos=False):
        """Returns a random nucleotide position from the chromosome.

        start and end specify an inclusive interval."""

        if end is None:
            end = self.length
        if relpos:
            end = self.length-end
        if not 1 <= start <= self.length:
            if self.length == 0:
                raise NotImplementedError ('Chromosome.length not set.')
            raise ValueError ('start position outside chromosome boundaries.')
        if not start <= end <= self.length:
            raise ValueError ('invalid end position (smaller than start or outside chromosome boundaries.')
        return random.randrange(start, end+1)

    @property
    def shortname (self):
        for prefix in ('CHROMOSOME_', 'CHROMOSOME', 'CHR_', 'CHR'):
            if self.name.upper().startswith(prefix):
                return 'chr' + self.name[len(prefix):]
        return 'chr' + self.name

    @property
    def barename (self):
        return self.shortname[3:]
            
class Transcript (str):
    @property
    def basename (self):
        return self.split('.')[0]

class Deletion (object):
    def __init__(self, chrm, start, stop, sample = None):
        self.chromosome = chrm
        self.start = start
        self.stop = stop
