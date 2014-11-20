#coding: utf8

import re

class RowIterator(object):
    QUERY = '' 

    def __init__(self, conn):
        self.conn = conn
        self.conn.ping()
        self.cursor = conn.cursor()
        self.cursor.execute(self.QUERY)

    def __iter__(self):
        return self

    def next(self):
        self.row = self.cursor.fetchone()
        if not self.row: 
            raise StopIteration


class Record(object):

    def __init__(self, conn):
        self.conn = conn


class Empresa(Record):
    razao              = u'RAZÃO SOCIAL DA EMPRESA'
    codigo_transmissao = '00000000000000000000'
    cnpj               = '00000000000000'


class Banco(Record):
    codigo = '033'
    nome   = 'SANTANDER'

    # Codigos da carteira
    # 1 = ELETRÔNICA COM REGISTRO
    # 3 = CAUCIONADA ELETRÔNICA
    # 4 = COBRANÇA SEM REGISTRO
    # 5 = RÁPIDA COM REGISTRO (BLOQUETE EMITIDO PELO CLIENTE)
    # 6 = CAUCIONADA RAPIDA
    # 7 = DESCONTADA ELETRÔNICA
    codigo_carteira = '4'

    def nome_banco(self):
        self.nome = self.nome[5:].replace(' (SIGCB) ', '')
        return self.nome.strip()

    def __str__(self):
        return "%s - %s - %s" % (self.nome_banco(), self.agencia, self.conta)


class Bancos(RowIterator):
    QUERY = ('select id, nomebanco, agencia, conta '
             'from financeiro_bancos '
             'where nomebanco like "%santander%"')

    def next(self):
        RowIterator.next(self)
        banco         = Banco(self.conn)
        banco.id_     = self.row[0]
        banco.nome    = self.row[1]
        banco.agencia = self.row[2]
        banco.conta   = self.row[3]
        return banco


class Grupos(RowIterator):
    QUERY = ('SELECT descricao '
             'FROM cadastro_grupos '
             'WHERE descricao NOT REGEXP "inativo" '
             'ORDER by descricao')

    def next(self):
        RowIterator.next(self)
        return self.row[0].upper()


class Sacado(object):
    numero_documento = '' # numero do documento cpf ou cnpj
    nome = ''
    endereco = ''
    bairro = ''
    cep = ''
    cidade = ''
    uf = ''

    @property
    def tipo_inscricao(self):
        """ Tipo de inscrição do sacado: 01 = CPF, 02 = CGC
        """
        return '01' if len(self.numero_documento)==11 else '02'


class Boleto(object):
    
    def __init__(self):
        self.sacado = Sacado()

    def __str__(self):
        return "<Boleto {0} {1} {2}>".format(self.nosso_numero, self.vencimento, self.valor)


class Boletos(RowIterator):

    QUERY = ('select bol.nome, bol.endereco, bol.bairro, bol.cep, bol.cidade, bol.uf, '
             'bol.cpfcgc, bol.nossonumero, bol.vencimento, bol.valor, bol.emissao '
             'from financeiro_boletos bol '
             'left join cadastro_clientes cli on (cli.id=bol.id_cliente)'
             'where (bol.vencimento between %s and %s) '
             'and cli.grupo=%s '
             'and cli.situacao in ({situacao}) '
             'and bol.id_banco=%s '
             'and bol.ativo="S" '
             'and bol.pago="0" ')

    def __init__(self, conn, vcto1, vcto2, grupo, situacao, idbanco):
        vcto1 = vcto1.strftime('%Y-%m-%d')
        vcto2 = vcto2.strftime('%Y-%m-%d')

        self.QUERY = self.QUERY.format(situacao=situacao)

        conn.ping()
        self.cursor = conn.cursor()
        self.count = self.cursor.execute(self.QUERY, (vcto1, vcto2, grupo, idbanco, ))

    def next(self):
        RowIterator.next(self)

        nome, endereco, bairro, cep, cidade, uf, cpfcgc, nossonumero, \
        vencimento, valor, emissao = self.row

        boleto = Boleto()
        boleto.sacado.nome = nome.encode('latin1')
        boleto.sacado.endereco = endereco.encode('latin1')
        boleto.sacado.bairro = bairro.encode('latin1')
        boleto.sacado.cep = cep.replace('-', '')
        boleto.sacado.cidade = cidade.encode('latin1')
        boleto.sacado.uf = uf
        boleto.sacado.numero_documento = re.sub('[-./]', '', cpfcgc)
        boleto.nosso_numero = str(int(nossonumero.replace('-', ''), 10))
        boleto.vencimento = vencimento.strftime("%d%m%y")
        boleto.valor = valor
        boleto.emissao = emissao.strftime("%d%m%y")
        return boleto

