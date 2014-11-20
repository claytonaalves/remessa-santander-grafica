#coding: utf8
import os.path
from bottle import route, run, template, request, static_file, redirect
from database import connection as conn
import vigo
import remessa

ROOT_PATH = os.path.dirname(os.path.abspath(__file__)) 

@route('/')
def main():
    return template('index.html', 
                    grupos=vigo.Grupos(conn),
                    bancos=vigo.Bancos(conn))

@route('/gerar', method='POST')
def gerar():
    root_path = ROOT_PATH+"/downloads"
    arquivo_remessa = remessa.gerar(request.forms, root_path)
    print arquivo_remessa
    return static_file(arquivo_remessa, root=root_path, download=True)          

run( host='0.0.0.0',
     port=8080,
     debug=True, 
     reloader=True 
 )
