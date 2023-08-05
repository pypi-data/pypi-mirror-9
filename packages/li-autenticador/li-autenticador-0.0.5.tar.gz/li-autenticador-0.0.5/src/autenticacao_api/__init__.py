# -*- coding: utf-8 -*-

import autenticador


def autenticacao(nome_api=None, versao_api=None):
    return autenticador.Autenticacao(nome_api, versao_api)