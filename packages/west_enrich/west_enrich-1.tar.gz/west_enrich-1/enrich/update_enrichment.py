import enrich
import subprocess
import gzip
import collections
import sys
import enrich.all_exceptions as aex


class Update_enrichment():
    def __init__(self):
        return
    
    def update(self, source):
        path = (enrich.__file__).replace('__init__.py', '')
        subprocess.call(['mkdir', path+'docs'])
        
        if source in ['go', 'gene_ontology', 'geneontology', 'go']:
            self.gene_ontology(path)
        if source in ['KEGG', 'kegg']:
            self.kegg(path)
        if source in ['OMIM', 'omim']:
            self.omim(path)
        if source in ['all', 'a', 'ALL', 'All']:
            self.gene_ontology(path)
            self.kegg(path)
            self.omim(path)
        return
    
    def gene_ontology(self, path):
        # retrieve source file
        sys.stdout.write('Retrieving Gene Ontology source file...\n\n')
        subprocess.call(['wget', 'ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene2go.gz'])
        gzfile = gzip.open('gene2go.gz', 'rb')
        gf = gzfile.read()
        gzfile.close()
        txtfile = open('gene2go', 'wb')
        txtfile.write(gf)
        txtfile.close()
        subprocess.call(['rm', 'gene2go.gz'])
        sys.stdout.write('Retrieving Gene Ontology source file...success\n')
        
        # parsing the source file
        sys.stdout.write('Parsing source file...')
        groupings = collections.defaultdict(list)
        groupinfo = collections.defaultdict(dict)
        infile = open('gene2go', 'r')
        infile.readline()
        for line in infile:
            line = line.replace('\n', '')
            tax_id, GeneID, GO_ID, Evidence, Qualifier, GO_term, PubMed, Category = line.split('\t')
            if tax_id == '9606':
                groupings[GO_ID].append(GeneID)
                if GO_ID not in groupinfo:
                    groupinfo[GO_ID]['name'] = GO_term
                    groupinfo[GO_ID]['category'] = Category
                    groupinfo[GO_ID]['taxid'] = tax_id
        subprocess.call(['rm', 'gene2go'])  
        sys.stdout.write('success\n')  
                
        # export to ouput files        
        sys.stdout.write('Exporting data files...')
        groupings_file = open(path+'docs/gene_ontology.groupings.txt', 'w')
        for go_id in groupings:
            groupings_file.write(go_id + '\t' + '\t'.join(groupings[go_id]) + '\n')
        groupings_file.close()
        
        groupinfo_file = open(path+'docs/gene_ontology.group_info.txt', 'w')
        for go_id in groupinfo:
            groupinfo_file.write('\t'.join([go_id, groupinfo[go_id]['taxid'], groupinfo[go_id]['name'], groupinfo[go_id]['category']]) + '\n')
        groupinfo_file.close()
        sys.stdout.write('success\n\n')
        return
    
    def kegg(self, path):
        sys.stdout.write('\nWe dont have KEGG\n\n')
        return
    
    def omim(self, path):
        try:
            mim2gene = open('mim2gene.txt', 'r')
            genemap2 = open('genemap2.txt', 'r')
        except:
            nomim = aex.NoOmimFile()
            sys.stdout.write(nomim.message)
            return
        
        # creating OMIM to GeneID reference
        sys.stdout.write('\nCreating OMIM to GeneID reference...')
        omim2geneid = {}
        mim2gene.readline()
        for line in mim2gene:
            line = line.split('\t')
            omim2geneid[line[0]] = line[2]
        mim2gene.close()
        sys.stdout.write('success\n')
        
        # creating omim groups
        sys.stdout.write('Parsing genemap2...')
        groupings = collections.defaultdict(list)
        groupinfo = collections.defaultdict(dict)
        for line in genemap2:
            line = line.replace('\n', '')
            line = line.split('|')
            gomim = line[8]
            disease_string = line[11]
            geneid = omim2geneid[gomim]

            domims = []
            if disease_string and disease_string != ' ' and geneid:
                disease_list = disease_string.split(';')
                for disease in disease_list:
                    disease_omim = ((disease.split(',')[-1]).split('(')[0]).replace(' ', '')
                    if not disease_omim:
                        disease_omim = ((disease.split(',')[-2]).split('(')[0]).replace(' ', '')
                    try:
                        int(disease_omim)
                    except: 
                        break
                    if len(disease_omim) != 6:
                        break
                    domims.append(disease_omim)
                    if disease_omim not in groupinfo:
                        groupinfo[disease_omim]['name'] = disease.strip()
                for domim in domims:
                    if geneid not in groupings[domim] and geneid != '-':
                        groupings[domim].append(geneid)
        sys.stdout.write('success\n')

        # export files        
        sys.stdout.write('Exporting data files...')
        groupings_file = open(path+'docs/omim.groupings.txt', 'w')
        for go_id in groupings:
            groupings_file.write(go_id + '\t' + '\t'.join(groupings[go_id]) + '\n')
        groupings_file.close()
        
        groupinfo_file = open(path+'docs/omim.group_info.txt', 'w')
        for go_id in groupinfo:
            groupinfo_file.write('\t'.join([go_id, '9606', groupinfo[go_id]['name'], '-']) + '\n')
        groupinfo_file.close()
        sys.stdout.write('success\n\n')
        
        return
    
    

        