import MySQLdb
import re
from cnab400 import Empresa, Banco, Boleto, CNAB400

conn = MySQLdb.connect('localhost', 'claytontemp', 'senha', 'vigo_erp')
q = conn.cursor()

q.execute('select bol.nome, bol.endereco, bol.bairro, bol.cep, bol.cidade, bol.uf, '
          'bol.cpfcgc, bol.nossonumero, bol.vencimento, bol.valor, bol.emissao '
          'from financeiro_boletos bol '
          'left join cadastro_clientes cli on (cli.id=bol.id_cliente)'
          'where (bol.vencimento between %s and %s) '
          'and cli.grupo="EMITIR TODO MES" '
          'and cli.situacao="L" '
          'and bol.id_banco=15 '
          'and bol.ativo="S" '
          'and bol.pago="0" '
          , ('2014-09-01', '2014-09-31'))

# TODO: pago='0'

boletos = []

for nome, endereco, bairro, cep, cidade, uf, cpfcgc, nossonumero, vencimento, valor, emissao in q:
    boleto = Boleto()
    boleto.sacado.nome = nome
    boleto.sacado.endereco = endereco
    boleto.sacado.bairro = bairro
    boleto.sacado.cep = cep.replace('-', '')
    boleto.sacado.cidade = cidade
    boleto.sacado.uf = uf
    boleto.sacado.numero_documento = re.sub('[-./]', '', cpfcgc)
    boleto.nosso_numero = str(int(nossonumero.replace('-', ''), 10))
    boleto.vencimento = vencimento.strftime("%d%m%y")
    boleto.valor = valor
    boleto.emissao = emissao.strftime("%d%m%y")
    boletos.append(boleto)

    print nome, nossonumero

empresa = Empresa()
banco = Banco()
remessa = CNAB400(banco, empresa)
remessa.gerar(boletos, 'remessa_total_telecom_setembro.rem')


