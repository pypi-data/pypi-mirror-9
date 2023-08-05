'''
Written by Sean West

Inputs:
    enrichment       enrichment type location = 'go', 'kegg', 'omim'
    input_loc        cluster file location
    output_loc       output file location
    all_nodes        file with all nodes in network
    update           which type of enrichment to update = 'go', 'kegg', 'omim'
'''
import getopt
import os

class Input_handler():
    def __init__(self, args):
        self.args = self.opts(args[1:])
        return
    
    def inputs(self):
        all_inputs = {}
        all_inputs['enrichment'] = self.args['e']
        all_inputs['input_loc'] = self.args['i']
        all_inputs['output_loc'] = self.args['o']
        all_inputs['all_nodes'] = self.args['n']
        all_inputs['update'] = self.args['u']
        return all_inputs
    
    def opts(self, options):
        shortops = 'e:i:o:n:u:'
        longops = ['enrichment=', 'input=', 'output=', 'nodes=', 'update=']
        opts = getopt.getopt(options, shortops, longops)
        
        args = {'e':'', 'i':'', 'o':'', 'n':'', 'u':''}
        for (opt, arg) in opts[0]:
            if opt == '-e' or opt == '--enrichment':
                args['e'] = arg
            elif opt == '-i' or opt == '--input':
                args['i'] = arg
            elif opt == '-o' or opt == '--output':
                args['o'] = arg
            elif opt == '-n' or opt == '--nodes':
                args['n'] = arg
            elif opt == '-u' or opt == '--update':
                args['u'] = arg
        return args

