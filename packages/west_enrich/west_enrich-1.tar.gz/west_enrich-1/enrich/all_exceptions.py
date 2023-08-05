'''
Written by Sean West

User Defined Exceptions
'''


# update_enrichment
class UE_exception(Exception):
    def __init__(self):
        return
    
class NoOmimFile(UE_exception):
    def __init__(self):
        self.message = '\nOMIM does not let their files be automatically downloaded\n'
        self.message += 'Go to "www.omim.org/downloads" to request ftp access.\n'
        self.message += 'Then place these files in the cwd and rerun the update command:\n'
        self.message += '\tmim2gene.txt\n\tgenemap2.txt\n\n'