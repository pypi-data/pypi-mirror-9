import hashlib
from .iterx import SepIter

class FastaReader (SepIter):

    RECORD_SEP = '>'
    
    def __init__ (self, iterable):
        self.super = super(FastaReader, self) # set this for fast access by next()
        self.super.__init__(iterable, self.RECORD_SEP)
        
    def sequences (self):
        for header, seq_iter in self:
            yield (header, ''.join(s.strip() for s in seq_iter))

    def md5sums (self):
        for header, seq_iter in self:
            md5 = hashlib.md5()
            for seqline in seq_iter:
                md5.update(seqline.strip().upper().encode())
            yield (header, md5.hexdigest())

def get_fasta_info (ifile):
    dna_strings = 'ACGTNKSYMWRBDHV'
    dna_strings += dna_strings.lower()
    IUPAC_DNA_codes = set(dna_strings)

    seqinfo = []
    with open(ifile, 'r') as ifo:
        for header, seq_iter in FastaReader(ifo):
            if header is None:
                raise RuntimeError('Expected ">" at start of file')
            seqlen = 0
            md5 = hashlib.md5()
            for seqline in seq_iter:
                seqline = seqline.strip().upper()
                if any(c not in IUPAC_DNA_codes for c in seqline):
                    raise RuntimeError('Invalid nucleotide code in sequence ' + header)
                seqlen += len(seqline)
                md5.update(seqline.encode())
            if seqlen == 0:
                raise RuntimeError('No nucleotide information found for sequence ' + header)
            seqinfo.append({'SN': header, 'LN': seqlen, 'M5': md5.hexdigest()})
    return seqinfo
