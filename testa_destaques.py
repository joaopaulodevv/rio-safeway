# testa_destaques.py - testes (por funções) do módulo destaques.py
#
# Reimplementado a partir da especificação de interfaces: cada função de acesso
# tem um teste para CADA código de retorno documentado (1 OK, 0 FALHA, -1 ERRO).
# No padrão do teste_livro.py, cada teste_*() executa a função, imprime o código
# e DEVOLVE o código de retorno, que verifica() confere contra o esperado.

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


def imprime_codigo(codigo):
    mensagens = {
        1: "OK - calculo realizado / variaveis copiadas",
        0: "FALHA - nada acima da media / nao consta / nao calculado ainda",
        -1: "ERRO - impossivel calcular media (0 ou 1 bairro na base)",
    }
    print(f"Codigo {int(codigo)}: {mensagens.get(codigo, 'desconhecido')}")


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


# ---------------- calcular_bairro_alerta (1 / 0 / -1) ----------------

def teste_calc_alerta_ok():
    carregar_sample(SAMPLE_MULTI)
    codigo = calcular_bairro_alerta()
    imprime_codigo(codigo)
    return codigo


def teste_calc_alerta_nenhum_acima():
    carregar_sample(SAMPLE_IGUAL)
    codigo = calcular_bairro_alerta()
    imprime_codigo(codigo)
    return codigo


def teste_calc_alerta_um_bairro():
    carregar_sample(SAMPLE_UM_BAIRRO)
    codigo = calcular_bairro_alerta()
    imprime_codigo(codigo)
    return codigo


# ---------------- obter_bairro_alerta (1 / 0) ----------------

def teste_obter_alerta_ok():
    carregar_sample(SAMPLE_MULTI)
    calcular_bairro_alerta()
    codigo = obter_bairro_alerta()[0]
    imprime_codigo(codigo)
    return codigo


def teste_obter_alerta_nao_processado():
    resetar()
    codigo = obter_bairro_alerta()[0]
    imprime_codigo(codigo)
    return codigo


# ---------------- calcular_top_crime_pbairro (1 / 0) ----------------

def teste_calc_top_ok():
    carregar_sample(SAMPLE_MULTI)
    codigo = calcular_top_crime_pbairro("Copacabana")
    imprime_codigo(codigo)
    return codigo


def teste_calc_top_bairro_nao_consta():
    carregar_sample(SAMPLE_MULTI)
    codigo = calcular_top_crime_pbairro("Atlantida")
    imprime_codigo(codigo)
    return codigo


# ---------------- obter_top_crime_pbairro (1 / 0) ----------------

def teste_obter_top_ok():
    carregar_sample(SAMPLE_MULTI)
    calcular_top_crime_pbairro("Copacabana")
    codigo = obter_top_crime_pbairro("Copacabana")[0]
    imprime_codigo(codigo)
    return codigo


def teste_obter_top_nao_calculado():
    resetar()
    codigo = obter_top_crime_pbairro("Copacabana")[0]
    imprime_codigo(codigo)
    return codigo


def verifica(funcao, esperado):
    retorno = funcao()
    assert retorno == esperado, f"esperado {esperado!r}, obtido {retorno!r}"


def monta_testes():
    testes = unittest.TestSuite()
    # calcular_bairro_alerta: 1 / 0 / -1
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_calc_alerta_ok, 1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_calc_alerta_nenhum_acima, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_calc_alerta_um_bairro, -1)))
    # obter_bairro_alerta: 1 / 0
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_obter_alerta_ok, 1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_obter_alerta_nao_processado, 0)))
    # calcular_top_crime_pbairro: 1 / 0
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_calc_top_ok, 1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_calc_top_bairro_nao_consta, 0)))
    # obter_top_crime_pbairro: 1 / 0
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_obter_top_ok, 1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_obter_top_nao_calculado, 0)))
    return testes


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(monta_testes())
