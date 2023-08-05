# -*- coding: utf-8 -*-

from importlib import import_module
settings = None


class ClasseNaoEncontrada(Exception):
    pass


class ClasseInvalida(Exception):
    pass


class ExtensaoNaoDefinido(Exception):
    pass


class ModuloDeExtensaoNaoEncontrado(Exception):
    pass


class Extensao(object):
    extensao = None

    def cria_entidade_da_extensao(self, tipo, **kwargs):
        try:
            import_extensao = settings.EXTENSOES[self.extensao]
        except KeyError:
            raise ExtensaoNaoDefinido(u"A extensão '{}' não foi encontrada nas configurações. Você esqueceu de inclui-la em settings.EXTENSOES?".format(self.extensao))
        try:
            modulo = import_module('{}.entidades'.format(import_extensao))
        except ImportError, ex:
            raise ModuloDeExtensaoNaoEncontrado(u'Não foi encontrado o modulo "{}.entidades" para a extensão "{}" no ambiente.'.format(import_extensao, self.extensao))
        try:
            classe = getattr(modulo, tipo)
        except AttributeError, ex:
            raise ClasseNaoEncontrada(u'Não foi encontrado a classe de entidade "{}.entidades.{}" para a extensão "{}" no ambiente.'.format(import_extensao, tipo, self.extensao))
        try:
            return classe(**kwargs)
        except TypeError:
            raise ClasseInvalida(u'A classe de entidade "{}.entidades.{}" para o meio de pagamento "{}" não aceitou os argumentos passados: "{}".'.format(import_extensao, tipo, self.extensao, kwargs))
