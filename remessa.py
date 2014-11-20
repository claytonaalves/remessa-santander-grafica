import re
import locale
from vigo import Empresa, Banco, Boletos
from database import connection as conn
from datetime import datetime
from cnab400 import CNAB400

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def gerar(opcoes, root_path):
    """ Gera um arquivo de remessa e retorna o nome do arquivo
    """
    situacoes = {
        "ativos"      : "'L'",
        "bloqueados"  : "'B'",
        "desativados" : "'X'",
        "todos"       : "'L', 'B', 'X'"
    }

    vcto_inicial = datetime.strptime(opcoes.get('data_inicial'), '%d/%m/%Y')
    vcto_final   = datetime.strptime(opcoes.get('data_final'), '%d/%m/%Y')
    grupo        = opcoes.get("grupo", "EMITIR TODO MES")
    situacao     = situacoes[opcoes.get('situacao', 'ativos')]
    idbanco      = int(opcoes.get("banco"))

    conn.ping()
    cedente = Empresa(conn)
    banco   = Banco(conn)
    boletos = Boletos(conn, vcto_inicial, vcto_final, grupo, situacao, idbanco)

    filename = '{0}.rem'.format(vcto_inicial.strftime('%B'))
    remessa = CNAB400(banco, cedente)
    remessa.gerar(boletos, root_path+'/'+filename)
    return filename

if __name__=="__main__":
    opcoes = dict(
        data_inicial = "01/01/2014",
        data_final   = "31/12/2014",
        banco = "15",
        grupo = "EMITIR TODO MES",
        situacao = "ativos"
    )                 

    gerar(opcoes, 'downloads')

