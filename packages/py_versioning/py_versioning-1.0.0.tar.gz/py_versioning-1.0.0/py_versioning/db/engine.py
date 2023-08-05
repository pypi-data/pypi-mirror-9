from sqlalchemy import create_engine, text, MetaData
from sqlalchemy import inspect

import json


class CreateVersion():
    def __init__(self, versioned_db_path, storage_db_path, table_name):
        self.path1 = versioned_db_path  # self.get_ini("DB", "path1")
        self.path2 = storage_db_path  # self.get_ini("DB", "path4")
        self.table_name = table_name
        self.create_engine()
        last_version = self.get_latest_version()
        if last_version:
            new_list = self.get_table_list()
            new_json = json.dumps(new_list)
            old_list = eval(last_version[3])
            if last_version['json_db'] == new_json:
                print 'No changes detected in db!'
                print 'path: %s' % self.path1
            else:
                column, row = self.compareVersion(new_list, old_list)
                new_version = last_version[1].split('.')
                if len(column) > 0:
                    new_version[0] = str(int(new_version[0]) + 1)
                    new_version[1] = str(0)
                else:
                    new_version[1] = str(int(new_version[1]) + 1)
                new_version_str = new_version[0] + '.' + new_version[1]
                if column:
                    print 'Change tables'
                for c in column:
                    print c
                if row:
                    print 'Change columns'
                for r in row:
                    print r

                self.insert_new_version(new_json, new_version_str)
                print 'Created new db version %s' % new_version_str
        else:
            self.create_new_version()
            print 'Version 0.0 was created.'


    def compareVersion(self, olds, news):
        diff_tables = []
        diff_columns = []
        for new in news:
            for i, jj in new.items():
                nn = self.find_in_list_with_dic(olds, i)
                if nn:
                    for n in nn:
                        if not n in jj:
                            diff_columns.append(('+++', unicode(i), n))
                    for j in jj:
                        if not j in nn:
                            diff_columns.append(('---', unicode(i), j))
                else:
                    diff_tables.append(('---', new))

        for old in olds:
            for i, jj in old.items():
                nn = self.find_in_list_with_dic(news, i)
                if nn:
                    pass
                else:
                    diff_tables.append(('+++', old))

        dt = []
        dc = []
        for t in diff_tables:
            if not t in dt:
                dt.append(t)
        for c in diff_columns:
            if not c in dt:
                dc.append(c)
        return dt, dc


    def find_in_list_with_dic(self, elements_dic, element):
        for e in elements_dic:
            for i, j in e.items():
                if i == element:
                    return e[i]
                    return True
        return False

    def create_engine(self):
        self.engine = create_engine(self.path1)
        self.engine2 = create_engine(self.path2)

    def do_sql(self, q):
        connection = self.engine.connect()
        result = connection.execute(text(q))
        return result

    def do_sql2(self, q):
        connection = self.engine2.connect()
        result = connection.execute(text(q))
        return result

    def get_versions(self):
        q = "select id, version, date, json_db from control ORDER BY id"

        return self.do_sql2(q)

    def get_latest_version(self):
        row = self.get_versions()
        latest = []
        for r in row:
            latest = r
        if latest:
            return latest
        else:
            return False

    def create_new_version(self, new_json=False):
        if not new_json:
            aaa = self.get_table_list()
            json_db = json.dumps(aaa)
            version = '0.1'
        self.insert_new_version(json_db, version)


    def insert_new_version(self, json_db, version):
        q = """INSERT INTO %s 
                (version, date ,json_db ) VALUES 
                ('%s', NOW(), '%s')""" % (self.table_name, version, json_db)
        self.do_sql2(q)


    def get_table_list(self):
        inspector = inspect(self.engine)

        table_list = []
        for table_name in inspector.get_table_names():
            table_dic = {}
            columns = []

            for column in inspector.get_columns(table_name):
                columns.append(column['name'])
            det_str = table_name + '_details'
            details = self.get_details(table_name)

            table_dic[det_str] = details
            table_dic[table_name] = columns
            table_list.append(table_dic)

        return table_list

    def get_details(self, name):
        meta = MetaData()
        meta.bind = self.engine
        meta.reflect()
        datatable = meta.tables[name]
        return [str(c.type) for c in datatable.columns]


class CheckVersion():
    def __init__(self, versioned_db_path, storage_db_path, table_name):
        self.path1 = versioned_db_path  # self.get_ini("DB", "path1")
        self.path2 = storage_db_path  # self.get_ini("DB", "path4")
        self.table_name = table_name

        self.create_engines()
        versions = self.get_versions()
        aaa = self.get_table_list()
        my_json = json.dumps(aaa)

        for v in versions:

            if v[3] == my_json:
                ver = str(self.path1).split('/')
                print 'Version %s:' % (str(ver[-1])), v[1]
                break


    def create_engines(self):
        self.engine = create_engine(self.path1)
        self.engine2 = create_engine(self.path2)

    def do_sql(self, q):
        connection = self.engine.connect()
        result = connection.execute(text(q))
        return result

    def do_sql2(self, q):
        connection = self.engine2.connect()
        result = connection.execute(text(q))
        return result

    def get_versions(self):

        q = "select id, version, date, json_db from control ORDER BY -id"

        return self.do_sql2(q)

    def get_table_list(self):
        inspector = inspect(self.engine)
        table_list = []
        for table_name in inspector.get_table_names():
            table_dic = {}
            columns = []

            for column in inspector.get_columns(table_name):
                columns.append(column['name'])
            det_str = table_name + '_details'
            details = self.get_details(table_name)
            table_dic[det_str] = details
            table_dic[table_name] = columns
            table_list.append(table_dic)
        return table_list

    def get_details(self, name):
        meta = MetaData()
        meta.bind = self.engine
        meta.reflect()
        datatable = meta.tables[name]

        return [str(c.type) for c in datatable.columns]

# create = CreateVersion()
#heck = CheckVersion()
#db = DataBase(2)
