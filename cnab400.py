#coding: utf8
from datetime import date

class Empresa(object):
    razao              = u'RAZÃO SOCIAL DA EMPRESA'
    codigo_transmissao = '20320216899501300356'
    cnpj               = '02271317000198'


class Banco(object):
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


class CNAB400(object):

    def __init__(self, banco, empresa):
        self.banco = banco
        self.empresa = empresa

    def _header(self):
        self.sequencial_registro = 1
        self.arquivo.write('0')                                    # codigo do registro
        self.arquivo.write('1')                                    # codigo remessa
        self.arquivo.write('REMESSA')                              # literal_transmissao
        self.arquivo.write('01')                                   # codigo servico
        self.arquivo.write('COBRANCA'.ljust(15))                   # literal servico
        self.arquivo.write(self.empresa.codigo_transmissao)        # codigo de transmissão
        self.arquivo.write(self.empresa.razao.encode('latin1'))    # nome da empresa
        self.arquivo.write(self.banco.codigo)                      # codigo do banco
        self.arquivo.write(self.banco.nome.ljust(15))              # nome do banco
        self.arquivo.write(date.today().strftime('%d%m%y'))        # data gravacao
        self.arquivo.write('0000000000000000')                     # zeros
        self.arquivo.write(' ' * 275)                              # brancos
        self.arquivo.write('000')                                  # versao remessa
        self.arquivo.write(str(self.sequencial_registro).zfill(6)) # sequencial do registro

        # custom
        self.arquivo.write(' ' * 200)
        self.arquivo.write('\n')

    def _detail(self, boleto):
        self.sequencial_registro += 1

        self.arquivo.write('1')                                            # codigo registro
        self.arquivo.write('02')                                           # tipo_inscricao = cnpj
        self.arquivo.write(self.empresa.cnpj)                              # cnpj da empresa
        self.arquivo.write(self.empresa.codigo_transmissao)                # codigo de transmissao
        self.arquivo.write('                         ')                    # numero_participante
        self.arquivo.write(boleto.nosso_numero[0:8].rjust(8, '0'))         # nosso número 9(008)
        self.arquivo.write('000000')                                       # data segundo desconto 9(006)
        self.arquivo.write(' ')                                            # branco
        self.arquivo.write('4')                                            # Informação de multa = 4, senão houver informar zero
        self.arquivo.write('0200')                                         # Percentual multa por atraso % 9(004)
        self.arquivo.write('00')                                           # Unidade de valor moeda corrente = 00
        self.arquivo.write('0000000000000')                                # Valor do título em outra unidade
        self.arquivo.write('    ')                                         # brancos X(004)
        self.arquivo.write('000000')                                       # Data para cobrança de multa 9(006)
        self.arquivo.write(self.banco.codigo_carteira)                     # código da carteira 9(001)
        self.arquivo.write('01')                                           # código da ocorrência 9(002) ( 01 = ENTRADA DE TÍTULO )
        self.arquivo.write(boleto.nosso_numero.rjust(10, '0'))             # seu número (nosso número)
        self.arquivo.write(boleto.vencimento)                              # Data de vencimento do título 9(006)
        self.arquivo.write(self._formata_valor(boleto.valor))              # Valor do título - moeda corrente 9(013)v99
        self.arquivo.write(self.banco.codigo)                              # Número do Banco cobrador = 033
        self.arquivo.write('00000')                                        # Código da agência cobradora
        self.arquivo.write('01')                                           # espécie de documento (01 = DUPLICATA)
        self.arquivo.write('N')                                            # Tipo de aceite = N
        self.arquivo.write(boleto.emissao)                                 # Data da emissão do título 9(006)
        self.arquivo.write('00')                                           # Primeira instrução cobrança
        self.arquivo.write('00')                                           # Segunda instrução cobrança (00 = NÃO HÁ INSTRUÇÕES)
        self.arquivo.write('0'*13)                                         # Valor de mora a ser cobrado por dia de atraso. 9(013)v99
        self.arquivo.write('000000')                                       # Data limite para concessão de desconto
        self.arquivo.write('0'*13)                                         # Valor de desconto a ser concedido
        self.arquivo.write('0'*13)                                         # Valor do IOF a ser recolhido pelo Banco para nota de seguro
        self.arquivo.write('0'*13)                                         # Valor do abatimento a ser concedido ou valor do segundo desconto
        self.arquivo.write(boleto.sacado.tipo_inscricao)                   # Tipo de inscrição do sacado: 01 = CPF, 02 = CGC
        self.arquivo.write(boleto.sacado.numero_documento[0:14].rjust(14, '0')) # CGC ou CPF do sacado 9(014)
        self.arquivo.write(boleto.sacado.nome[0:40].ljust(40))             # Nome do sacado X(040)
        self.arquivo.write(boleto.sacado.endereco[0:40].ljust(40))         # Endereço do sacado X(040)
        self.arquivo.write(boleto.sacado.bairro[0:12].ljust(12))           # Bairro do sacado X(012)
        self.arquivo.write(boleto.sacado.cep.rjust(8, '0'))                # CEP do sacado 9(008)
        self.arquivo.write(boleto.sacado.cidade[0:15].ljust(15))           # Município do sacado X(015)
        self.arquivo.write(boleto.sacado.uf)                               # UF Estado do sacado X(002)
        self.arquivo.write(' '*30)                                         # Nome do sacador ou coobrigado X(030)
        self.arquivo.write(' ')                                            # brancos
        self.arquivo.write('I')                                            # Identificador do Complemento
        self.arquivo.write('25')                                           # Complemento
        self.arquivo.write(' '*6)                                          # brancos
        self.arquivo.write('00')                                           # Número de dias para protesto. 9(002)
        self.arquivo.write(' ')                                            # branco
        self.arquivo.write(str(self.sequencial_registro).zfill(6))         # Número seqüencial do registro no arquivo

        # custom
        self.arquivo.write(boleto.sacado.endereco[0:60].ljust(60)) # X(060)
        self.arquivo.write(' '*80) # brancos X(080)
        self.arquivo.write(boleto.sacado.cep.rjust(8, '0')) # cep 9(008)
        self.arquivo.write(boleto.sacado.cidade[0:52].ljust(52)) # cep X(054)

        self.arquivo.write('\n')

    def _trailler(self, valor_total):
        total_registros = str(self.sequencial_registro+1).zfill(6)
        self.arquivo.write('9')                              # código do registro
        self.arquivo.write(total_registros)                  # Quantidade total de linhas no arquivo
        self.arquivo.write(self._formata_valor(valor_total)) # Valor total dos títulos
        self.arquivo.write('0'*374)                          # zeros
        self.arquivo.write('000000')                         # Número seqüencial do registro no arquivo
        self.arquivo.write('0'*70)                           # zeros
        self.arquivo.write(total_registros)                  # Quantidade total de linhas no arquivo
        self.arquivo.write(' '*123)
        self.arquivo.write('0')

        self.arquivo.write('\n')

    def _formata_valor(self, valor):
        return ("%.2f" % valor).replace('.', '').zfill(13)

    def gerar(self, boletos, arquivo):
        self.arquivo = open(arquivo, 'w')
        self._header()
        valor_total = 0
        for boleto in boletos:
            self._detail(boleto)
            valor_total += boleto.valor
        self._trailler(valor_total)
        self.arquivo.close()


