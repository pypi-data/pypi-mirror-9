from _db import Database

from sqlalchemy import create_engine, text


class SQLDatabase(Database):
    def __init__(self, db_path, table_name):
        self.db_path = db_path
        self.table_name = table_name
        self.engine = create_engine(self.db_path)
    
    def _do_sql(self, sql):
        connection = self.engine.connect()
        result = connection.execute(text(sql))
        return result
    
    def get_all_versions(self):
        sql = "select name, hash, json from %s ORDER BY id" % self.table_name
        r = self._do_sql(sql)
        return map(lambda x: map(lambda y: y.strip(), x), r)
    
    def get_latest_version(self):
        try:
            sql = "select name, hash, json from %s ORDER BY id DESC LIMIT 1" % self.table_name
            r = list(self._do_sql(sql))[0]
            return map(lambda y: y.strip(), r)
        except Exception:
            return ['None', None, '[{}, {}]']

    def get_version(self, name):
        try:
            sql = "select name, hash, json from %s WHERE name='%s' LIMIT 1" % (self.table_name, name)
            r = list(self._do_sql(sql))[0]
            return map(lambda y: y.strip(), r)
        except Exception:
            raise KeyError()
        
    def new_version(self, name, hash_, json_):
        sql = "INSERT INTO %s (name, hash, json, date) VALUES ('%s', '%s', '%s', NOW())" % (self.table_name, name, hash_, json_)
        return self._do_sql(sql)
    
    def delete_version(self, name):
        try:
            sql = "DELETE FROM %s WHERE id IN (SELECT id FROM %s WHERE name='%s' LIMIT 1)" % (self.table_name, self.table_name, name)
            return self._do_sql(sql)
        except Exception:
            raise KeyError()
