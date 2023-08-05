import os
import sys
import subprocess
from collections import namedtuple, OrderedDict
from . import config, tmpfiles, pyvcf, anno_weblinks, bioobj_base

def annotate (inputfile, genome = None, species = None, ofile=None, oformat = 'html', snpeff_out = None, grouping = None, link_formatter = None, **snpeff_options):
    """High-level function to run SnpEff and convert its output to pretty-formatted html."""

    outputfile = snpeff_out if snpeff_out else tmpfiles.unique_tmpfile_name ('snpeff','.vcf')
    snpeff_path = snpeff_options.get('snpeff_path') or config.snpeff_path
    try:
        if genome:
            # call snpeff, then work on resulting vcf
            snpeff (genome, inputfile, outputfile, **snpeff_options)
            vcf_to_annotate = pyvcf.open(outputfile)
        else:
            # work on input file directly
            vcf_to_annotate = pyvcf.open(inputfile)

        if grouping == "by_sample":
            vcf_iter = vcf_to_annotate.by_sample
        elif grouping is None:
            vcf_iter = vcf_to_annotate.expand_samples
        elif grouping == "by_genes":
            vcf_iter = affected_genes(vcf_to_annotate)

        if oformat == 'html':
            # html pre-formatting
            header="""\
<html>
<body>
<table border="1">
<tr>
<th>Sample</th>
<th>Chromosome</th>
<th>Position</th>
<th>Change</th>
<th>Affected Gene</th>
<th>Transcript</th>
<th>Effect</th>
<th>Genotype</th>
"""

            line_template="""\
<tr>
<td>{sample}</td>
<td>{chromosome}</td>
<td>{position}</td>
<td>{change}</td>
<td>{gene}</td>
<td>{transcript}</td>
<td>{effect}</td>
<td>{genotype}</td>
"""

            footer="""\
</table>
</body>
</html>
"""
        else:
            header = 'Sample\tChromosome\tPosition\tChange\tAffected Transcript\tEffect\tGenotype\n'
            line_template = footer = ''

        if oformat == 'html':
            if genome and not species:
                # if no organism species is specified, try to get it from SnpEff's config file
                snpeff_species = get_organism_from_snpeff_genome(genome, snpeff_path)
                # replace underscores with spaces
                species = ' '.join(snpeff_species.split('_'))

            if not species and link_formatter:
                raise RuntimeError('Need a species name to use with the link formatter file')
            
            if link_formatter:
                try:
                    link_formatter = link_formatter[species]
                except KeyError:
                    raise ValueError('Species {0} not found in formatter file.'.format(species))
            else:
                # see if that species is in the default dictionary
                species_id = anno_weblinks.species_synonyms.get(species)
                if species_id:
                    link_formatter = anno_weblinks.links[species_id]
                else:
                    raise ValueError('Unknown species {0} (not found in default lookup table').format(species)

        if not ofile:
            ofo = sys.stdout
        else:
            ofo = open(ofile, 'w')
            
        ofo.write(header)

        for sample, e in vcf_iter():
            per_transcript = OrderedDict()
            for eff in snpeff_effects(e):                        
                if (eff.gene_name, eff.transcript_id) in per_transcript:
                    per_transcript[(eff.gene_name, eff.transcript_id)].append(eff)
                else:
                    per_transcript[(eff.gene_name, eff.transcript_id)] = [eff]
            for gene, transcript in per_transcript:
                if oformat == 'html':
                    if link_formatter:
                        # write html with database links
                        ofo.write(line_template.format(sample = sample,
                                                            chromosome = e.chrom,
                                                            position = '<a href={0}>{1}</a>'.format(link_formatter['pos'].format(chromosome = bioobj_base.Chromosome(e.chrom), start = int(e.pos)-500, stop = int(e.pos)+500), e.pos),
                                                            change = '{0}->{1}'.format(e.ref, e.alt),
                                                            gene = gene,
                                                            transcript = '<a href={0}>{1}</a>'.format(link_formatter['gene'].format(gene = gene, transcript = bioobj_base.Transcript(transcript)), transcript),
                                                            effect = ' | '.join(effect.func_class or effect.efftype for effect in per_transcript[(gene, transcript)]),
                                                            genotype = e.sampleinfo['GT'][sample] if e.sampleinfo else '?'
                                                            ))
                    else:
                        # write html without links
                        # while this is not particularly useful, users have a right to get what they asked for
                        ofo.write(line_template.format(sample = sample,
                                                            chromosome = e.chrom,
                                                            position = e.pos,
                                                            change = '{0}->{1}'.format(e.ref, e.alt),
                                                            gene = transcript,
                                                            effect = ' | '.join(effect.func_class or effect.efftype for effect in per_transcript[(gene, transcript)]),
                                                            genotype = e.sampleinfo['GT'][sample] if e.sampleinfo else '?'
                                                            ))

                else:
                    # write tab-separated txt
                    ofo.write('\t'.join((sample,
                                         e.chrom,
                                         str(e.pos),
                                         '{0}->{1}'.format(e.ref, e.alt),
                                         transcript,
                                         ' | '.join(effect.func_class or effect.efftype for effect in per_transcript[(gene, transcript)]),
                                         e.sampleinfo['GT'][sample] if e.sampleinfo else '?', '\n')
                                        ))
        ofo.write(footer)
    finally:
        try:
            if ofo is not sys.stdout:
                ofo.close()
        except:
            pass
        if not snpeff_out:
            try:
                os.remove(outputfile)
            except:
                pass
    
def affected_genes (vcf):
    affected_genes = {}
    for record in vcf:
        snpeffects_by_gene = {}
        for effect in snpeff_effects(record):
            ident = effect.gene_name or (record.chrom, record.pos)
            if ident in snpeffects_by_gene:
                snpeffects_by_gene[ident].append(effect)
            else:
                snpeffects_by_gene[ident] = [effect]
        for gene, effects in snpeffects_by_gene.items():
            partial_record = record.copy()
            effects_string = ','.join(e.verbatim for e in effects if e.verbatim)
            if effects_string:
                partial_record.info['EFF']=effects_string
            else:
                partial_record.info.pop('EFF', None)
            if gene in affected_genes:
                affected_genes[gene].append(partial_record)
            else:
                affected_genes[gene] = [partial_record]
    gene_list = sorted(affected_genes.items(),key=lambda x: (-len(x[1]), x[1][0].chrom, x[1][0].pos))
    
    def records_by_times_affected():
        for gene, records in gene_list:
            for record in records:
                for sample in record.samplenames:
                    if record.sampleinfo['GT'][sample] in ('0/1', '1/1'):
                        yield sample, record
    return records_by_times_affected

SnpEff_Effect = namedtuple('SnpEff_Effect',
                           ['verbatim',
                            'efftype', 'impact', 'func_class',
                            'codon_change', 'aa_change',
                            'aa_len', 'gene_name',
                            'transcript_biotype',
                            'gene_coding', 'transcript_id',
                            'exon', 'genotype_num',
                            'errors', 'warnings'])

def snpeff_effects (vcf_entry):
    """Read out the Eff tag added to the INFO field by SnpEff as a namedtuple."""
    
    if 'EFF' in vcf_entry.info:
        effects = [eff.strip() for eff in vcf_entry.info['EFF'].split(',')]
        for effect in effects:
            try:
                eff_type, details = effect.rstrip(')').split('(')
            except:
                print(effects)
                raise
            eff_details = [d.split(':')[-1] for d in details.split('|')]
            l = len(eff_details)
            if not 11 <= l <= 13:
                raise RuntimeError('Mal-formatted EFF entry in vcf INFO field: {0}'.format(effect))
            if l < 13: #no errors, no warnings
                for i in range(13-l):
                    eff_details.append(None)
            yield SnpEff_Effect(effect, eff_type, *eff_details)
    else:
        yield SnpEff_Effect(*['']*13, errors = None, warnings = None)

def snpeff (genome, inputfile = '-', outputfile = None, memory = None, verbose = False, quiet = True, **optionals):
    """Wrapper around SnpEff.

    Provides a functional interface for subprocess calls of the form:
    java -Xmx<i>g -jar snpEff.jar [options] genome-version variants-file.

    Arguments:
    genome (required): the reference genome version;

    inputfile: path to the input VCF file; default: '-', i.e. stdin
    outputfile: path to outputfile; default: stdout
    snpeff_path: path of the SnpEff installation directory;
                 default: config.snpeff_path

    Optional arguments passed through to SnpEff:
    stats: write an overview of the results to summary-file
           (-stats, default: None)
    memory: GB of memory used (-Xmx<i>g, default: i = config.max_memory)
    chr: prepend 'chr' to chromosome names if True, e.g., 'chr7' instead of '7'
         (-chr, default: False)
    minC: filter out sequence changes with coverage lower than min_cov
          (-minC <i>, default: None (off))
    minQ: filter out sequence changes with quality lower than min_qual
          (-minQ <i>, default: None (off))
    no_downstream: do not show downstream changes if True
                   (-no_downstream, default: False)
    no_upstream: do not show upstream changes if True
                 (-no_upstream, default: False)
    no_intron: do not show intron changes if True
               (-no_intron, default: False)
    ud: set upstream downstream interval length
        (-ud, default: None)
    v: show messages and errors if True (-v, default: False)
    settings currently not modifiable through the interface:
      -o vcf: output format is always vcf
      -t (multithreading) is always switched off"""

    # set snpEff config file and check genome file
    snpeff_path = optionals.get('snpeff_path') or config.snpeff_path
    if not is_installed_snpeff_genome(genome, snpeff_path):
        raise ValueError(
            '{0} is not the name of an installed SnpEff genome.'.format(genome))
    #adjust the memory parameter
    memory = '-Xmx{0}g'.format(memory or config.max_memory)
     
    if not optionals.get('stats'):
        optionals['noStats'] = True
        
    option_table = {'stats':'-stats',
                    'minC':'-minC',
                    'minQ':'-minQ',
                    'ud':'-ud'}

    bool_table = {'chr':'-chr chr',
                  'no_downstream':'-no-downstream',
                  'no_upstream':'-no-upstream',
                  'no_intron':'-no-intron',
                  'no_intergenic':'-no-intergenic',
                  'no_utr':'-no-utr',
                  'v':'-v',
                  'noStats':'-noStats'}

    # build a SnpEff call of the form
    # java -Xmx<i>g -jar snpEff.jar [options] genome-version variants-file

    snpeff_jar = os.path.join(snpeff_path, 'snpEff.jar')
    # build string of switches
    switches = [switch_trans for switch, switch_trans in bool_table.items() if optionals.get(switch)]
    # build options string
    # quote values since some are file names that may contain spaces
    options = ['-c', get_snpeff_config_file(snpeff_path)]
    # see if we are running a new version of SnpEff (v4.1+)
    # that understands the '-formatEff' switch
    test_call = ['java', memory, '-jar', snpeff_jar, '-formatEff'] + options
    proc = subprocess.Popen(test_call, stderr = subprocess.PIPE, universal_newlines = True)
    results, errors = proc.communicate()
    # we always expect an error here, 
    # the question is: is it about the '-formateff' switch ?
    # we have to look at the first line of the error message to find out.
    # in SnpEff 3.6 - 4.0 the first line should read:
    # Error        :	Unknow option '-formatEff'
    assert proc.returncode, 'this version of SnpEff seems to accept rudimentary test options ???'
    if not "option '-formatEff'" in errors.split('\n')[0]:
        # -formatEff seems to be available
        # add it to switches
        switches += ['-formatEff']
    for option, option_trans in option_table.items():
        if option in optionals:
            options += [option_trans, str(optionals[option])]
    # assemble the command line
    # quote file names in case there are spaces in them or their paths
    snpeff_call = ['java', memory, '-jar', snpeff_jar] + \
                  switches + ['-noLog'] + options + \
                  ['-o', 'vcf', genome, inputfile]
    if outputfile:
        stdout_pipe = open(outputfile, 'w')
    else:
        stdout_pipe = None

    # now make the actual call to SnpEff
    if verbose:
        print ('Calling SnpEff with')
        print (' '.join(snpeff_call))

    proc = subprocess.Popen(snpeff_call,
                            stdout = stdout_pipe,
                            stderr = subprocess.PIPE,
                            universal_newlines = True)
    results, errors = proc.communicate()
    if outputfile:
        stdout_pipe.close()
    # check for errors
    if proc.returncode:
        err = []
        for line in errors.split('\n'):
            if line.startswith('snpEff version'):
                break
            err.append(line)
        raise RuntimeError ('snpEff failed with the following error:\n{0}'.format('\n'.join(err)))
    if errors and not quiet:
        # redirect warnings to stdout
        print ('Stderr output from snpEff:')
        print (errors)


def get_snpeff_config_file (snpeff_path = None):
    if snpeff_path is None:
        snpeff_path = config.snpeff_path
    config_file = os.path.join(os.path.expanduser(snpeff_path), 'snpEff.config')
    if not os.path.isfile(config_file):
        raise RuntimeError(
            'Could not get snpEff config file. Check the snpeff_path variable in the MiModD configuration settings.')
    return config_file

def get_snpeff_data_dir (snpeff_path = None):
    if snpeff_path is None:
        snpeff_path = config.snpeff_path    
    config_file = get_snpeff_config_file(snpeff_path)
    with open(config_file) as ifo:
        for line in ifo:
            if line.startswith('data_dir') or line.startswith('data.dir'):
                data_dir = line.split('=')[-1].strip()
                data_dir = os.path.normpath(os.path.join(os.path.expanduser(snpeff_path), os.path.expanduser(data_dir)))
                if not os.path.isdir(data_dir):
                    raise RuntimeError(
                        'Could not find snpEff data directory at location {0} specified in snpEff config file.'.format(data_dir))
                return data_dir
        raise RuntimeError ('snpEff config file at {0} does not specify a data directory.'.format(config_file))

def get_snpeff_config_genomes (snpeff_path = None):
    config_file = get_snpeff_config_file(snpeff_path)
    with open(config_file) as ifo:
        for line in ifo:
            if not line.startswith('#'):
                fields = [e.strip() for e in line.split(':')]
                if len(fields) == 2 and fields[0].endswith('.genome'):
                    yield fields[0][:-len('.genome')], fields[1]

def is_installed_snpeff_genome (query_genome, snpeff_path = None):
    return True if query_genome in (genome for genome, organism in get_snpeff_config_genomes(snpeff_path)) and os.path.isfile(os.path.join(get_snpeff_data_dir (snpeff_path), query_genome, 'snpEffectPredictor.bin')) else False

def get_organism_from_snpeff_genome (query_genome, snpeff_path = None):
    for genome, organism in get_snpeff_config_genomes(snpeff_path):
        if genome == query_genome:
            return organism
    raise KeyError('Genome file {0} not found among the registered SnpEff genomes'.format(query_genome))
        
def get_installed_snpeff_genomes (output = None, snpeff_path = None):
    if output:
        file = open(output, 'w')
    else:
        file = sys.stdout
        
    snpeff_data_dir = get_snpeff_data_dir (snpeff_path)
    for genome, organism in get_snpeff_config_genomes(snpeff_path):
        if os.path.isfile(os.path.join(snpeff_data_dir, genome, 'snpEffectPredictor.bin')):
            print ('{0}: {1}\t{1}'.format(organism, genome), file = file)
    if file is not sys.stdout:
        file.close()
