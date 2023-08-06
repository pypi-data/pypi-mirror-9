# -*- coding: utf-8 -*-

"""
Regras e facilitadores para formatação de dados
"""
import json
import traceback

from urllib import quote_plus
from unicodedata import normalize
from xml.etree import ElementTree
import decimal
from xml.etree.ElementTree import ParseError
import sys


class Formatador(object):
    """
    Classe a ser injetada na entidade que precisa de recursos de formatação
    """
    @classmethod
    def formata_data(cls, data, hora=True, iso=False):
        """
        Formata data nos padrões AAAA-MM-DD HH:mm:ss, AAAA-MM-DDTHH:mm:ss ou AAAA-MM-DD
        :param data: A data a ser formatada
        :type data: datetime
        :param hora: Define se a hora deve vir na data formatada.
        :type hora: bool
        :param iso: Define se a hora virá no formato ISO
        :type iso: bool
        :return: A data formatada de acordo com os parâmetros passados
        :rtype: str
        """
        if hora:
            return data.strftime("%Y-%m-%d{}%H:%M:%S".format("T" if iso else " "))
        return data.strftime("%Y-%m-%d")

    @classmethod
    def formata_cpf(cls, cpf):
        """
        Formata o CPF no padrão XXX.XXX.XXX-XX
        :param cpf: O número do CPF a ser formatado.
        :type cpf: str
        :return: O CPF formatado ou None se o valor for inválido para um CPF
        :rtype: str
        """
        cpf = cpf.replace('.', '').replace('-', '')
        if len(cpf) == 11 and cpf.isdigit():
            return '%s.%s.%s-%s' % (cpf[:3], cpf[3:6], cpf[6:9], cpf[9:])
        return None

    @classmethod
    def formata_cnpj(cls, cnpj):
        """
        Formata o CNPJ no padrão XX.XXX.XXX/XXXX-XX
        :param cnpj: O número do CNPJ a ser formatado.
        :type cnpj: str
        :return: O CNPJ formatado ou None se o valor for inválido para um CNPJ
        :rtype: str
        """
        cnpj = cnpj.replace('.', '').replace('-', '').replace('/', '')
        if len(cnpj) == 14 and cnpj.isdigit():
            return '%s.%s.%s/%s-%s' % (cnpj[:2], cnpj[2:5], cnpj[5:8], cnpj[8:12], cnpj[12:])
        return None

    @classmethod
    def formata_cpf_cnpj(cls, cpf_cnpj):
        """
        Aceita tanto um CPF quanto um CNPJ e retorna o mesmo formatado de acordo com o tamanho do valor enviado.
        :param cpf_cnpj: O número a ser formatado. Se com 11 caracters, formata como CPF, se 14, como CNPJ.
        :type cpf_cnpj: str
        :return: O documento formatado conforme o tamanho.
        :rtype: str
        """
        if not cpf_cnpj:
            return ''
        formatado = cls.formata_cpf(cpf_cnpj) or cls.formata_cnpj(cpf_cnpj)
        if not formatado:
            return cpf_cnpj
        return formatado

    @classmethod
    def string_para_ascii(cls, texto):
        """
        Formata um texto para ascii, removendo caracteres especiais e convertendo acentuados para não acentuados
        :param texto: O texto a ser formatado.
        :type texto: str
        :return: O texto so com caracters ascii
        :rtype: str
        """
        try:
            return normalize('NFKD', texto.decode('utf-8')).encode('ASCII', 'ignore')
        except UnicodeEncodeError:
            return normalize('NFKD', texto).encode('ASCII', 'ignore')

    @classmethod
    def string_para_url(cls, texto):
        """
        Formata a string para ser usada em uma URK (URL Encode)
        :param texto: O texto a ser formatado.
        :type texto: str
        :return: O texto formatado com URL Encode.
        :rtype: str
        """
        return quote_plus(unicode(texto))

    @classmethod
    def converte_para_decimal(cls, valor):
        """
        Converte um valor para Decimal. Caso não seja possível converter, retorna Decimal('0.00')
        :param valor: O valor a ser convertido, podendo ser str, float ou bool
        :return: O valor convertido para Decimal
        :rtype: decimal.Decimal
        """
        try:
            return decimal.Decimal(valor)
        except (decimal.InvalidOperation, ValueError, TypeError):
            return decimal.Decimal('0.00')

    @classmethod
    def trata_unicode_com_limite(cls, texto, limite=None, ascii=False, trata_espaco_duplo=False):
        """
        Trata texto unicode e retorna de acordo com os parâmetros.
        :param texto: O texto a ser tratado.
        :type texto: unicode
        :param limite: Define q quantidade de caracteres a ser retornado de texto.
        :type limite: int
        :param ascii: Define se o texto deve ser retornado apenas com caracteres ascii
        :type ascii: bool
        :param trata_espaco_duplo: Define se espaços duplos entre palavras devem ser trocados por um espaço apenas.
         :type trata_espaco_duplo: bool
        :return: O texto codificado em utf-8 ou ascii conforme o caso
        :rtype: str
        """
        if texto is None:
            return ""
        if isinstance(texto, unicode):
            texto = texto.encode("utf-8")
        if ascii:
            texto = cls.string_para_ascii(texto)
        if trata_espaco_duplo:
            texto = " ".join([palavra for palavra in texto.split(" ") if palavra.strip()])
        if limite:
            return texto[:limite]
        return texto

    @classmethod
    def trata_nome(cls, nome):
        """
        Trata caso especial de nome mal formatado, garantindo que o mesmo tenha pelo ao menos nome e sobrenome e retirando caracteres que podem conflitar com formatação de URL como & e ?.
        :param nome: O nome a ser formatado.
        :type nome: str
        :return: O nome com os ajustes necessários.
        :rtype: str
        """
        if nome:
            nome = nome.strip()
        if len(nome.split(" ")) < 2:
            nome = u"{} x".format(nome)
        if "&" in nome:
            nome = nome.replace("&", "E")
        if "?" in nome:
            nome = nome.replace("?", " ")
        return nome

    @classmethod
    def formata_decimal(cls, valor, como_float=False, como_int=False, em_centavos=False):
        """
        Formata decimal de acordo com os parâmetros passado. O padrão é retornar como string com duas casas decimais.
        :param valor: O valor a ser formatado.
        :type valor: decimal.Decimal, float ou int
        :param como_float: Define se o valor deve ser retornado como float ao invés de string
        :type como_float: bool
        :param como_int: Define se o valor deve ser retornado como int ao invés de string
        :type como_int: bool
        :param em_centavos: Define se o valor deve ser multiplicado por 100 e retornado como um inteiro.
        :type em_centavos: bool
        :return: O valor formatado como string ou de acordo com os parâmetros
        :rtype: str
        """
        if como_float:
            return float('{0:.2f}'.format(valor))
        if como_int:
            return int(valor)
        if em_centavos:
            return int(valor * 100)
        return '{0:.2f}'.format(valor)

    @classmethod
    def converte_tel_em_tupla_com_ddd(cls, telefone):
        """
        Converte um número de telefone em tupla com (DDD, Número). O DDD deve ser os dois primeiros caracteres do telefone passado.
        O método valida se o DDD é um número válido e pertence a algum DDD do Brasil.
        Também valida se o telefone tem 8 ou 9 dígitos.
        :param telefone: Número de telefone com DDD.
        :type telefone: str
        :return: Uma tupla contento o DDD e o Número do telefone.
        :rtype: tuple
        """
        ddd = telefone[:2]
        numero = telefone[2:]
        if not ddd.isdigit() or not telefone.isdigit():
            return '', ''
        if int(ddd) < 11:
            return '', ''
        ddds_invalidos = [20, 23, 25, 26, 29, 30, 36, 39, 40, 50, 52, 56, 57, 58, 59, 60, 70, 72, 76, 78, 80, 90]
        if int(ddd) in ddds_invalidos:
            return '', ''
        if len(numero) < 8 or len(numero) > 9:
            return '', ''
        if numero.startswith("0"):
            return '', ''
        return ddd, numero

    @classmethod
    def trata_email_com_mais(cls, email):
        """
        Remove a parte +algumacoisa da parte caixa postal de um e-mail. Ex.: email+algumacoisa@email.com -> email@email.com
        :param email: O email a ser tratado
        :type email: str
        :return: O email sem o +xxx s existir.
        :rtype: str
        """
        if "+" not in email:
            return email
        partes = email.split("@")
        caixa = partes[0].split("+")[0]
        return "{}@{}".format(caixa, partes[1])

    @classmethod
    def dict_para_xml(cls, dados, tem_cabecalho=False):
        """
        Converte um dicionário em xml.
        Consegue converter subníveis e elementos como lista.
        :param dados: Os dados a serem convertidos em xml
        :type dados: dict
        :param tem_cabecalho: Informa que o xml já possui cabeçalho e não precisa incluir. Se esse valor for False, o método irá adiocionar um <?xml version="1.0" encoding="UTF-8" standalone="yes"?> no início.
        :type tem_cabecalho: bool
        :return: Uma string contendo os valores do dicionário como xml
        :rtype: str
        """
        if not isinstance(dados, dict):
            return ""
        if not dados:
            return ""
        documento = []
        if not tem_cabecalho:
            documento.append('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
        for chave, valor in dados.iteritems():
            documento.append("<{}>".format(chave))
            if isinstance(valor, dict):
                documento.append(cls.dict_para_xml(valor, True))
            elif isinstance(valor, list):
                for parte in valor:
                    documento.append(cls.dict_para_xml(parte, True))
            else:
                documento.append(unicode(valor))
            documento.append("</{}>".format(chave))
        return "".join(documento)

    @classmethod
    def xml_para_dict(cls, content):
        """
        Converte uma string contendo um XML válido em um dicionário python. Caso não seja possível ler o XML, retorna um dicionário vazio.
        Consegue converter subníveis e elementos em lista.
        :param content: Uma string com um XML válido.
        :type content: str
        :return: Um dicionário contendo os valores do XML.
        :rtype: dict
        """
        def iterando(elemento):
            """
            Itera pelo elemento XML e converte para dicionário
            :param elemento: Um elemento xml
            :type elemento: xml.etree.ElementTree
            :return: O elemento como dicionário
            :rtype: dict
            """
            resultado = {}
            childrens = elemento.getchildren()
            if len(childrens) > 0:
                if len(elemento.findall(childrens[0].tag)) > 1:
                    resultado[elemento.tag] = []
                else:
                    resultado[elemento.tag] = {}
                for children in childrens:
                    if isinstance(resultado[elemento.tag], list):
                        resultado[elemento.tag].append(iterando(children))
                    else:
                        resultado[elemento.tag].update(iterando(children))
            else:
                resultado[elemento.tag] = elemento.text
            return resultado

        try:
            root = ElementTree.fromstring(content)
            return iterando(root)
        except (ParseError, TypeError):
            return {}


class ResultadoDeApi(object):
    """
    Fornece métodos para padronizar a serialização de respostas das APIs
    """
    _resultados = {
        200: 'sucesso',
        400: 'request_invalido',
        401: 'nao_autorizado',
        403: 'nao_autenticado',
        404: 'nao_encontrado',
        405: 'metodo_nao_permitido',
        408: 'timeout',
        500: 'erro_servidor'
    }

    @classmethod
    def _formata_trace_back(cls, trace_back):
        """
        Formata o trace back como uma lista de dicionários no seguinte formato:
        {
            'codigo': '    a = 1 / 0',
            'local': '..unitarios/padroes/test_serializacao.py, line 318, in test_deve_retornar_resposta_para_erro_500_com_trace_back_passado'
        }
        :param trace_back: O traceback da exceção
        :type trace_back: list
        :return: A lista de traceback formatada
        :rtype: list
        """
        resultado = []
        for stack in trace_back[-4:-1]:
            linhas = stack.split('\n')
            local = linhas[0].split(', ')
            local[0] = local[0].strip()
            local[0] = local[0].replace('File "', '').replace('"', '')
            local[0] = '..{}'.format('/'.join(local[0].split('/')[-3:]))
            local = ", ".join(local)
            if not local.startswith('..Traceback '):
                resultado.append({'local': local, 'codigo': linhas[1]})
        return resultado

    @classmethod
    def resposta(cls, conteudo, nome_api, versao, status=200, excecao=None):
        """
        Monta a resposta para os dados do resultado.
        :param conteudo: Um dicionário com o conteúdo da resposta a ser enviado. Caso não seja passado um dicionário, o mesmo será criado com a chave 'conteudo' e o valor passado nesse parametro.
        :type conteudo: dict
        :param nome_api: O nome da API que está produzindo a resposta
        :type nome_api: str
        :param versao: A versão da API que está produzindo a resposta
        :type versao: str
        :param status: O status code da resposta
        :type status: int
        :param excecao: A exceção que gerou uma resposta com status code 500
        :type excecao: Exception
        :return: Tupla com os dados do resultado e o status code
        :rtype: tuple
        """
        if status == 403:
            conteudo = {'conteudo': u'A autenticação falhou: {}'.format(conteudo)}
        if status == 404:
            conteudo = {'conteudo': u'A url acessada não existe em nome-da-api'}
        if status == 405:
            conteudo = {'conteudo': u'Não é permitido esse método HTTP para essa URL.'}
        if status == 408:
            conteudo = {'conteudo': u'O servidor não respondeu em tempo.'}
        if not isinstance(conteudo, dict):
            conteudo = {'conteudo': conteudo}
        try:
            status_resultado = cls._resultados[status]
        except KeyError:
            status_resultado = 'status_nao_definido'
        metadados = {
            'api': nome_api,
            'versao': versao,
            'resultado': status_resultado,
        }
        conteudo = conteudo
        if excecao:
            exc_type, exc_value, trace_back = sys.exc_info()
            if exc_type:
                stack_trace = traceback.format_exception(exc_type, exc_value, trace_back)
            else:
                try:
                    stack_trace = traceback.format_exception(excecao.tipo, excecao, excecao.tb)
                except AttributeError:
                    stack_trace = []
            stack_trace = cls._formata_trace_back(stack_trace)
            nome_exec = excecao.__class__.__name__
            conteudo.update({'excecao': {'nome': nome_exec, 'mensagem': unicode(excecao), 'stack_trace': stack_trace}})
        resultado = {
            'metadados': metadados,
            status_resultado: conteudo
        }
        return json.dumps(resultado), status
