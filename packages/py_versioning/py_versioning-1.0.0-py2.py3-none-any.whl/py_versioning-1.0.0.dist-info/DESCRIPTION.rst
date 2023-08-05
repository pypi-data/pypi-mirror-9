# Versioning
Set of tools helping in versioning projects

---- ENGLISH ----
PyVersioning
Required
python 2.7
SQLAlchemy 

How it works?
This program can create and manage version of databases and  file system.

In file example.py you must set:
Engine with path to versioned project, flag to ignore empty folders, list of regular expressions for files to include and exclude
  fs_engine = FSVersionerEngine(PROJECT, True, [r'^.*py$'], [r'^.*\\storage\\.*$',])
Database and table, where program keeps data about file system, f.e:
  fs_database = SQLDatabase('postgresql://postgres:postgres@localhost/versioning', 'fs_version')
Versioner manager with database, engine and path to file with version information
  fs_versioner = FSVersionCommander(fs_database, fs_engine, '.version')


command: python example.py fs list
action: Shows list of file system versions

command: python example.py fs current/actual/latest
action: Shows details about current/actual/latest file system version

command: python example.py fs changed/outdated
action: Checks if file system was changed / is outdated

command: python example.py fs del <name>
action: Deletes file system version with <name> from database

command: python example.py fs set <name>
action: Manually sets file system version [version with name <name> must exist]

command: python example.py fs bump [<level=0>]
action: Creates new file system version, raising number depending on actual and <level> [bump 0: 1.2.3 -> 1.2.4; bump 2: 1.2.3 -> 2.0.0]

command: python example.py fs diff [<name1=None> [<name2=--ACTUAL-->]]
action: Shows changes between versions with names <name1> and <name2>


Database, which we want to versioning and db, where program keeps data about versionised fb, f.e: 
db_versioner = DBVersionCommander('postgresql://postgres:postgres@localhost/vers_test3', 'postgresql://postgres:postgres@localhost/vers_control')

command: python example.py db, python example.py db check
action: Check version db. 

command: python example.py db create
action: Create new version db, if changes will be detected.

---- POLSKI ----
PyVersioning
Wymagania: 
python 2.7
SQLAlchemy 

Działanie:
Program pozwala na wersjonowanie schematów baz danych oraz systemu plików. 

W pliku example.py należy odpowiednie ścieżki:
Silnik wraz ze ścieżką do versionowanego projektu, flagą ignorującą puste foldery, listę wyrażeń regularnych by zawrzeć/wykluczyć pliki 
  fs_engine = FSVersionerEngine(PROJECT, True, [r'^.*py$'], [r'^.*\\storage\\.*$',])
Ścieżka do bazy danych oraz nazwa kolumny w której będziemy trzymać dane odnośnie plików, np:
  fs_database = SQLDatabase('postgresql://postgres:postgres@localhost/versioning', 'fs_version')
Menedżer wersji z bazą danych, silnikiem i ścieżką do pliku z inforamcją o wersji
  fs_versioner = FSVersionCommander(fs_database, fs_engine, '.version')

komenda: python example.py fs list
działanie: wyświetla listę wersji systemu plików

komenda: python example.py fs current/actual/latest
działanie: Wyświetla szczegóły odnośnie bierzącej/aktualnej/najnowszej wersji systemu plików

komenda: python example.py fs changed/outdated
działanie: Sprawdza czy system plików uległ zmianie / jest nieaktualny

komenda: python example.py fs del <name>
działanie: Usuwa wersję systemu plików o nazwie <name> z bazy danych

komenda: python example.py fs set <name>
działanie: Ręcznie ustawia wersję systemu plików [wersja o nazwie <name> musi istnieć w bazie danych]

komenda: python example.py fs bump [<level=0>]
działanie: Tworzy nową wersję systemu plików, podnosząc numer w stosunku do aktualnego w zależności od <level> [bump 0: 1.2.3 -> 1.2.4; bump 2: 1.2.3 -> 2.0.0] 

komenda: python example.py fs diff [<name1=None> [<name2=--ACTUAL-->]]
działanie: Pokazuje zmiany między wersjami o nazwach <name1> i <name2>

Pierwsza ścieżka jest bazy którą chcemy wersjonować, druga do bazy w której będziemy trzyamć dane.

db_versioner = DBVersionCommander('postgresql://postgres:postgres@localhost/vers_test3', 'postgresql://postgres:postgres@localhost/vers_control')

komenda: python example.py db, python example.py db check
działanie: sprawdza wersje bazy 

komenda: python example.py db create
działanie: tworzy nową wersje bazy jeżeli wykryje zmiany


