from metaseq import genomic_signal
import pybedtools
import numpy as np
try:
    del a
except NameError:
    pass
features = pybedtools.BedTool(pybedtools.BedTool('chr17.exons'))#.saveas()
gs = genomic_signal('data/wgEncodeHaibTfbsK562Atf3V0416101RawRep1_chr17.bigWig', 'bigwig')
a = gs.array(features, bins=100, processes=8, chunksize=250)
