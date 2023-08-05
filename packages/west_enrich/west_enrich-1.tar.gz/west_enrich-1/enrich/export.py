'''
Written by Sean West

Exports results as:
ClusterID    ClusterSize    GroupID    PVal    GroupName
'''

class Export():
    def __init__(self):
        return
    
    def report(self, hits, group_info, outfileloc):
        outfile = open(outfileloc, 'w')
        cid_order = self.most_hits(hits)
        for cid in cid_order:
            for outline in hits[cid]:
                gid = outline['gid']
                outfile.write('\t'.join([str(cid), str(outline['csize']), gid, str(outline['pval']), group_info[gid]['name']]) + '\n')
        outfile.close()        
        return
        
    def most_hits(self, hits):
        cid_numhits = []
        for cid in hits:
            cid_numhits.append((cid,len(hits[cid])))
        cid_numhits = sorted(cid_numhits, key=lambda x: x[1])
        return [x[0] for x in cid_numhits]