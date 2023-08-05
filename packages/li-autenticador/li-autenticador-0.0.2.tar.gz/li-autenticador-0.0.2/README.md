# LI-Autenticador

## Versão:

[![PyPi version](https://pypip.in/v/li-autenticador/badge.png?style=flat)](https://pypi.python.org/pypi/li-autenticador)
[![PyPi downloads](https://pypip.in/d/li-autenticador/badge.png?style=flat)](https://pypi.python.org/pypi/li-autenticador)


## Build Status

### Master

[![Build Status](https://travis-ci.org/lojaintegrada/LI-Autenticador.svg?branch=master)](https://travis-ci.org/lojaintegrada/LI-Autenticador)
[![Coverage Status](https://coveralls.io/repos/lojaintegrada/LI-Autenticador/badge.svg?branch=master)](https://coveralls.io/r/lojaintegrada/LI-Autenticador?branch=master)

## Descrição

Possibilita adicionar autenticação simples a API baseada em Flask.


## Exemplo

Em um módulo que seja acessível a API, de preferência no mesmo onde a App Flask é criada implemente:

módulo app.py

```python
from flask import Flask
import autenticacao_api


autenticacao = autenticacao_api.autenticacao()
autenticacao.define_valor('chave_necessario', 'VALOR-NECESSARIO')

app_flask = Flask("App")
```

No código que precise de autenticação, faça:

módulo recursos.py

```python
import app

@app.app_flask.route("/secure")
@app.autenticacao.requerido
def secure():
    return "Autenticado!"
```
