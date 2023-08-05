'''
Written by Sean West

SOURCE OBJECT
'''
import collections

class Source_ob():
    def __init__(self):
        self.groupings = collections.defaultdict(list)
        self.group_info = collections.defaultdict(dict)
        return