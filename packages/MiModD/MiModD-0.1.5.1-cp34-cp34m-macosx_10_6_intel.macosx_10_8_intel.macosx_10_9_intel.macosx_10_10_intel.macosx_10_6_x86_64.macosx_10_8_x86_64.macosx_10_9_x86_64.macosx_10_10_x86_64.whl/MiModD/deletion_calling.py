import sys
import os
import signal
import random
import itertools
from math import log10

from . import mimodd_base, tmpfiles, samheader, pysamtools, pysam, pyvcf
from .fisher import fisher as fisher_exact
from .bioobj_base import Chromosome, Deletion

threshold = 0.01
            
def delcall (ibams, icov, ofile = None, max_cov = None, min_size = None, window = 100,
             include_uncovered = False, group_by_id = False, verbose = False):
    """Calls deletions in paired-end NGS data based on coverage and insert sizes.

    Uses find_lowcov_regions() to identify candidate regions based on low coverage, then
    calls del_stats() to compute significance scores for potential deletions
    based on the insert size distributions around the candidate region and
    elsewhere in the genome. It uses sample_insert_sizes() to obtain an
    estimate of the insert size distributions across the genome."""

    # watch out for SIGTERM to remove temporary files
    signal.signal(signal.SIGTERM, mimodd_base.catch_sigterm)

    original_bams, ibams = ibams, []
    try:
        # open the coverage file and retrieve the sample information
        coverage = pyvcf.open (icov, 'rb')
        samples = set(coverage.info.sample_names) 

        headers = []
        for ibam in original_bams:
            try:
                headers.append(samheader.Header.frombam(ibam))
            except RuntimeError:
                raise RuntimeError(
                    'Aligned reads input file {0} does not seem to be a BAM file'
                    .format(ibam))
        chrm_lengths = {sq['SN']: sq['LN'] for hdr in headers for sq in hdr['SQ']}
        
        # get the read groups of all input files as a flat object
        # using set here ensures that if data for one read group is
        # spread over several input files, that read group won't be used twice
        all_read_groups = [rg for hdr in headers for rg in hdr['RG']]
  
        # check bam RGs and cov header line to see if we have matching sample names
        # if not, try if we can make them match by appending _<RGID> to the
        # sample names in the bam file (this would indicate that the bam file names
        # were made unique by varcall before SNP calling
        for n in range(2):
            rgid_sm_mapping = {}
            for sample in samples:
                # this loop builds the matching_read_groups list
                matches = {rg['ID']:rg['SM'] for rg in all_read_groups if rg['SM'] == sample}
                if not matches:
                    rgid_sm_mapping = {}
                    break
                if len(matches) > 1 and group_by_id:
                    # the sample name from the cov file had several matches in the bam file(s)
                    # this is dealt with if deletions are to be called by sample name,
                    # but is inacceptable for calling them by read group id
                    raise RuntimeError('Ambiguous mapping of the sample names between the coverage and the bam input files.')
                rgid_sm_mapping.update(matches)
            if rgid_sm_mapping:
                # we're ok, proceed
                break
            elif n == 0:
                # some samples could not be found in the bam file headers
                # lets extend the header SM tags with the ID tag information
                # then check again
                for hdr in headers:
                    hdr.uniquify_sm()
                all_read_groups = [rg for hdr in headers for rg in hdr['RG']] # recalculate all_read_groups
        else:
            # neither the original headers nor the extended ones gave us a
            # successful mapping of all Cov file sample names
            print('Matching sample names between bam file and coverage file:', file = sys.stderr)
            print(', '.join([sm for sm in samples & {rg['SM'] for rg in all_read_groups}] or ['---']), file = sys.stderr)
            print('sample names found ONLY in coverage file:', file = sys.stderr)
            print(', '.join([sm for sm in samples - {rg['SM'] for rg in all_read_groups}]), file = sys.stderr)
            raise RuntimeError ('Some samples in the coverage file could not be matched to entries in the bam file.')


        # start indexing the input bam files
        ibams = [tmpfiles.tmp_hardlink(ibam, 'tmp_indexed_bam', '.bam') for ibam in original_bams]
        for ibam in ibams:
            call, results, errors = pysamtools.index(ibam)
            if errors:
                raise RuntimeError ('The following error message was raised by samtools index: {0}'.format(errors))


        # estimate the insert size distribution in the input bam
        sizes = sample_insert_sizes (ibams, rgid_sm_mapping)

        bam_input = [pysam.Samfile(ibam, 'rb') for ibam in ibams]

        if ofile:
            outdel = open(ofile, 'w')
        else:
            outdel = sys.stdout

        if verbose:
            print('Starting prediction for the following samples')
            print(', '.join(coverage.info.sample_names))
            uncallable_samples = {rg:sm for rg,sm in rgid_sm_mapping.items() if not sizes[rg]}
            if uncallable_samples:
                print('The following samples have been excluded from deletion calling (only Uncovered Regions will be reported for them):')
                print(','.join(['{0} [RG_ID:{1}]'.format(sm, rg) for sm,rg in uncallable_samples.items()]))
                
        last_start = 0
        for sample, deletion in find_lowcov_regions(coverage, max_cov, min_size):
            affected_rgs = [rgid for rgid, sm in rgid_sm_mapping.items() if sm == sample]
            if deletion.start-window <= 0 or deletion.stop == chrm_lengths[deletion.chromosome]:
                for rg in affected_rgs:
                    p_value = float('Nan')
                    outdel.write(write_region(deletion, p_value, sample, rg if len(affected_rgs) > 1 else None, include_uncovered))
            else:
                if deletion.start != last_start:
                    nearby_reads = [r for inbam in bam_input for r in
                                    inbam.fetch(deletion.chromosome,
                                    deletion.start-window,
                                    deletion.start)
                                    if r.mapq > 0]
                for rg in affected_rgs:
                    if not sizes[rg]:
                        p_value =float('Nan')
                    else:
                        p_value = del_stats(deletion,
                                            (r for r in nearby_reads if r.tags[[tag[0] for tag in r.tags].index('RG')][1] == rg),
                                            sizes[rg])
                    outdel.write(write_region(deletion, p_value, sample, rg if len(affected_rgs) > 1 else None, include_uncovered))
                    last_start = deletion.start
                
    finally:
        try:
            coverage.close()
        except:
            pass
        if locals().get('bam_input'):
            for inbam in bam_input:
                try:
                    inbam.close()
                except:
                    pass
        try:
            outdel.close()
        except:
            pass
        for ibam in ibams:
            try:
                os.remove(ibam)
            except:
                pass
            try:
                os.remove(ibam + '.bai')
            except:
                pass


def find_lowcov_regions(coviter, max_cov = None, min_size = None):
    if not max_cov:
        max_cov = 0
    if not min_size:
        min_size=100
    contig_lengths = coviter.info.contigs
    sample_names = coviter.info.sample_names
    unc_current = {sample: ['', 1] for sample in sample_names}
    for cov in coviter.cov_iter():
        for sample in sample_names:
            if unc_current[sample][0] != cov[0]:
                if unc_current[sample][0] and min_size <= contig_lengths[unc_current[sample][0]] - unc_current[sample][1]:
                    yield sample, Deletion(unc_current[sample][0], unc_current[sample][1], contig_lengths[unc_current[sample][0]])
                unc_current[sample] = [cov[0], 1]                    
            if cov[2][sample] > max_cov:
                if min_size <= cov[1] - unc_current[sample][1]:
                    yield sample, Deletion(unc_current[sample][0], unc_current[sample][1], cov[1] - 1)
                unc_current[sample][1] = cov[1] + 1
    # done, but need to process pending deletions
    for sample in sample_names:
        if unc_current[sample][0] and min_size <= contig_lengths[unc_current[sample][0]] - unc_current[sample][1]:
            yield sample, Deletion(unc_current[sample][0], unc_current[sample][1], contig_lengths[unc_current[sample][0]])


def sample_insert_sizes (ibams, rgid_sm_mapping, sampling_depth = 100):
    headers = []
    for ibam in ibams:
        headers.append(samheader.Header.frombam(ibam))
    # merge header information into a set of Chromosome instances
    # to do: move the merging part to samheader module (merge function or method)
    chrms = {Chromosome(name, length) for name, length in {sq['SN']: sq['LN'] for hdr in headers for sq in hdr['SQ']}.items()}
    # ensure constant results for same set of bam input files
    random.seed(''.join([str(hdr) for hdr in headers]))
    try:
        bam_input = [pysam.Samfile(ibam, 'rb') for ibam in ibams]
        sizes = {rg:[] for rg in rgid_sm_mapping}
        
        for chrm in chrms:
            given_up_rgs = set()
            for x in range (sampling_depth):
                samples_to_treat = {rg:sm for rg,sm in rgid_sm_mapping.items() if rg not in given_up_rgs}
                if not samples_to_treat:
                    break
                trials = 0
                # keep repeating sampling for samples for which no appropriate read
                # was found up to 50 trials, then exclude the sample for this chromosome
                for trial in range (500):
                    randpos = chrm.randpos()
                    fetchers = [inbam.fetch(chrm.name, randpos, randpos+1) for inbam in bam_input]
                    for read in itertools.chain(*fetchers):
                        if read.is_proper_pair and not read.is_reverse and read.tlen >= 0:
                            rgid = dict(read.tags)['RG'] # equally fast as the out-commented variant below
                            # rgid = read.tags[[tag[0] for tag in read.tags].index('RG')][1]
                            if rgid in samples_to_treat:
                                sizes[rgid].append(read.pnext-read.pos-read.alen) # append the insert size
                                del samples_to_treat[rgid]
                                if not samples_to_treat:
                                    break
                    if not samples_to_treat:
                        break
                for rg in samples_to_treat:
                    given_up_rgs.add(rg)
    finally:
        try:
            for inbam in bam_input:
                try:
                    inbam.close()
                except:
                    pass
        except:
            pass

    return sizes

def del_stats (deletion, adjacent_reads, sizes):
    without_mate = with_mate = short_seq = large_seq = 0

    effective_lengths = []
    for read in adjacent_reads:
        if read.is_paired and not read.is_reverse:
            if read.mate_is_unmapped:
                without_mate += 1
            elif read.pnext >= deletion.stop:
                with_mate +=1
            effective_lengths.append(deletion.stop - (read.pos+read.alen+1)) # deletion coordinates are 1-based, but pysam uses 0-based system
    if with_mate + without_mate == 0:
        return float('Nan')
    for length in sizes:
        if length < random.choice(effective_lengths):
            short_seq += 1
        else:
            large_seq += 1
    p_value = fisher_exact(with_mate, without_mate, large_seq, short_seq)
    return p_value

def write_region(deletion, p_value, sample, rg = None, include_uncovered = False):
    if p_value < threshold:
        region_type = 'Deletion'
        region_score = str(int(-10*log10(p_value)))
    elif include_uncovered:
        region_type = 'Uncovered_Region'
        region_score = '.'
    else:
        return ''

    return '\t'.join([deletion.chromosome, 'MiModD', region_type,
                      str(deletion.start), str(deletion.stop),
                      region_score, '.', '.',
                      'sample={0} {1};p_value={2:e}'.format(sample, '[RG_ID:{0}]'.format(rg) if rg else '', p_value), '\n'])

