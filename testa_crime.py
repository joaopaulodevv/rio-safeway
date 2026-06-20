# testa_crime.py - testes (por funções) do módulo crime.py
#
# Cada caso de teste é uma função teste_*() que prepara o estado e devolve o
# valor a ser verificado. O Dataframe é reiniciado e carregado a cada teste.

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


def carregar_sample(processar_bairros=True):
    """Reseta Dataframe e Crime e carrega o CSV de exemplo."""
    caminho = os.path.join(tempfile.mkdtemp(), "dados.csv")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(SAMPLE)
    dataframe.resetar()
    resetar()
    dataframe.carregar_dados(caminho)
    dataframe.filtra_dados_invalidos()
    if processar_bairros:
        dataframe.processar_coluna_bairros()


def contar_ativo():
    qtd = 0
    while dataframe.obter_registro(qtd)[0] == dataframe.DF_CondRet.OK:
        qtd += 1
    return qtd


# ---------------- aplicar_filtro_crime ----------------

def teste_filtro_com_registros():
    carregar_sample()
    return aplicar_filtro_crime("Furto")


def teste_filtro_conta():
    carregar_sample()
    aplicar_filtro_crime("Furto")
    return contar_ativo()


def teste_filtro_string_invalida():
    carregar_sample()
    return aplicar_filtro_crime("")


def teste_filtro_crime_sem_ocorrencias():
    carregar_sample()
    return aplicar_filtro_crime("Sequestro")


# ---------------- limpar_filtro_crime ----------------

def teste_limpar_restaura():
    carregar_sample()
    aplicar_filtro_crime("Furto")
    limpar_filtro_crime()
    return contar_ativo()


# ---------------- processar_contagem_tpCrime ----------------

def teste_contagem_tpcrime_gerada():
    carregar_sample()
    return processar_contagem_tpCrime()


def teste_contagem_tpcrime_valor():
    carregar_sample()
    processar_contagem_tpCrime()
    return obter_qtd_crime("Furto")


def teste_contagem_tpcrime_visao_vazia():
    carregar_sample()
    aplicar_filtro_crime("Sequestro")
    return processar_contagem_tpCrime()


# ---------------- processar_contagem_bairro ----------------

def teste_contagem_bairro_gerada():
    carregar_sample()
    return processar_contagem_bairro()


def teste_contagem_bairro_valor():
    carregar_sample()
    processar_contagem_bairro()
    return obter_qtd_bairro("Copacabana")


def teste_contagem_bairro_coluna_nao_processada():
    carregar_sample(processar_bairros=False)
    return processar_contagem_bairro()


# ---------------- obter_qtd_crime ----------------

def teste_obter_qtd_crime_listado():
    carregar_sample()
    processar_contagem_tpCrime()
    return obter_qtd_crime("Furto")


def teste_obter_qtd_crime_nao_listado():
    carregar_sample()
    processar_contagem_tpCrime()
    return obter_qtd_crime("Homicídio")


def verifica(funcao, esperado):
    retorno = funcao()
    assert retorno == esperado, f"esperado {esperado!r}, obtido {retorno!r}"


def monta_testes():
    testes = unittest.TestSuite()
    casos = [
        (teste_filtro_com_registros, CRIME_CondRet.OK),
        (teste_filtro_conta, 3),
        (teste_filtro_string_invalida, CRIME_CondRet.FALHA),
        (teste_filtro_crime_sem_ocorrencias, CRIME_CondRet.ERRO),
        (teste_limpar_restaura, 6),
        (teste_contagem_tpcrime_gerada, CRIME_CondRet.OK),
        (teste_contagem_tpcrime_valor, (CRIME_CondRet.OK, 3)),
        (teste_contagem_tpcrime_visao_vazia, CRIME_CondRet.FALHA),
        (teste_contagem_bairro_gerada, CRIME_CondRet.OK),
        (teste_contagem_bairro_valor, (CRIME_CondRet.OK, 3)),
        (teste_contagem_bairro_coluna_nao_processada, CRIME_CondRet.ERRO),
        (teste_obter_qtd_crime_listado, (CRIME_CondRet.OK, 3)),
        (teste_obter_qtd_crime_nao_listado, (CRIME_CondRet.FALHA, 0)),
    ]
    for funcao, esperado in casos:
        testes.addTest(unittest.FunctionTestCase(
            lambda f=funcao, e=esperado: verifica(f, e)))
    return testes


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(monta_testes())
