species_synonyms = {
                    # Worm
                    '6239' : 6239,
                    'Caenorhabditis elegans' : 6239,
                    'C. elegans' : 6239,
                    'C.elegans' : 6239,

                    # Yeast
                    '1196866' : 1196866,
                    'Saccharomyces cerevisiae' : 1196866,
                    'S. cerevisiae' : 1196866,
                    'S.cerevisiae' : 1196866,

                    # Synechocystis
                    '1148' : 1148,
                    'Synechocystis sp. PCC 6803' : 1148,
                    'Synechocystis PCC 6803' : 1148,
                    'Synechocystis' : 1148,
                    'PCC 6803' : 1148,

                    # Fly
                    '7227' : 7227,
                    'Drosophila melanogaster' : 7227,
                    'D. melanogaster' : 7227,
                    'D.melanogaster' : 7227,

                    # Zebrafish
                    '7955' : 7955,
                    'Danio rerio' : 7955,
                    'D. rerio' : 7955,
                    'D.rerio' : 7955,
                    'Brachydanio rerio' : 7955,
                    # Arabidopsis
                    '3702' : 3702,
                    'Arabidopsis thaliana' : 3702,
                    'A. thaliana' : 3702,
                    'A.thaliana' : 3702
                    }
links = {
        # Worm
        6239 :
            {
            'gene' : 'http://www.wormbase.org/species/c_elegans/gene/{gene}',
            'pos'  : 'http://www.wormbase.org/tools/genome/gbrowse/c_elegans_PRJNA13758?name={chromosome.barename}:{start}..{stop}'
            },
        # Yeast
        1196866 :
            {
            'gene' : 'http://www.yeastgenome.org/cgi-bin/locus.fpl?locus={gene}',
            'pos'  : 'http://browse.yeastgenome.org/fgb2/gbrowse/scgenome/?name={chromosome.barename}:{start}..{stop}'
            },
        # Synechocystis
        1148 :
            {
            'gene' : 'http://genome.microbedb.jp/cyanobase/Synechocystis/genes/search?q={gene}&keyword=search&m=gene_symbol%2Cgi_gname%2Cdefinition%2Cgi_pname',
            'pos'  : 'http://genome.microbedb.jp/cgi-bin/gbrowse/Synechocystis/?name={chromosome.barename}:{start}..{stop}'
            },
        # Fly
        7227 :
            {
            'gene' : 'http://flybase.org/reports/{transcript}.html',
            'pos'  : 'http://flybase.org/cgi-bin/gbrowse2/dmel/?name={chromosome.barename}:{start}..{stop}'
            },
        # Zebrafish
        7955 :
            {
            'gene' : 'http://www.ensembl.org/Danio_rerio/Gene/Matches?db=core;t={transcript}',
            'pos'  : 'http://zfin.org/gb2/gbrowse/zfin_ensembl/?name={chromosome.barename}:{start}..{stop}'
            },
        # Arabidopsis
        3702 :
            {
            'gene' : 'http://www.arabidopsis.org/servlets/TairObject?name={transcript.basename}&type=locus',
            'pos'  : 'http://tairvm17.tacc.utexas.edu/cgi-bin/gb2/gbrowse/arabidopsis/?name={chromosome.shortname}:{start}..{stop}'
            }
        }
