'''
Written by Sean West

This code is the core funtionality of the enrich program.

It:
        obtain inputs
                if 'update' then calls the update_enrichment
        creates enrichment dictionaries by parsing enrichment files:
                source.groupings.txt
                source.group_info.txt
        obtains input clusters
        compares clusters to source groups
        exports results
'''

from enrich import input_handler
from enrich import document_handler
from enrich import source_ob
from enrich import input_ob
from enrich import stat_compare
from enrich import export
from enrich import update_enrichment

import sys
from pkg_resources import resource_filename


class Central_hub():
    def __init__(self):
        return
    
    def main(self):
        # obtain inputs
        ih = input_handler.Input_handler(sys.argv)
        inputs = ih.inputs()
        enrichment = inputs['enrichment']
        input_loc = inputs['input_loc']
        outfile_loc = inputs['output_loc']
        all_nodes = inputs['all_nodes']
        
        # if need to update source files
        if inputs['update']:
            ue = update_enrichment.Update_enrichment()
            ue.update(inputs['update'])
            return
        
        # obtain enrichment dictionaries
        so = source_ob.Source_ob()
        dh = document_handler.Document_handler()
        
        dh.enrichment = enrichment
        dh.e_doc, dh.gi_doc = dh.enrichment_document()
        so.groupings = dh.parse_ed()
        so.group_info = dh.parse_gid()
        
        # obtain input clusters
        io = input_ob.Input_ob()
        io.nodes = dh.parse_nodes(all_nodes)
        io.clusters = dh.parse_id(input_loc)
        
        # stat compare
        sc = stat_compare.Stat_compare()
        sc.compare(groupings=so.groupings, clusters=io.clusters, allnodes=io.nodes)
        
        # export
        ex = export.Export()
        ex.report(sc.hits, so.group_info, outfile_loc)
        
        return
    
def smain():
    ''' Called by runner '''
    stick = Central_hub()
    stick.main()
    return
