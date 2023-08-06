# -*- coding: utf-8 -*-
"""
Fornece recusros para a montagem de formulário para as APIs
"""
from li_common.padroes import entidades, serializacao


class TipoDeCampo(object):
    """
    Traduções de nomes de campo para o renderizador de campos
    """
    texto = "CharField"
    area = "TextArea"
    boleano = "BooleanField"
    escolha = "ChoiceField"
    decimal = "BRDecimalField"
    oculto = "Hidden"


class FormatoDeCampo(object):
    """
    Tipos de formato de campo para que o valor do campo seja formatado ao ser renderizado
    """
    texto = "texto"
    ascii = "ascii"
    html = "html"
    xml = "xml"
    json = "json"
    numero = "numero"


class CampoFormulario(entidades.Entidade):
    """
    Define as informações necessárias para construir um campo de formulário no renderizador
    """
    _nao_serializar = ['validador']

    def __init__(self, nome, label=None, bound=True, descricao=None, requerido=False, tipo=TipoDeCampo.texto, formato=FormatoDeCampo.texto, invisivel=False,
                 tamanho_min=None, tamanho_max=None, ordem=0, texto_ajuda=None, opcoes=(), grupo=None, valor_padrao=None, validador=None, decimais=2):
        self.bound = bound
        self.ordem = ordem
        self.nome = nome
        self.label = label
        self.descricao = descricao
        self.requerido = requerido
        self.tipo = tipo
        self.formato = formato
        self.invisivel = invisivel
        self.tamanho_min = tamanho_min
        self.tamanho_max = tamanho_max
        self.texto_ajuda = texto_ajuda
        self.opcoes = opcoes
        self.grupo = grupo
        self.valor_padrao = valor_padrao
        self.validador = validador
        self.decimais = decimais


class DadosInvalidos(Exception):
    """
    Exceção para quando ocorrer erros de validação. Ela possui atributo erros, que é um dicionário contendo o erro de cada validação.
    """
    def __init__(self, msg, erros):
        super(DadosInvalidos, self).__init__(msg)
        self.erros = erros


class ValidadorBase(object):
    """
    Base para processar validações
    """
    def __init__(self, valor):
        self.valor = valor
        self.erros = {}

    @property
    def eh_valido(self):
        """
        É chamado pelo processo de validação do formulário. Deve ser sobrescrito com a regra de validação
        :return True caso o valor esteja correto
        :rtype: bool
        """
        return True


class Formulario(entidades.Entidade):
    """
    Classe base para a criação de um formulário para cadastro de entidades.
    """
    def __init__(self):
        self._campos = [atributo for atributo in dir(self) if atributo != 'campos' and atributo != 'nomes_campos' and isinstance(getattr(self, atributo), CampoFormulario)]

    @property
    def campos(self):
        """
        Um dicionário com os campos do formulário, tendo o nome do atributo como chave e a instância de CampoFormulario como valor
        :return: A lista de campos
        :rtype: dict
        """
        return {campo: getattr(self, campo) for campo in self._campos}

    @property
    def nomes_campos(self):
        """
        Uma lista contendo os nomes dos campos definidos no atributo CampoFormulario.nome
        :return: A lista dos nomes dos campos
        :rtype: list
        """
        return [getattr(self, campo).nome for campo in self._campos]

    def to_dict(self):
        """
        Renderiza os campos do formulário em dicionário
        :return: Um dicionario com os campos do formulário em dicionário
        :rtype: dict
        """
        return {campo: self.campos[campo].to_dict() for campo in self.campos}

    def validar_valores(self, valores):
        """
        Valida se os valores passados para os campos estão de acordo com a regra de validação caso seja definida no campo
        :param valores: Um dicionário contendo os valores a serem validados sendo a chave o nome atributo do campo
        :type valores: dict
        :return: Um dicionário com os erros encontrados ou um dicionário vazio.
        :rtype: dict
        """
        erros = {}
        for campo in self.campos:
            campo = self.campos[campo]
            if campo.validador:
                valor = valores.get(campo.nome, None)
                validacao = campo.validador(valor)
                if not validacao.eh_valido:
                    erros[campo.nome] = validacao.erros
        if erros:
            raise DadosInvalidos(u"Ocorreram erros de validação.", erros)

    def definir_valores(self, instancia, valores):
        """
        Define os valores dos campos do formulário em um instancia, formatando os valores de acordo com o campo.formato
        :param instancia: Uma instância de um objeto.
        :type instancia: object
        :param valores: Dicionário contendo os valores. As chaves deve ser os mesmos que campo.nome
        :type valores: dict
        :return: None
        """
        for campo in self.campos:
            campo = self.campos[campo]
            if campo.bound:
                valor = valores.get(campo.nome, None)
                if valor and campo.formato == FormatoDeCampo.ascii:
                    valor = serializacao.Formatador.string_para_ascii(valor)
                setattr(instancia, campo.nome, valor)
