# Py Inspector

## Versão:

[![PyPi version](https://pypip.in/v/py-inspector/badge.png)](https://pypi.python.org/pypi/py-inspector)
[![PyPi downloads](https://pypip.in/d/py-inspector/badge.png)](https://pypi.python.org/pypi/py-inspector)


## Build Status

### Master

[![Build Status](https://travis-ci.org/Maethorin/py-inspector.svg?branch=master)](https://travis-ci.org/Maethorin/py-inspector)
[![Coverage Status](https://coveralls.io/repos/Maethorin/py-inspector/badge.svg?branch=master)](https://coveralls.io/r/Maethorin/py-inspector?branch=master)

## Descrição

Possibilita a criação de testes para PEP8 e PyLint que serão executados com nose


## Exemplo

```python
import unittest
from py_inspector import verificadores
from seu_codigo import modulo_a_ser_validado

class ValidandoPython(unittest.TestCase, verificadores.TestValidacaoPython):
    def test_deve_verificar_pep8_no_modulo(self):
        arquivo = modulo_a_ser_validado.__file__.replace('pyc', 'py')
        self.validacao_pep8([arquivo])

    def test_deve_verificar_pylint_no_modulo(self):
        arquivo = modulo_a_ser_validado.__file__.replace('pyc', 'py')
        self.validacao_pylint([arquivo])
```
