import metaseq
import pybedtools

tsses = pybedtools.BedTool('g.bed')
#input = metaseq.genomic_signal('t.bed', 'bed')
input = metaseq.genomic_signal('t.bam', 'bam')
data = input.array(tsses, bins=100, processes=8)
