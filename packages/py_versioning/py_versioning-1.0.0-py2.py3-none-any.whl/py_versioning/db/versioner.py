import sys

from .engine import CheckVersion, CreateVersion

class DBVersioner(object):
    def __init__(self, versioned_db_path, storage_db_path, table_name):
        self.versioned_db_path = versioned_db_path
        self.storage_db_path = storage_db_path
        self.table_name = table_name
    
    
    def check_version(self):
        return CheckVersion(self.versioned_db_path, self.storage_db_path, self.table_name)
    
    def create_version(self):
        return CreateVersion(self.versioned_db_path, self.storage_db_path, self.table_name)
        
        

class DBVersionCommander(DBVersioner):
    
    def execute_command(self, parts):
        HELP = "Available commands are: check; create."
        if parts == []:
            parts = ['check']
        
        cmm = parts[0]
        if cmm == 'check':
            self.check_version()
        elif cmm == 'create':
            self.create_version()
        
        else:
            print "Error: '%s' - No such command!" % cmm
            print HELP
                    
                    
    def execute_from_command_line(self):
        self.execute_command(sys.argv[1:])


