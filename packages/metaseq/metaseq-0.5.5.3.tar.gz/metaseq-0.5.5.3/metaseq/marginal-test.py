import numpy as np
from matplotlib import pyplot as plt
import pandas
from matplotlib.transforms import blended_transform_factory
from matplotlib.collections import EventCollection
from metaseq.results_table import DESeqResults
from marginalhists import MarginalHistScatter
import matplotlib
matplotlib.rcParams['font.size'] = 10
d = DESeqResults('kc_shep-rb5.htseq_exon.deseq.results')
d.data['rpkm'] = d.data['baseMeanA'] / d.data['exonic']
d.scatter(
    'length', 'rpkm', xfunc=np.log1p, yfunc=np.log1p,
    genes_to_highlight=[
        (d.enriched(), dict(color='r',label='enriched', marginal_histograms=False, alpha=0.5), ) ,
    ],
    general_hist_kwargs=dict(bins=50, linewidth=0, log=True),
    marginal_histograms=True,
)

plt.show()
