import sys

from html.parser import HTMLParser

from . import samheader, pyvcf, pysamtools, fasta

STR_INFO_NOT_PROVIDED = '-- information not provided --'
STR_MISSING = '---'
NOT_KNOWN = None

class ContigInfo (list):
    def __str__ (self):
        if self:
            ret = []
            for contig in self:
                contig_info = []
                contig_info.append(contig['SN'] + ('of ' + contig['SP'] if contig.get('SP') else '') + ':')
                contig_info.append('length / nts:\t' + str(contig.get('LN') or '???'))
                contig_info.append('other information:')
                other_info = [tag + ':\t' + value for tag, value in contig.items() if tag not in ('SN', 'LN')]
                if other_info:
                    contig_info += other_info
                else:
                    contig_info.append(STR_MISSING)
                ret.append('\n'.join(contig_info))
            return '\n\n'.join(ret)
        else:
            return STR_INFO_NOT_PROVIDED

    def as_html (self):
        return str(self).replace('\n', '<br />')

class SampleInfo (list):
    def __str__ (self):
        if self:
            ret = []
            for sample in self:
                sample_info = []
                sample_info.append((sample['SM'] if sample.get('SM') else '???') + (' (ID: ' + sample['ID'] + ')' if sample.get('ID') else '') + ':')
                sample_info.append('description:\t' + (sample.get('DS') or '???'))
                sample_info.append('other information:')
                other_info = [tag + ':\t' + value for tag, value in sample.items() if tag not in ('SM', 'ID', 'DS')]
                if other_info:
                    sample_info += other_info
                else:
                    sample_info.append(STR_MISSING)
                ret.append('\n'.join(sample_info))
            return '\n\n'.join(ret)
        else:
            return STR_MISSING

    def as_html (self):
        return str(self).replace('\n', '<br />')


class ProgramInfo (list):
    def __str__ (self):
        if self:
            ret = []
            for pg in self:
                pg_info = []
                pg_info.append('[' + pg['ID'] + '] ' if pg.get('ID') else '')
                pg_info.append('run on output of [' + pg['PP'] + ']' if pg.get('PP') else '')
                pg_info.append('\n' + pg['PN'] + ' ' if pg.get('PN') else '')
                pg_info.append('(version: ' + pg['VN'] + ')' if pg.get('VN') else '')
                pg_info.append('\nCL: ' + pg['CL'] if pg.get('CL') else '')
                ret.append(''.join(pg_info))
            return '\n\n'.join(ret)
        else:
            return STR_MISSING

    def as_html (self):
        return str(self).replace('\n', '<br />')


class CoInfo (list):
    def __str__ (self):
        if self:
            return '\n'.join(self)
        else:
            return STR_MISSING

    def as_html (self):
        return str(self).replace('\n', '<br />')

    
class NGSInfo (dict):
    @classmethod
    def fromfile (cls, seqfile, fileformat = None):
        if fileformat is None:
            header, fileformat = get_info(seqfile)
            return cls.fromheader(header, fileformat)
        if fileformat == 'fasta':
            header = fasta.get_fasta_info(seqfile)
            return FastaInfo.fromheader(header)
        elif fileformat == 'vcf':
            header = pyvcf.open(seqfile).info
            return VCFInfo.fromheader(header)
        elif fileformat == 'bcf':
            header = pyvcf.open(seqfile, 'rb').info
            return BCF2Info.fromheader(header)            
        elif fileformat == 'sam':
            header = samheader.Header.fromsam(seqfile)
            return SAMInfo.fromheader(header)
        elif fileformat == 'bam':
            header = samheader.Header.frombam(seqfile)
            return BAMInfo.fromheader(header)
        else:
            raise RuntimeError ('Unsupported file format: "{0}"'.format(fileformat))

    @classmethod
    def fromheader (cls, header, fileformat):
        if fileformat == 'vcf':
            return VCFInfo.fromheader(header)
        elif fileformat == 'bcf':
            return BCF2Info.fromheader(header)
        elif fileformat == 'sam':
            return SAMInfo.fromheader(header)
        elif fileformat == 'bam':
            return BAMInfo.fromheader(header)
        elif fileformat == 'fasta':
            return FastaInfo.fromheader(header)
        else:
            raise RuntimeError ('Unsupported file format: "{0}"'.format(fileformat))


class FastaInfo (NGSInfo):
    @classmethod
    def fromheader (cls, info):
        info_dict = {
                    'fileformat': ('Fasta', ''),
                    'reference': None,
                    'source': ProgramInfo([]),
                    'rg': SampleInfo([]),
                    'sq': ContigInfo(info),
                    'co': CoInfo([])
                    }
        return cls(info_dict)

    
class SAMInfo (NGSInfo):
    @classmethod
    def fromheader (cls, info):
        info_dict = {
                    'fileformat': ('SAM', info.get('HD', {'VN': None})['VN']),
                    'reference': None,
                    'source': ProgramInfo(info.get('PG', [])),
                    'rg': SampleInfo(info.get('RG', [])),
                    'sq': ContigInfo(info.get('SQ', [])),
                    'co': CoInfo(info.get('CO', []))
                    }
        return cls(info_dict)
    
    def __init__ (self, info):
        super().__init__(info)
        self['compression'] = None


class BAMInfo (SAMInfo):
    def __init__ (self, info):
        super().__init__(info)
        self['compression'] = 'BAM'


class VCFInfo (NGSInfo):
    @classmethod
    def fromheader (cls, info):
        info_dict = {
                    'fileformat': tuple(info.comments['fileformat'][0].split('v')),
                    'reference' : info.comments.get('reference', [None])[0],
                    'source' : ProgramInfo([{'PN': pg} for pg in info.comments.get('source',[])]),
                    'rg': SampleInfo([{'ID': i.get('ID'), 'SM': rg , 'DS': i.get('Description')} for rg, i in info.rginfo.items()]),
                    'sq': ContigInfo([{'SN': contig , 'LN': info.contigs[contig]} for contig in info.contigs]),
                    'co': CoInfo(info.co)
                    }
        return cls(info_dict)

    def __init__ (self, info):
        super().__init__(info)
        self['compression'] = None


class BCF2Info (VCFInfo):
    def __init__ (self, info):
        super().__init__(info)
        self['compression'] = 'BCF2'

    
def get_info(ifile):
    fformat = None
    try:
        try:
            info = samheader.Header.frombam(ifile)
            fformat = 'bam'
        except RuntimeError:
            try:
                info = samheader.Header.fromsam(ifile)
                fformat = 'sam'
            except RuntimeError:
                try:
                    info = pyvcf.open(ifile).info
                    fformat = 'vcf'
                except (RuntimeError, UnicodeDecodeError):
                    try:
                        info = pyvcf.open(ifile, 'rb').info
                        fformat = 'bcf'
                    except (RuntimeError, UnicodeDecodeError):
                        info = fasta.get_fasta_info(ifile)
                        fformat = 'fasta'
    except (RuntimeError, UnicodeDecodeError):
        raise AssertionError('Do not know how to parse the input file.')

    return info, fformat


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def print_fileinfo (info, ofile, oformat = 'txt'):
    ofo = open(ofile, 'w') if ofile else sys.stdout

    html_template = """<html><body>\
<b>File format:\t{fileformat} {compressed}</b><br />
<hr>
<b>Samples declared in this file:</b><br />
{rginfo}
<hr>
<b>Reference sequence information</b><br />
<br />
<b>Reference genome file:</b><br />
{reference} <br />
<br />
<b>Individual contigs:</b><br />
{contigs}
<hr>
<b>Software used to generate the file:</b><br />
{source}
<hr>
<b>Comments attached to the file:</b><br />
{comments}
</body>
</html>
"""
    txt_template = strip_tags(html_template.
                              replace('<hr>', '\n*****\n'))
    if oformat == 'html':
        ofo.write(html_template.
                  format(fileformat = info['fileformat'][0] + ' ' + info['fileformat'][1],
                         compressed = '(stored as ' + info['compression'] + ')' if info.get('compression') else '',
                         reference = info['reference'] or '-- not provided --',
                         contigs = info['sq'].as_html(),
                         source = info['source'].as_html(),
                         rginfo = info['rg'].as_html(),
                         comments = info['co'].as_html()))
    elif oformat == 'txt':
        ofo.write(txt_template.
                  format(fileformat = info['fileformat'][0] + ' ' + info['fileformat'][1],
                         compressed = '(stored as ' + info['compression'] + ')' if info.get('compression') else '',
                         reference = info['reference'] or '-- not provided --',
                         contigs = info['sq'],
                         source = info['source'],
                         rginfo = info['rg'],
                         comments = info['co']))

def fileinfo(ifile, fformat= None, ofile = None, oformat = 'txt', verbose = False):
    info = NGSInfo.fromfile(ifile, fformat)
    print_fileinfo(info, ofile, oformat)
