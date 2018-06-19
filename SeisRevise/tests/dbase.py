from SeisRevise.DBase.temp import SqliteORM

a=SqliteORM()
a.folder_path='D:/temp'
a.dbase_name='qwerty.db'
q,e=a.create_dbase
print(e)