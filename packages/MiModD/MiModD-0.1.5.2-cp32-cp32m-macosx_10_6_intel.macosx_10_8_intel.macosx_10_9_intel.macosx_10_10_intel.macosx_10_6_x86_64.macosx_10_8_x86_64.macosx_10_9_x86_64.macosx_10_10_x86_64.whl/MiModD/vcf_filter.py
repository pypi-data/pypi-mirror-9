import sys
from . import pyvcf

SNP_TYPE = 1
INDEL_TYPE = 2

def filter(ifile, ofile = None, samples = (), gt = (), dp = (), gq = (), type_filter = None, region_filter = None, v_filter = None):
    # parameter sanity checks
    sample_no = len(samples)
    if gt == ():
        gt = ('ANY',) * sample_no
    if dp == ():
        dp = (0,) * sample_no
    if gq == ():
        gq = (0,) * sample_no
    if not all(len(param) == len(samples) for param in (gt, dp, gq)):
        raise ValueError('The number of samples must match the number of genotype filters.')
    # transform region_filter from a sequence of regions to a chromosome-based dictionary
    if region_filter:
        region_dict ={}
        for r in region_filter:
            try:
                chrom, posinfo = r.split(':')
                if posinfo:
                    start, stop = [int(e) for e in posinfo.split('-')]
                else:
                    start = 0
                    stop = float('inf')
            except ValueError:
                raise ValueError('Region filters must be specified in the format CHROM:START-STOP')
            if chrom not in region_dict:
                region_dict[chrom] = [(start, stop)]
            else:
                region_dict[chrom].append((start, stop))
        region_filter = region_dict
    
    # prepare filter dictionary    
    filters = {sample:{'GT':_gt.split(','),
                       'DP':_dp,
                       'GQ':_gq}
               for sample, _gt, _dp, _gq in zip(samples, gt, dp, gq)}

    # remove wildcards from filters dict
    for f in filters.values():
        if 'ANY' in f['GT']:
            if len(f['GT'])>1:
                raise ValueError('If "ANY" is used with --gt it has to be the only argument')
            else:
                del f['GT']
        if f['DP'] == 0:
            del f['DP']
        if f['GQ'] == 0:
            del f['GQ']

    try:
        # open IO channels
        in_vcf = pyvcf.open(ifile, 'r')
        if ofile:
            out_vcf = open(ofile, 'w')
        else:
            out_vcf = sys.stdout

        # write metadata
        if v_filter:
            out_vcf.write(str(in_vcf.info.sample_slice(v_filter)))
        else:
            out_vcf.write(str(in_vcf.info))
        out_vcf.write('\n')

        # set up filters for variant types and chromosomes
        if not type_filter:
            rec_iterator = in_vcf.filter(filters, v_filter)
        elif type_filter == INDEL_TYPE:
            rec_iterator = (rec for rec in in_vcf.filter(filters, v_filter) if 'INDEL' in rec.info)
        elif type_filter == SNP_TYPE:
            rec_iterator = (rec for rec in in_vcf.filter(filters, v_filter) if 'INDEL' not in rec.info)
        else:
            raise ValueError ('Unrecognized variant type filter {0}'.format(type_filter))
        if region_filter:
            rec_iterator = (rec for rec in rec_iterator
                            if rec.chrom in region_filter and
                            any(interval[0] <= rec.pos <= interval[1] for interval in region_filter[rec.chrom]))

        # process the vcf file entries
        for rec in rec_iterator:
            out_vcf.write(str(rec))
            out_vcf.write('\n')
    finally:
        try:
            in_vcf.close()
        except:
            pass
        if out_vcf is not sys.stdout:
            try:
                out_vcf.close()
            except:
                pass

