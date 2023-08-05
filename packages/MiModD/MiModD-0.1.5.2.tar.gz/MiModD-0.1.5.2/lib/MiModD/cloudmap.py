import sys
from . import pyvcf

def vcf_to_cloudmap (mode, ifile, sample, reference = None, ofile = None, seqdict_file = None, verbose = False):
    mode = mode.upper()
    if mode == 'VAF':
        if not reference:
            raise RuntimeError('Mode "{0}" requires reference to be specified.'
                                .format(mode))
    elif mode == "SVD":
        if reference:
            raise RuntimeError('Reference can not be used in mode "{0}"'
                                .format(mode))
    else:
        raise ValueError ('Expected one of "SVD", "VAF" for mode.')
            
    if seqdict_file:
        cloudmap_seqdict_from_vcf (ifile, seqdict_file)
    try:
        vcf = pyvcf.open(ifile)
        if not ofile:
            out = sys.stdout
        else:
            out = open(ofile, 'w')

        if sample not in vcf.info.sample_names:
            raise RuntimeError('Sample {0}: no such sample name in the vcf file.'.format(sample))

        out.write(str(vcf.info.sample_slice([sample])) + '\n')

        if mode == 'SVD':
            for record in vcf:
                out.write(str(record.sample_slice([sample])) + '\n')
        elif mode == 'VAF':
            if reference not in vcf.info.sample_names:
                raise RuntimeError('Reference sample {0}: no such sample name in the vcf file.'.format(reference))

            for record in vcf:
                ref_allele_nos = {int(n) for n in record.sampleinfo['GT'][reference].split('/') if n !='.'}
                if len(ref_allele_nos) == 1:
                    ref_allele_no = ref_allele_nos.pop()
                    dpr_counts = [int(count) for count in record.sampleinfo['DPR'][sample].split(',')]
                    if sum(dpr_counts) > 0:
                        for allele_no in sorted(range(0, len(dpr_counts)), key = lambda index: dpr_counts[index], reverse = True):
                            if allele_no != ref_allele_no:
                                record.alt = record.alt_from_num(allele_no or ref_allele_no)
                                record.sampleinfo['AD'] = {}
                                ref_count = dpr_counts.pop(ref_allele_no)
                                record.sampleinfo['AD'][sample] = '{0},{1}'.format(sum(dpr_counts), ref_count)
                                record = record.sample_slice([sample])
                                out.write(str(record) + '\n')                            
                                break
        else:
            raise AssertionError('Oh oh, this looks like a bug')
            
    finally:
        try:
            vcf.close()
        except:
            pass
        if out is not sys.stdout:
            try:
                out.close()
            except:
                pass
            
def cloudmap_seqdict_from_vcf (ifile, ofile = None):
    try:
        vcf = pyvcf.open(ifile)
        if not ofile:
            out = sys.stdout
        else:
            out = open(ofile, 'w')
        
        for ident, length in vcf.info.contigs.items():
                out.write ('{0}\t{1}\n'.format(ident, int(length)//10**6+1))
    finally:
        try:
            vcf.close()
        except:
            pass
        if out is not sys.stdout:
            try:
                out.close()
            except:
                pass
    
