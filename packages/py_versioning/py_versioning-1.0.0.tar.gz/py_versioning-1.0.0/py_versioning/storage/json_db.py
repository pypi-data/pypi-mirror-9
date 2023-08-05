from _db import Database

import json


class FileJsonDatabase(Database):
    def __init__(self, file_name):
        self.file_name = file_name
        self.data = self._load(self.file_name)
    
    def _load(self, file_name):
        try:
            f = open(file_name, 'r')
        except IOError:
            self._init_db(file_name)
            f = open(file_name, 'r')
        data = json.load(f)
        f.close()
        return data
    
    def _init_db(self, file_name):
        self._dump(file_name, [])
        
    def _dump(self, file_name, data):
        f = open(file_name, 'w')
        json.dump(data, f, separators = (',', ':'), indent = 0)
        f.close()
        
    def save(self):
        self._dump(self.file_name, self.data)
    
    
    def get_all_versions(self):
        return self.data
    
    def get_latest_version(self):
        try:
            return self.data[-1]
        except IndexError:
            return ['None', None, '[{}, {}]']
    
    def get_version(self, name):
        for name_, hash_, json_ in self.data:
            if name_ == name:
                return [name_, hash_, json_]
        raise KeyError()
    
    def new_version(self, name, hash_, json_):
        self.data.append([name, hash_, json_])
        self.save()
    
    def delete_version(self, name):
        for i, data in enumerate(self.data):
            if data[0] == name:
                d = self.data.pop(i)
                self.save()
                return d
        raise KeyError()
            