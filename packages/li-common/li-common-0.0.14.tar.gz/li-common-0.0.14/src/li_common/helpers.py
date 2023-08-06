# -*- coding: utf-8 -*-

"""
Funções para auxiliarem no desenvolvimento
"""

import time
from functools import wraps


def tente_outra_vez(excecoes, tentativas=4, tempo_espera=3, multiplicador_espera=1, logger=None):
    """
    Escuta pelas exceções especificadas e refaz a chamada para o método.
    :param excecoes: As exceções que devem ser escutadas
    :type excecoes: Exception or tuple
    :param tentativas: Número de vezes que deve ser chamado o método
    :type tentativas: int
    :param tempo_espera: Tempo inicial de espera em segundos entre as tentativas
    :type tempo_espera: int
    :param multiplicador_espera: Multiplicador para o tempo de espera nas chamadas subsequentes.
    :type multiplicador_espera: int
    :param logger: Mecanismo de log
    :type logger: logging.Logger instance
    """
    def deco_tente_outra_vez(funcao):
        """
        Decorator para tente_outra_vez
        """
        @wraps(funcao)
        def funcao_tente_outra_vez(*args, **kwargs):
            """
            Tratamento de decorator para tente_outra_vez
            """
            _tentativas, _tempo_espera = tentativas, tempo_espera
            while _tentativas > 1:
                try:
                    return funcao(*args, **kwargs)
                except excecoes, exc:
                    msg = "{}, Reconectando in {} segundos...".format(str(exc), _tempo_espera)
                    if logger:
                        logger.warning(msg)
                    time.sleep(_tempo_espera)
                    _tentativas -= 1
                    _tempo_espera *= multiplicador_espera
            return funcao(*args, **kwargs)
        return funcao_tente_outra_vez
    return deco_tente_outra_vez
