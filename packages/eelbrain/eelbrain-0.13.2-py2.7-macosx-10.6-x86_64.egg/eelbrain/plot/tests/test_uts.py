'''
Created on Dec 2, 2012

@author: christian
'''
from eelbrain import Factor, datasets, plot, testnd


def test_uts_stat():
    "test plot.UTSStat plotting function"
    ds = datasets.get_uts()
    p = plot.UTSStat('uts', ds=ds, show=False)
    p.close()
    p = plot.UTSStat('uts', 'A%B', ds=ds, show=False)
    p.plot_legend('lower right')
    p.plot_legend(False)
    pl = p.plot_legend('fig')
    p.plot_legend('center')
    pl.close()
    p.close()
    p = plot.UTSStat('uts', 'A', Xax='B', ds=ds, show=False)
    p.close()
    p = plot.UTSStat('uts', 'A%B', 'rm', sub="rm.isin(('R00', 'R01'))", ds=ds,
                     show=False)
    p.close()
    p = plot.UTSStat('uts', 'A%B', 'rm', sub="rm.isin(('R00', 'R01'))", ds=ds,
                     pool_error=False, show=False)
    p.close()

    # clusters
    sds = ds.sub("B == 'b0'")
    res = testnd.ttest_rel('uts', 'A', 'a1', 'a0', match='rm', ds=sds,
                           samples=0, pmin=0.05, mintime=0.02)
    p = plot.UTSStat('uts', 'A', ds=ds, show=False)
    p.set_clusters(res.clusters)
    p.close()
    p = plot.UTSStat('uts', 'A', ds=ds, clusters=res.clusters, show=False)
    p.close()
    res = testnd.ttest_rel('uts', 'A', 'a1', 'a0', match='rm', ds=sds,
                           samples=100, pmin=0.05, mintime=0.02)
    p = plot.UTSStat('uts', 'A', ds=ds, clusters=res.clusters, show=False)
    p.close()
    p = plot.UTSStat('uts', 'A', 'B', ds=ds, clusters=res.clusters, show=False)
    p.set_clusters(None)
    p.set_clusters(res.clusters, ax=0)
    p.close()
    p = plot.UTSStat('uts', 'A', 'B', ds=ds, show=False)
    p.set_clusters(res.clusters)
    p.set_clusters(None, ax=1)
    p.close()


def test_uts():
    "test plot.UTS plotting function"
    ds = datasets.get_uts()
    p = plot.UTS('uts', ds=ds, show=False)
    p.close()
    p = plot.UTS('uts', 'A%B', ds=ds, show=False)
    p.close()


def test_clusters():
    "test plot.uts cluster plotting functions"
    ds = datasets.get_uts()

    A = ds['A']
    B = ds['B']
    Y = ds['uts']

    # fixed effects model
    res = testnd.anova(Y, A * B)
    p = plot.UTSClusters(res, title="Fixed Effects Model", show=False)
    p.close()

    # random effects model:
    subject = Factor(range(15), tile=4, random=True, name='subject')
    res = testnd.anova(Y, A * B * subject, samples=2)
    p = plot.UTSClusters(res, title="Random Effects Model", show=False)
    p.close()

    # plot UTSStat
    p = plot.UTSStat(Y, A % B, match=subject, show=False)
    p.set_clusters(res.clusters)
    p.close()
    p = plot.UTSStat(Y, A, Xax=B, match=subject, show=False)
    p.close()
