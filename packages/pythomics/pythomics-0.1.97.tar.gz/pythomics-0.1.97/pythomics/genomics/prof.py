from collections import OrderedDict
# @profile
def parse_entry(entry):
    """This parses a VCF row and stores the relevant information"""
    entry = entry.split('\t')
    chrom, pos, id, ref, alt_, qual, filter_, info_, format = entry[:9]
    samples = entry[9:]
    n_individuals = len(samples)
    phase = {}
    genotype = {}
    genome_quality = []
    depth = []
    individuals = {}
    gfilter = ""
    alt = None
    GT = -1
    GQ = -1
    DP = -1
    FT = -1
    ploidy = 2
    alt = alt_.split(',')
    if filter_ == 'PASS' or filter_ == '.':
        passed = True
    else:
        passed = filter_.split(';')
    if info_ != '.':
        info_l = info_.split(';')
        info = [v.split('=') if '=' in v else (v,1) for v in info_l]
    format = format.split(':')
    if 'GT' in format:
        GT = format.index('GT')
    if 'GQ' in format:
        GQ = format.index('GQ')
    if 'DP' in format:
        DP = format.index('DP')
    if 'FT' in format:
        FT = format.index('FT')
    #on to the samples

    extra_sample_info = {}
    for individual, sample in enumerate(samples):
        for info_n, sample_info in enumerate(sample.split(':')):
            if info_n == GT:
                if len(sample_info) == 3 and ('|' in sample_info or '/' in sample_info):
                    genotype[individual] = sample_info
            elif info_n == GQ:
                if not sample_info:
                    genome_quality[individual] = None
                elif sample_info == '.':
                    sample_info = -1
                else:
                    sample_info = int(sample_info)
                if sample_info > 99:
                    sample_info = 99
                genome_quality[individual] = sample_info
        # elif info_n == DP:
        #     if not sample_info or sample_info == '.':
        #         depth[n] = -1
        #     else:
        #         depth[n] = int(sample_info)
        # elif info_n == FT:
        #     #not supported, I haven't encountered this yet
        #     pass
        # else:
        #     try:
        #         extra_sample_info[n][info_n] = sample_info
        #     except KeyError:
        #         extra_sample_info[n] = {info_n: sample_info}

for row in open('/home/chris/ref/human/1000G/text_prof.vcf'):
    if row.startswith('#'):
        continue
    parse_entry(row)