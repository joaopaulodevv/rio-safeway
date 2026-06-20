# testa_destaques.py - testes (por funções) do módulo destaques.py
#
# Cada caso de teste é uma função teste_*() que prepara o estado e devolve o
# valor a ser verificado. Reinicia Dataframe, Crime e Destaques e carrega
# conjuntos específicos para cada cenário.

import os
import tempfile
import unittest

import crime
import dataframe
from destaques import *

# Copa 3 (Roubo,Furto,Furto), Centro 2 (Furto,Roubo), Desconhecido 1 -> média 2
SAMPLE_MULTI = (
    "data,latitude,longitude,tipo_crime\n"
    "2024-01-01,-22.9700,-43.1850,Roubo\n"
    "2024-02-01,-22.9720,-43.1830,Furto\n"
    "2024-03-01,-22.9680,-43.1880,Furto\n"
    "2024-04-01,-22.9050,-43.1800,Furto\n"
    "2024-05-01,-22.9080,-43.1760,Roubo\n"
    "2024-06-01,-23.0600,-43.1800,Roubo\n"
)
# Copa 2, Centro 2 -> média 2, ninguém estritamente acima
SAMPLE_IGUAL = (
    "data,latitude,longitude,tipo_crime\n"
    "2024-01-01,-22.9700,-43.1850,Roubo\n"
    "2024-02-01,-22.9720,-43.1830,Furto\n"
    "2024-03-01,-22.9050,-43.1800,Furto\n"
    "2024-04-01,-22.9080,-43.1760,Roubo\n"
)
# Apenas Copacabana -> 1 bairro
SAMPLE_UM_BAIRRO = (
    "data,latitude,longitude,tipo_crime\n"
    "2024-01-01,-22.9700,-43.1850,Roubo\n"
    "2024-02-01,-22.9720,-43.1830,Furto\n"
    "2024-03-01,-22.9680,-43.1880,Furto\n"
)
# Copacabana com empate Furto 1 x Roubo 1
SAMPLE_EMPATE = (
    "data,latitude,longitude,tipo_crime\n"
    "2024-01-01,-22.9700,-43.1850,Furto\n"
    "2024-02-01,-22.9720,-43.1830,Roubo\n"
)


def carregar_sample(texto):
    """Reseta Dataframe, Crime e Destaques e carrega o CSV informado."""
    caminho = os.path.join(tempfile.mkdtemp(), "dados.csv")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)
    dataframe.resetar()
    crime.resetar()
    resetar()
    dataframe.carregar_dados(caminho)
    dataframe.filtra_dados_invalidos()
    dataframe.processar_coluna_bairros()


# ---------------- calcular_bairro_alerta / obter_bairro_alerta ----------------

def teste_bairro_alerta_identificado():
    carregar_sample(SAMPLE_MULTI)
    return calcular_bairro_alerta()


def teste_bairro_alerta_valor():
    carregar_sample(SAMPLE_MULTI)
    calcular_bairro_alerta()
    return obter_bairro_alerta()


def teste_bairro_alerta_nenhum():
    carregar_sample(SAMPLE_IGUAL)
    return calcular_bairro_alerta()


def teste_bairro_alerta_um_bairro():
    carregar_sample(SAMPLE_UM_BAIRRO)
    return calcular_bairro_alerta()


def teste_obter_alerta_antes_de_calcular():
    resetar()
    return obter_bairro_alerta()


# ---------------- calcular/obter_top_crime_pbairro ----------------

def teste_top_crime_existente():
    carregar_sample(SAMPLE_MULTI)
    calcular_top_crime_pbairro("Copacabana")
    return obter_top_crime_pbairro("Copacabana")


def teste_top_crime_empate():
    carregar_sample(SAMPLE_EMPATE)
    calcular_top_crime_pbairro("Copacabana")
    return obter_top_crime_pbairro("Copacabana")


def teste_top_crime_inexistente():
    carregar_sample(SAMPLE_MULTI)
    return calcular_top_crime_pbairro("Atlântida")


def teste_obter_top_antes_de_calcular():
    resetar()
    return obter_top_crime_pbairro("Copacabana")


def verifica(funcao, esperado):
    retorno = funcao()
    assert retorno == esperado, f"esperado {esperado!r}, obtido {retorno!r}"


def monta_testes():
    testes = unittest.TestSuite()
    casos = [
        (teste_bairro_alerta_identificado, DEST_CondRet.OK),
        (teste_bairro_alerta_valor, (DEST_CondRet.OK, "Copacabana", 3)),
        (teste_bairro_alerta_nenhum, DEST_CondRet.FALHA),
        (teste_bairro_alerta_um_bairro, DEST_CondRet.ERRO),
        (teste_obter_alerta_antes_de_calcular, (DEST_CondRet.FALHA, None, 0)),
        (teste_top_crime_existente, (DEST_CondRet.OK, "Furto")),
        (teste_top_crime_empate, (DEST_CondRet.OK, "Furto e Roubo")),
        (teste_top_crime_inexistente, DEST_CondRet.FALHA),
        (teste_obter_top_antes_de_calcular, (DEST_CondRet.FALHA, None)),
    ]
    for funcao, esperado in casos:
        testes.addTest(unittest.FunctionTestCase(
            lambda f=funcao, e=esperado: verifica(f, e)))
    return testes


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(monta_testes())
