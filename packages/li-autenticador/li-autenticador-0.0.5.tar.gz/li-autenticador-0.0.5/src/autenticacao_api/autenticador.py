# -*- coding: utf-8 -*-
"""
Funcionalidades para implementar uma autenticação via chave no header para uma API Flask
"""

from functools import wraps
from flask import request, make_response
from li_common.padroes import serializacao


class ErrosHTTP(object):
    """
    Encapsula métodos para os dois tipos de erro, 400 e 401
    """

    def __init__(self, nome_api=None, versao_api=None):
        self.nome_api = nome_api
        self.versao_api = versao_api

    def erro_400(self, chaves):
        """
        Retorna uma tupla para ser usada como retorno de requisição de API com uma mensagem padrão de erro 400
        :param chaves: As chaves necessárias para fazer a autenticação.
        :type chaves: list
        :return: Uma tupla com dicionário com a mensagem de erro, citando um exemplo de como fazer a requisição correta e o status code 400.
        :rtype: tuple
        """
        modelos = ["{} XXXXXXXX-YYYY-ZZZZ-AAAA-BBBBBBBBBBBB".format(chave) for chave in chaves]
        conteudo = {
            'mensagem': u"Adicione um cabeçalho Authorization com {} para acessar essa api. Ex.: Authorization: {}".format(", ".join(chaves), " ".join(modelos))
        }
        conteudo, status = serializacao.ResultadoDeApi.resposta(conteudo, self.nome_api or 'Autenticador', self.versao_api or '0.0.1', 400)
        headers = {'Content-Type': 'text/json; charset=utf-8'}
        return make_response(conteudo, status, headers)

    def erro_401(self):
        """
        Retorna uma tupla para ser usada como retorno de requisição de API com uma mensagem padrão de erro 401
        :return: Uma tupla com dicionário com a mensagem 'Você não está autorizado a acessar essa url.' e o status code 401.
        :rtype: tuple
        """
        conteudo = {
            'mensagem': u"Você não está autorizado a acessar essa url."
        }
        conteudo, status = serializacao.ResultadoDeApi.resposta(conteudo, self.nome_api or 'Autenticador', self.versao_api or '0.0.1', 401)
        headers = {'Content-Type': 'text/json; charset=utf-8'}
        return make_response(conteudo, status, headers)


class Autenticacao(object):
    """
    Fornece as funcionalidades para executar a autenticação da API
    """
    def __init__(self, nome_api=None, versao_api=None):
        self.nome_api = nome_api
        self.versao_api = versao_api
        self.valores = {}

    def define_valor(self, nome, valor):
        """
        Define o uma chave/valor que deverá ser validada em um cabeçalho AUTHORIZATION. Esse método deve ser chamado na inicialização da api que precisa da autenticação.
        :param nome: O nome da chave que deverá existir no cabeçalho AUTHORIZATION
        :type nome: str
        :param valor: O valor da chave
        :type valor: str
        :return: None
        """
        self.valores[nome] = valor

    def chaves_validas(self, chaves):
        """
        Verifica se as chaves passadas foram definidas para a API e se os valores são válidos
        :param chaves: As chaves extraídas do cabeçalho AUTHORIZATION
        :type chaves: dict
        :return: True caso a chave exista e o valor seja o mesmo definido. De outro jeito, False
        :rtype: bool
        """
        for chave in self.valores.keys():
            if chave not in chaves:
                return False
            if chaves[chave] != self.valores[chave]:
                return False
        return True

    def extrai_chaves(self, chaves, headers):
        """
        Tenta extrair as chaves de autenticação do cabeçalho HTTP passado. O cabeçalho deve conter um elemento AUTHORIZATION
        :param chaves: Lista com as chaves que se espera existir no cabeçalho. As mesmas definidas com o Autenticador.define_valor(nome, valor)
        :type chaves: list
        :param headers: O cabeçalho HTTP
        :type headers: dict
        :return: As chaves extraídas do cabeçalho como um dicionário
        :rtype: dict
        """
        try:
            authorization = headers["AUTHORIZATION"]
        except KeyError:
            return None
        if not authorization:
            return None
        authorization = authorization.split()
        if len(authorization) != len(chaves) * 2:
            return None
        resultado = {}
        for chave in chaves:
            if chave in authorization:
                indice = authorization.index(chave) + 1
                resultado[chave] = authorization[indice]
        return resultado

    def requerido(self, function):
        """
        Decorator para ser usado na função que deve exigir autenticação.
        """
        @wraps(function)
        def decorated(*args, **kwargs):
            """
            Valida a autenticação para o método decorado
            """
            chaves = self.extrai_chaves(self.valores.keys(), request.headers)
            if not chaves:
                return ErrosHTTP(self.nome_api, self.versao_api).erro_400(self.valores.keys())
            if not self.chaves_validas(chaves):
                return ErrosHTTP(self.nome_api, self.versao_api).erro_401()
            return function(*args, **kwargs)

        return decorated
