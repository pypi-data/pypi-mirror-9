import metaseq

x = metaseq.genomic_signal(
    metaseq.example_filename('sh_chr2L.bam'), 'bam')

#res = x.local_coverage(['chr2L:60000-70000', 'chr2L:80000-90000'], fragment_size=100, bins=[50, 10], processes=None)
res = x.local_coverage('chr2L:60000-170000', fragment_size=300, bins=100, processes=4)
#res = x.local_coverage(['chr2L:60000-70000', 'chr2L:80000-90000'], fragment_size=300, bins=[50, 1000], processes=None)

x, y = res
plot(x,y, '.-')
show()


