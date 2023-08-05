'''
Written by Sean West

Uses hypergeometric distribution function to compare all the clusters to every group in source.
'''
import collections
from scipy.stats import hypergeom

class Stat_compare():
    def __init__(self):
        self.hits = collections.defaultdict(list)
        return
    
    def compare(self, clusters, groupings, allnodes):
        for cid in clusters:
            for gid in groupings:
                pval = self.hyper_geom_compare(clusters[cid], groupings[gid], allnodes)
                if pval <= 0.05:
                    self.hits[cid].append({'csize': len(clusters[cid]), 'gid':gid, 'pval':pval})
        return
                    
    def hyper_geom_compare(self, cluster, group, allnodes):
        common = len(set(cluster).intersection(group))
        g_in_net = len(set(group).intersection(allnodes))
        return hypergeom.sf(common, len(allnodes), g_in_net, len(cluster))