import MySQLdb

connection = MySQLdb.connect('localhost',
                             'usuario', 
                             'senha', 
                             'vigo_erp', 
                             charset='latin1', 
                             use_unicode=True)


