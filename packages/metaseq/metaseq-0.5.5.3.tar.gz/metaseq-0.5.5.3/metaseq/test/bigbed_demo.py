from metaseq.results_table import DESeqResults
from pybedtools.contrib.bigbed import bigbed

d = DESeqResults('data/rrp40-s2-polyA.final.summary', dbfn='data/dmel-all-r5.33-cleaned.gff.db')

d = d[:100]

x = d.colormapped_bedfile()
asql = d.autosql_file()

output = bigbed(x, 'dm3', 'test.bb', _as=asql, bedtype='bed9+5')
