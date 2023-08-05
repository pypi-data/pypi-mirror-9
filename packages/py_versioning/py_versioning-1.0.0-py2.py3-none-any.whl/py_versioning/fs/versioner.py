import json
import sys

def safe_list_get(l, idx, default = None):
    try:
        return l[idx]
    except IndexError:
        return default

class FSVersioner(object):
    def __init__(self, database, engine, versioning_file_path = '.version'):
        self.database = database
        self.engine = engine
        self.versioning_file_path = versioning_file_path
    
    def current_version(self):
        try:
            f = open(self.versioning_file_path, 'r')
            name = f.read()
            f.close()
        except IOError:
            name = '0.0.1'
            self.set_version(name)
        return self.find_version(name)

    
    def actual_version(self):
        hash_, json_ = self.engine.dump_json(pretty = False)
        return ['--ACTUAL--', hash_, json_]
    
    def latest_version(self):
        return self.database.get_latest_version()
        
    def version_list(self):
        current = self.current_version()
        actual = self.actual_version()
        all_ = self.database.get_all_versions()
        if current[1]:
            if current[1] == actual[1]:
                return all_
            return all_ + [actual]
        return [actual]
    
    def changed(self):
        current = self.current_version()
        actual = self.actual_version()
        return current[1] != actual[1]
    
    def outdated(self):
        current = self.current_version()
        latest = self.latest_version()
        return current[1] != latest[1]
    
    def get_version(self, ignore_modified = False, ignore_outdated = False):
        current = self.current_version()
        actual = self.actual_version()
        latest = self.latest_version()
        version = current[0]
        if (not ignore_modified) and current[1] != actual[1]:
            version = '%s+' % version
        if (not ignore_outdated) and current[1] != latest[1]:
            version = '%s^' % version
        return version
        
    def new_version(self, name, hash_, json_):
        self.database.new_version(name, hash_, json_)
        
    def delete_version(self, name):
        r = self.find_version(name)
        self.database.delete_version(name)
        return r
        
    def find_version(self, name = None):
        if name is None:
            return self.current_version()
        if name == '--ACTUAL--':
            return self.actual_version()
        try:
            return self.database.get_version(name)
        except KeyError:
            return ['None', None, '[{}, {}]']
    
    def set_version(self, name):
        f = open(self.versioning_file_path, 'w')
        f.write(name)
        f.close()
    
    def bump_version(self, level = 0):
        current = self.current_version()
        actual = self.actual_version()
        try:
            v2, v1, v0 = map(int, current[0].split('.'))
        except:
            v2, v1, v0 = (0, 0, 0)
        if level == 2:
            v2 += 1
            v1 = 0
            v0 = 0
        elif level == 1:
            v1 += 1
            v0 = 0
        else:
            v0 += 1
        name = '%s.%s.%s' % (v2, v1, v0)
        
        self.new_version(name, actual[1], actual[2])
        self.set_version(name)
        return [name, actual[1], actual[2]]
        
        

class FSVersionCommander(FSVersioner):
    def print_deltas(self, v1_json, v2_json, show_no_change = False):
        v1 = json.loads(v1_json)
        v2 = json.loads(v2_json)
        created, not_changed, changed, deleted = self.engine.compare_dirs(v1, v2)
        for f in created:
            print '+++', f.encode('ascii','replace')
        for f in changed:
            print '@@@', f.encode('ascii','replace')
        for f in deleted:
            print '---', f.encode('ascii','replace')
        if show_no_change:
            for f in not_changed:
                print '===', f.encode('ascii','replace')
    
    def execute_command(self, parts):
        HELP = "Available commands are: current; actual; latest; changed; outdated; list; del <name>; set <name>; bump <level=0>; diff [<name1=None> [<name2=--ACTUAL-->]]."
        if parts == []:
            print HELP
            parts = ['diff']
        
        print "Version:", self.get_version()
        
        cmm = parts[0]
        if cmm == 'current':
            name, hash_, json_ = self.current_version()
            print 'Current: %s [%s]' % (name, hash_)
        elif cmm == 'actual':
            name, hash_, json_ = self.actual_version()
            print 'Actual: %s [%s]' % (name, hash_)
        elif cmm == 'latest':
            name, hash_, json_ = self.latest_version()
            print 'Latest: %s [%s]' % (name, hash_)
        elif cmm == 'changed':
            print "Changed:", self.changed()
        elif cmm == 'outdated':
            print "Outdated:", self.outdated()
        elif cmm == 'list':
            for name, hash_, json_ in self.version_list():
                print '%s [%s]' % (name.ljust(20, ' '), hash_)
#         elif cmm == 'new':
#             name = safe_list_get(parts, 1, None)
#             current = self.current_version()
#             actual = self.actual_version()
#             if current[1] != actual[1]:
#                     self.new_version(name, actual[1], actual[2])
#                     print "Created new version: '%s' : %s." % (name, actual[1])
#             else:
#                 print "Error: No changes detected!"
        elif cmm == 'del':
            name = safe_list_get(parts, 1, '')
            name, hash_, json_ = self.delete_version(name = name)
            print "Deleted version named '%s' : %s." % (name, hash_)
        elif cmm == 'set':
            name = safe_list_get(parts, 1, '')
            name, hash_, json_ = self.find_version(name)
            self.set_version(name)
            print "Set version to %s [%s]" % (name, hash_)
        elif cmm == 'bump':
            try:
                level = int(safe_list_get(parts, 1, '0'))
            except:
                level = 0
            name, hash_, json_ = self.bump_version(level)
            print "Bumped version to %s [%s]" % (name, hash_)
        
        elif cmm == 'diff':
            name1 = safe_list_get(parts, 1, None)
            name2 = safe_list_get(parts, 2, '--ACTUAL--')
            try:
                v1 = self.find_version(name = name1)
                v2 = self.find_version(name = name2)
            except KeyError:
                print "Error: Version named '%s' or '%s' not found!" % (name1, name2)
                return
            print "Comparing '%s' to '%s':" % (v1[0], v2[0])
            self.print_deltas(v1[2], v2[2], '-v' in parts)
        
        else:
            print "Error: '%s' - No such command!" % cmm
            print HELP
                    
                    
                    
    def execute_from_command_line(self):
        self.execute_command(sys.argv[1:])


