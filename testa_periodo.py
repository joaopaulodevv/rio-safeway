# testa_periodo.py - testes (por funções) do módulo periodo.py
#
# Cada caso de teste é uma função teste_*() que prepara o estado e devolve o
# valor a ser verificado. O Dataframe é reiniciado e carregado quando o teste
# precisa da visão ativa (o filtro de período opera sobre ela).

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


def carregar_sample():
    """Reseta Dataframe e Período e carrega o CSV de exemplo."""
    caminho = os.path.join(tempfile.mkdtemp(), "dados.csv")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(SAMPLE)
    dataframe.resetar()
    resetar()
    dataframe.carregar_dados(caminho)
    dataframe.processar_coluna_bairros()


def contar_ativo():
    qtd = 0
    while dataframe.obter_registro(qtd)[0] == dataframe.DF_CondRet.OK:
        qtd += 1
    return qtd


# ---------------- valida_periodo ----------------

def teste_valida_periodo_valido():
    return valida_periodo("2024-01-01", "2024-12-31")


def teste_valida_datas_invertidas():
    return valida_periodo("2024-12-31", "2024-01-01")


def teste_valida_limite_um_dia():
    return valida_periodo("2024-05-15", "2024-05-15")


def teste_valida_tipagem():
    return valida_periodo(123, 456)


def teste_valida_formato():
    return valida_periodo("ontem", "hoje")


def teste_valida_nulo():
    return valida_periodo(None, "2024-12-31")


# ---------------- aplicar_filtro_periodo ----------------

def teste_aplicar_com_ocorrencias():
    carregar_sample()
    return aplicar_filtro_periodo("2024-01-01", "2024-12-31")


def teste_aplicar_conta():
    carregar_sample()
    aplicar_filtro_periodo("2024-01-01", "2024-12-31")
    return contar_ativo()


def teste_aplicar_falha_validacao():
    carregar_sample()
    return aplicar_filtro_periodo("2024-12-31", "2024-01-01")


def teste_aplicar_sem_ocorrencias():
    carregar_sample()
    return aplicar_filtro_periodo("2030-01-01", "2030-12-31")


# ---------------- limpar_filtro_periodo ----------------

def teste_limpar_restaura():
    carregar_sample()
    aplicar_filtro_periodo("2030-01-01", "2030-12-31")
    limpar_filtro_periodo()
    return contar_ativo()


def verifica(funcao, esperado):
    retorno = funcao()
    assert retorno == esperado, f"esperado {esperado!r}, obtido {retorno!r}"


def monta_testes():
    testes = unittest.TestSuite()
    casos = [
        (teste_valida_periodo_valido, PER_CondRet.OK),
        (teste_valida_datas_invertidas, PER_CondRet.FALHA),
        (teste_valida_limite_um_dia, PER_CondRet.FALHA),
        (teste_valida_tipagem, PER_CondRet.ERRO),
        (teste_valida_formato, PER_CondRet.ERRO),
        (teste_valida_nulo, PER_CondRet.ERRO),
        (teste_aplicar_com_ocorrencias, PER_CondRet.OK),
        (teste_aplicar_conta, 3),
        (teste_aplicar_falha_validacao, PER_CondRet.FALHA),
        (teste_aplicar_sem_ocorrencias, PER_CondRet.ERRO),
        (teste_limpar_restaura, 3),
    ]
    for funcao, esperado in casos:
        testes.addTest(unittest.FunctionTestCase(
            lambda f=funcao, e=esperado: verifica(f, e)))
    return testes


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(monta_testes())
