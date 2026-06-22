# testa_periodo.py - testes (por funções) do módulo periodo.py
#
# Reimplementado a partir da especificação de interfaces: cada função de acesso
# tem um teste para CADA código de retorno documentado (1 OK, 0 FALHA, -1 ERRO).
# No padrão do teste_livro.py, cada teste_*() executa a função, imprime o código
# e DEVOLVE o código de retorno, que verifica() confere contra o esperado.

import os
import tempfile
import unittest

import dataframe
from periodo import *

SAMPLE = (
    "data,latitude,longitude,tipo_crime\n"
    "2024-01-01,-22.9700,-43.1850,Roubo\n"
    "2024-03-01,-22.9720,-43.1830,Furto\n"
    "2024-06-01,-22.9050,-43.1800,Furto\n"
)


def imprime_codigo(codigo):
    mensagens = {
        1: "OK - periodo valido / filtro aplicado com ocorrencias",
        0: "FALHA - datas invertidas/limite de 1 dia / falha de validacao",
        -1: "ERRO - tipagem/formato invalido / aplicado sem ocorrencias",
    }
    print(f"Codigo {int(codigo)}: {mensagens.get(codigo, 'desconhecido')}")


def carregar_sample():
    """Reseta Dataframe e Período e carrega o CSV de exemplo."""
    caminho = os.path.join(tempfile.mkdtemp(), "dados.csv")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(SAMPLE)
    dataframe.resetar()
    resetar()
    dataframe.carregar_dados(caminho)
    dataframe.filtra_dados_invalidos()


# ---------------- valida_periodo (1 / 0 / -1) ----------------

def teste_valida_ok():
    codigo = valida_periodo("2024-01-01", "2024-12-31")
    imprime_codigo(codigo)
    return codigo


def teste_valida_datas_invertidas():
    codigo = valida_periodo("2024-12-31", "2024-01-01")
    imprime_codigo(codigo)
    return codigo


def teste_valida_limite_um_dia():
    codigo = valida_periodo("2024-05-15", "2024-05-15")
    imprime_codigo(codigo)
    return codigo


def teste_valida_tipagem():
    codigo = valida_periodo(123, 456)
    imprime_codigo(codigo)
    return codigo


def teste_valida_formato():
    codigo = valida_periodo("ontem", "hoje")
    imprime_codigo(codigo)
    return codigo


# ---------------- aplicar_filtro_periodo (1 / 0 / -1) ----------------

def teste_aplicar_com_ocorrencias():
    carregar_sample()
    codigo = aplicar_filtro_periodo("2024-01-01", "2024-12-31")
    imprime_codigo(codigo)
    return codigo


def teste_aplicar_falha_validacao():
    carregar_sample()
    codigo = aplicar_filtro_periodo("2024-12-31", "2024-01-01")
    imprime_codigo(codigo)
    return codigo


def teste_aplicar_sem_ocorrencias():
    carregar_sample()
    codigo = aplicar_filtro_periodo("2030-01-01", "2030-12-31")
    imprime_codigo(codigo)
    return codigo


# ---------------- limpar_filtro_periodo (1) ----------------

def teste_limpar_ok():
    carregar_sample()
    aplicar_filtro_periodo("2030-01-01", "2030-12-31")
    codigo = limpar_filtro_periodo()
    imprime_codigo(codigo)
    return codigo


def verifica(funcao, esperado):
    retorno = funcao()
    assert retorno == esperado, f"esperado {esperado!r}, obtido {retorno!r}"


def monta_testes():
    testes = unittest.TestSuite()
    # valida_periodo: 1 / 0 / 0 / -1 / -1
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_valida_ok, 1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_valida_datas_invertidas, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_valida_limite_um_dia, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_valida_tipagem, -1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_valida_formato, -1)))
    # aplicar_filtro_periodo: 1 / 0 / -1
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_aplicar_com_ocorrencias, 1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_aplicar_falha_validacao, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_aplicar_sem_ocorrencias, -1)))
    # limpar_filtro_periodo: 1
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_limpar_ok, 1)))
    return testes


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(monta_testes())
