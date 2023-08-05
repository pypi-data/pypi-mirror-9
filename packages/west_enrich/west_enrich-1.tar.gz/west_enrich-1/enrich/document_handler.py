'''
Written by Sean West

Sets location for enrichment document in:
    enrichment_document
Parses:
    enrichment document       parse_ed
    input document            parse_id
    group info file           parse_gid
    node list file            parse_nodes
'''
import collections
import enrich


class Document_handler():
    def __init__(self):
        self.enrichment = ''
        self.e_doc = ''
        self.gi_doc = ''
        return
    
    def enrichment_document(self):
        path = (enrich.__file__).replace('__init__.py', '')
        eloc, dloc = ['','']
        if self.enrichment in ['GO', 'gene_ontology', 'geneontology', 'go']:
            eloc = path + 'docs/gene_ontology.groupings.txt'
            dloc = path + 'docs/gene_ontology.group_info.txt'
        elif self.enrichment in ['KEGG', 'kegg']:
            eloc = path +  'docs/kegg.groupings.txt'
            dloc = path + 'docs/kegg.group_info.txt'
        elif self.enrichment in ['OMIM', 'omim']:
            eloc = path + 'docs/omim.groupings.txt'
            dloc = path + 'docs/kegg.group_info.txt'
        return eloc, dloc
            
    def parse_ed(self):
        dic = collections.defaultdict(list)
        with open(self.e_doc) as ed:
            for line in ed:
                line = line.replace('\n', '')
                line = line.split('\t')
                first = line.pop(0)
                dic[first] = line
        return dic
    
    def parse_id(self, i_doc):
        clusters = collections.defaultdict(list)
        with open(i_doc) as id:
            i = 1
            for line in id:
                line = line.replace('\n', '')
                line = line.split('\t')
                clusters[i] = line
                i += 1
        return clusters
    
    def parse_gid(self):
        group_info = collections.defaultdict(dict)
        with open(self.gi_doc) as gd:
            for line in gd:
                line = line.replace('\n', '')
                line = line.split('\t')
                group_info[line[0]]['name'] = line[1]
        return group_info
    
    def parse_nodes(self, location):
        allnodes = []
        with open(location) as an:
            for line in an:
                allnodes.append(line.replace('\n', ''))
        return allnodes