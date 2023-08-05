import sys


class CombinedCommander(object):
    def __init__(self, **commanders):
        self.commanders = commanders
        
    def execute_command(self, parts):
        HELP = "Available commands are: %s." % ('; '.join(self.commanders.keys()))
        if parts == []:
            print "Error: Need to supply command!"
            print HELP
            return
        
        cmm = parts[0]
        if self.commanders.has_key(cmm):
            self.commanders[cmm].execute_command(parts[1:])
        else:
            print "Error: '%s' - No such command!" % cmm
            print HELP
                    
                    
    def execute_from_command_line(self):
        self.execute_command(sys.argv[1:])


