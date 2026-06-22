# testa_crime.py - testes (por funções) do módulo crime.py
#
# Reimplementado a partir da especificação de interfaces: cada função de acesso
# tem um teste para CADA código de retorno documentado (1 OK, 0 FALHA, -1 ERRO).
# No padrão do teste_livro.py, cada teste_*() executa a função, imprime o código
# e DEVOLVE o código de retorno, que verifica() confere contra o esperado.

import os
import tempfile
import unittest

import dataframe
from crime import *

SAMPLE = (
    "data,latitude,longitude,tipo_crime\n"
    "2024-01-01,-22.9700,-43.1850,Roubo\n"
    "2024-02-01,-22.9720,-43.1830,Furto\n"
    "2024-03-01,-22.9680,-43.1880,Furto\n"
    "2024-04-01,-22.9050,-43.1800,Furto\n"
    "2024-05-01,-22.9080,-43.1760,Roubo\n"
    "2024-06-01,-23.0600,-43.1800,Roubo\n"
)


def imprime_codigo(codigo):
    mensagens = {
        1: "OK - operacao concluida com sucesso",
        0: "FALHA - visao vazia / string invalida / nao listado",
        -1: "ERRO - sem ocorrencias do crime / coluna bairro nao processada",
    }
    print(f"Codigo {int(codigo)}: {mensagens.get(codigo, 'desconhecido')}")


def carregar_sample(bairros=True):
    """Reseta Dataframe e Crime e carrega o CSV de exemplo."""
    caminho = os.path.join(tempfile.mkdtemp(), "dados.csv")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(SAMPLE)
    dataframe.resetar()
    resetar()
    dataframe.carregar_dados(caminho)
    dataframe.filtra_dados_invalidos()
    if bairros:
        dataframe.processar_coluna_bairros()


# ---------------- aplicar_filtro_crime (1 / 0 / -1) ----------------

def teste_filtro_crime_ok():
    carregar_sample()
    codigo = aplicar_filtro_crime("Furto")
    imprime_codigo(codigo)
    return codigo


def teste_filtro_crime_string_invalida():
    carregar_sample()
    codigo = aplicar_filtro_crime("")
    imprime_codigo(codigo)
    return codigo


def teste_filtro_crime_sem_ocorrencias():
    carregar_sample()
    codigo = aplicar_filtro_crime("Sequestro")
    imprime_codigo(codigo)
    return codigo


# ---------------- limpar_filtro_crime (1) ----------------

def teste_limpar_crime_ok():
    carregar_sample()
    aplicar_filtro_crime("Furto")
    codigo = limpar_filtro_crime()
    imprime_codigo(codigo)
    return codigo


# ---------------- processar_contagem_tpCrime (1 / 0) ----------------

def teste_contagem_tpcrime_ok():
    carregar_sample()
    codigo = processar_contagem_tpCrime()
    imprime_codigo(codigo)
    return codigo


def teste_contagem_tpcrime_visao_vazia():
    carregar_sample()
    aplicar_filtro_crime("Sequestro")  # esvazia a visão ativa
    codigo = processar_contagem_tpCrime()
    imprime_codigo(codigo)
    return codigo


# ---------------- processar_contagem_bairro (1 / 0 / -1) ----------------

def teste_contagem_bairro_ok():
    carregar_sample()
    codigo = processar_contagem_bairro()
    imprime_codigo(codigo)
    return codigo


def teste_contagem_bairro_visao_vazia():
    carregar_sample()
    aplicar_filtro_crime("Sequestro")  # esvazia a visão ativa
    codigo = processar_contagem_bairro()
    imprime_codigo(codigo)
    return codigo


def teste_contagem_bairro_coluna_nao_processada():
    carregar_sample(bairros=False)
    codigo = processar_contagem_bairro()
    imprime_codigo(codigo)
    return codigo


# ---------------- obter_qtd_crime (1 / 0) ----------------

def teste_obter_qtd_crime_listado():
    carregar_sample()
    processar_contagem_tpCrime()
    codigo = obter_qtd_crime("Furto")[0]
    imprime_codigo(codigo)
    return codigo


def teste_obter_qtd_crime_nao_listado():
    carregar_sample()
    processar_contagem_tpCrime()
    codigo = obter_qtd_crime("Homicidio")[0]
    imprime_codigo(codigo)
    return codigo


# ---------------- obter_qtd_bairro (1 / 0) ----------------

def teste_obter_qtd_bairro_listado():
    carregar_sample()
    processar_contagem_bairro()
    codigo = obter_qtd_bairro("Copacabana")[0]
    imprime_codigo(codigo)
    return codigo


def teste_obter_qtd_bairro_nao_listado():
    carregar_sample()
    processar_contagem_bairro()
    codigo = obter_qtd_bairro("Atlantida")[0]
    imprime_codigo(codigo)
    return codigo


# ---------------- obter_lista_crimes / obter_lista_bairros (1) ----------------

def teste_obter_lista_crimes_ok():
    carregar_sample()
    processar_contagem_tpCrime()
    codigo = obter_lista_crimes()[0]
    imprime_codigo(codigo)
    return codigo


def teste_obter_lista_bairros_ok():
    carregar_sample()
    processar_contagem_bairro()
    codigo = obter_lista_bairros()[0]
    imprime_codigo(codigo)
    return codigo


def verifica(funcao, esperado):
    retorno = funcao()
    assert retorno == esperado, f"esperado {esperado!r}, obtido {retorno!r}"


def monta_testes():
    testes = unittest.TestSuite()
    # aplicar_filtro_crime: 1 / 0 / -1
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_filtro_crime_ok, 1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_filtro_crime_string_invalida, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_filtro_crime_sem_ocorrencias, -1)))
    # limpar_filtro_crime: 1
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_limpar_crime_ok, 1)))
    # processar_contagem_tpCrime: 1 / 0
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_contagem_tpcrime_ok, 1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_contagem_tpcrime_visao_vazia, 0)))
    # processar_contagem_bairro: 1 / 0 / -1
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_contagem_bairro_ok, 1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_contagem_bairro_visao_vazia, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_contagem_bairro_coluna_nao_processada, -1)))
    # obter_qtd_crime: 1 / 0
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_obter_qtd_crime_listado, 1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_obter_qtd_crime_nao_listado, 0)))
    # obter_qtd_bairro: 1 / 0
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_obter_qtd_bairro_listado, 1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_obter_qtd_bairro_nao_listado, 0)))
    # obter_lista_crimes / obter_lista_bairros: 1
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_obter_lista_crimes_ok, 1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_obter_lista_bairros_ok, 1)))
    return testes


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(monta_testes())
