import os
import re
import json
import hashlib


def md5(data):
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()

def md5_file(f, block_size = 2**10):
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    return md5.hexdigest()


class FSVersionerEngine(object):
    def __init__(self, path, ignore_empty_folders = True, allow_regs = [r'^.*$'], ignore_regs = []):
        self.path = unicode(path)
        self.ignore_empty_folders = ignore_empty_folders
        self.allow_regs = allow_regs
        self.ignore_regs = ignore_regs

    def process_folder(self, path, name = u'.'):
        path = unicode(path)
        all_dirs, all_files = self.get_dirs_files(path)
        dirs = {}
        files = {}
        for dir_name in all_dirs:
            dir = self.process_folder(os.path.join(path, dir_name), dir_name)
            if dir:
                dirs[dir_name] = dir
        for file_name in all_files:
            files[file_name] = self.hash_file(os.path.join(path, file_name))
        if self.ignore_empty_folders and (not files) and (not dirs):
            return None
        #print path, dirs
        return [dirs, files]
    
    def file_ok(self, path):
        for reg in self.allow_regs:
            if re.match(reg, path):
                for reg2 in self.ignore_regs:
                    if re.match(reg2, path):
                        return False
                return True
        return False
    
    def get_dirs_files(self, path):
        _, all_dirs, all_files = os.walk(path).next()
        files = []
        for f in all_files:
            fp = u".\\%s" % os.path.relpath(os.path.join(path, f), self.path)
            if self.file_ok(fp):
                files.append(f)
        return all_dirs, files
    
    def hash_file(self, path):
        f = open(path, 'rb')
        r = md5_file(f, 2**12)
        f.close()
        return r
    
    def dump_json(self, pretty = False):
        data = self.process_folder(self.path)
        json_ = json.dumps(data, sort_keys = True, separators=(',', ':'))
        hash_ = md5(json_)
        if pretty:
            json_p = json.dumps(data, sort_keys = True, indent = 2, separators=(',', ': '))
            return hash_, json_p
        return hash_, json_
    
    
    def compare_files(self, files1, files2):
        created = []
        not_changed = []
        changed = []
        deleted = []
        for filename, hash_ in files2.iteritems():
            if files1.has_key(filename):
                if files1[filename] == hash_:
                    not_changed.append(filename)
                else:
                    changed.append(filename)
            else:
                created.append(filename)
        
        for filename, hash_ in files1.iteritems():
            if not files2.has_key(filename):
                deleted.append(filename)
                
        return created, not_changed, changed, deleted
    
    def compare_dirs(self, dir1, dir2, path = u'.'):
        created = []
        not_changed = []
        changed = []
        deleted = []
        
        for dir_name, rdir1 in dir1[0].iteritems():
            rdir2 = dir2[0].get(dir_name, [{}, {}])
            cr, nc, ch, dl = self.compare_dirs(rdir1, rdir2, os.path.join(path, dir_name))
            created.extend(cr)
            not_changed.extend(nc)
            changed.extend(ch)
            deleted.extend(dl)
        
        cr, nc, ch, dl = self.compare_files(dir1[1], dir2[1])
        created.extend(map(lambda x: os.path.join(path, x), cr))
        not_changed.extend(map(lambda x: os.path.join(path, x), nc))
        changed.extend(map(lambda x: os.path.join(path, x), ch))
        deleted.extend(map(lambda x: os.path.join(path, x), dl))
        
        return created, not_changed, changed, deleted 
    
    

