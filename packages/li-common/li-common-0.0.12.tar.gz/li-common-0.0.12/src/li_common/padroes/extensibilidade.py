# -*- coding: utf-8 -*-

"""
Componentes para permitir a criação de objetos de extensões.
"""
from importlib import import_module

SETTINGS = None


class ClasseNaoEncontrada(Exception):
    """
    Erro disparado quando uma classe não é encontrada no módulo entidades.
    """
    pass


class ClasseInvalida(Exception):
    """
    Disparado quando a instância da classe não pode ser criada por algum TypeError.
    """
    pass


class ExtensaoNaoDefinido(Exception):
    """
    Disparado quando a extensão não for definida no SETTINGS.
    """
    pass


class ModuloDeExtensaoNaoEncontrado(Exception):
    """
    Disparado quando der ImportError do módulo definido no SETTINGS.
    """
    pass


class Extensao(object):
    """
    Fornece a capacidade de uma classe poder criar extensões baseados em um modulo definido como o atributo da classe 'extensao'.
    """
    extensao = None

    def _cria_extensao(self, tipo, modulo, **kwargs):
        """
        Método que executa a ação de criar a extensão. É usado pelos dois métodos públicos de criar extensão.
        :param tipo: O nome da classe que deverá ser encontrada no módulo <extensao>.<modulo>
        :type tipo: str
        :param modulo: O módulo de onde a classe deve ser instanciada.
        :type modulo: str
        :param kwargs: Argumentos a serem passados para a criação da instância da classe
        :return: Uma instância da classe criada.
        """
        try:
            import_extensao = SETTINGS.EXTENSOES[self.extensao]
        except KeyError:
            raise ExtensaoNaoDefinido(u'A extensão "{}" não foi encontrada nas configurações. Você esqueceu de inclui-la em SETTINGS.EXTENSOES?'.format(self.extensao))
        try:
            _modulo = import_module('{}.{}'.format(import_extensao, modulo))
        except ImportError:
            raise ModuloDeExtensaoNaoEncontrado(u'Não foi encontrado o modulo "{}.{}" para a extensão "{}" no ambiente.'.format(import_extensao, modulo, self.extensao))
        try:
            classe = getattr(_modulo, tipo)
        except AttributeError:
            raise ClasseNaoEncontrada(u'Não foi encontrado a classe "{}.{}.{}" para a extensão "{}" no ambiente.'.format(import_extensao, modulo, tipo, self.extensao))
        try:
            instancia = classe(**kwargs)
            if hasattr(instancia, 'extensao'):
                instancia.extensao = self.extensao
            return instancia
        except TypeError:
            raise ClasseInvalida(u'A classe "{}.{}.{}" para o meio de pagamento "{}" não aceitou os argumentos passados: "{}".'.format(import_extensao, modulo, tipo, self.extensao, kwargs))

    def cria_entidade_extensao(self, tipo, **kwargs):
        """
        Retorna a entidade definida em tipo contendo dentro do módulo 'entidades' da extensão.
        :param tipo: O nome da classe que deverá ser encontrada no módulo <extensao>.entidades
        :type tipo: str
        :param kwargs: Argumentos a serem passados para a criação da instância da classe
        :return: Uma instância da classe criada.
        """
        return self._cria_extensao(tipo, 'entidades', **kwargs)

    def cria_servico_extensao(self, tipo, **kwargs):
        """
        Retorna o serviço definido em tipo contendo dentro do módulo 'servicos' da extensão.
        :param tipo: O nome da classe que deverá ser encontrada no módulo <extensao>.servicos
        :type tipo: str
        :param kwargs: Argumentos a serem passados para a criação da instância da classe
        :return: Uma instância da classe criada.
        """
        return self._cria_extensao(tipo, 'servicos', **kwargs)
