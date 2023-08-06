# -*- coding: utf-8 -*-

"""
Módulo contendo a base para todos os repositórios usados nos projetos da Loja Integrada.
"""


class ModelNaoDefinido(Exception):
    """
    Exceção para quando um repositório for instanciado sem um model definido
    """
    pass


class ManagerNaoDefinido(Exception):
    """
    Exceção para quando um repositório for instanciado sem um manager definido
    """
    pass


class Repositorio(object):
    """
    Classe base para a criação dos repositórios
    """
    classe_model = None
    manager = None

    def __init__(self):
        if not self.classe_model:
            raise ModelNaoDefinido(u'Não foi definido o model para o repositório {}'.format(self.__class__.__name__))
        self.do_banco = None

    def _listar(self, **filtros):
        """
        Método padrão para fazer queries com o ORM
        :param filtros: Opcional, um dicionário contendo os filtros a serem passados para o ORM
        :type filtros: dict
        :return: O resultado do QuerySet do ORM
        """
        if filtros:
            return self.manager.filter(**filtros)
        return self.manager.all()

    def _obter_com_id(self, entidade_id):
        """
        Obtém uma entidade com o ID do registro no banco
        :param entidade_id: O ID no banco
        :type entidade_id: int
        :return: A instância do model do ORM
        """
        return self._obter(id=entidade_id)

    def _obter(self, **filtros):
        """
        Retorna um registro do banco usando o ORM
        :param filtros: os filtros a serem usando na busca
        :return: O resultado do ORM
        """
        try:
            return self.manager.get(**filtros)
        except self.classe_model.DoesNotExist:
            raise InstanciaNaoExiste(u'Não foi encontrada instância de {} com {}.'.format(self.classe_model.__name__, u', '.join(['{}={}'.format(chave, filtros[chave]) for chave in filtros])))
        except self.classe_model.MultipleObjectsReturned:
            raise MaisDeUmaInstanciaEncontrada(u'Mais de uma instância de {} foi retornada com {}.'.format(self.classe_model.__name__, u', '.join(['{}={}'.format(chave, filtros[chave]) for chave in filtros])))

    def _criar(self, **propriedades):
        """
        Cria uma instância do model no banco usando o ORM.
        :param propriedades: Os valores a serem gravados nas propriedades da instância criada
        :return A instância criada no banco
        """
        return self.manager.create(**propriedades)

    def _atualizar(self, entidade_id, **propriedades):
        """
        Atualiza uma instância do model no banco usando o ORM.
        :param entidade_id: O ID da instância da entidade que será atualizada
        :param propriedades: Os valores a serem gravados nas propriedades da instância atualizada
        """
        instancia = self._obter_com_id(entidade_id)
        for propriedade in propriedades:
            setattr(instancia, propriedade, propriedades[propriedade])
        instancia.save()


class InstanciaNaoExiste(Exception):
    """
    Exceção para quando uma instância não for encontrada pelo ORM
    """
    pass


class MaisDeUmaInstanciaEncontrada(Exception):
    """
    Exceção para quando o ORM retornar mais de um valor e a query esperar apenas um valor.
    """
    pass
