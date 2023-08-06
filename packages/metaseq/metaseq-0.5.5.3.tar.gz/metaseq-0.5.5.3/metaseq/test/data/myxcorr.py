import scipy
from scipy import signal
import numpy as np
import metaseq
import pybedtools
from matplotlib import pyplot as plt

x = metaseq.genomic_signal(
    'LM09.fastq.clipped.bowtie.bam.filtered.nodups', 'bam')

arr1 = x.local_coverage('chr2L:1-10000000', processes=8, fragment_size=1, read_strand='-')[1]
arr2 = x.local_coverage('chr2L:1-10000000', processes=8, fragment_size=1, read_strand='+')[1]

cc = signal.fftconvolve(arr1, arr2[::-1], mode='full')
center = len(cc)/2
normalized = cc / cc.max()#[center]
xi = np.arange(-center, center + 1)
print xi[np.argmax(normalized)]

plt.plot(xi, normalized)

b, a = signal.butter(3, 0.05)
filtered = signal.filtfilt(b, a, cc)

print xi[np.argmax(filtered)]

plt.plot(xi, filtered/filtered.max())

plt.axis(xmin=0, xmax=500)
plt.show()

# copied from scipy.signal.fftconvolve
"""
s1 = np.array(arr1.shape)
s2 = np.array(arr2.shape)
size = s1 + s2 - 1

# calculate closes power-of-2; fftn() will auto-pad to this size.
fsize = 2 ** np.ceil(np.log2(size))
fslice = tuple([slice(0, int(sz)) for sz in size])
res = np.fftn(arr1, fsize)
res *= np.fftn(arr2, fsize)
"""
