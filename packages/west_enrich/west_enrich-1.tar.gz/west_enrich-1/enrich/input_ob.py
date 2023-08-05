'''
Writen by Sean West

INPUT OBJECT
'''
import collections

class Input_ob():
    def __init__(self):
        self.clusters = collections.defaultdict(list)
        self.nodes = []
        return