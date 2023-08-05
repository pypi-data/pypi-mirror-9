
class Database(object):
    def get_all_versions(self):
        raise NotImplementedError()
    
    def get_latest_version(self):
        raise NotImplementedError()
    
    def get_version(self, name):
        raise NotImplementedError()
    
    def new_version(self, name, hash_, json_):
        raise NotImplementedError()
    
    def delete_version(self, name):
        raise NotImplementedError()

    


