# testa_destaques.py - testes (por funções) do módulo destaques.py
#
# Estilo da referência  UMA função de teste por função de
# acesso. Cada teste_*() exercita os DIFERENTES retornos daquela função
# (1 OK, 0 FALHA, -1 ERRO), compara cada um com o esperado e DEVOLVE 0 (passou)
# ou 1 (falhou). monta_testes() confere que todos devolvem 0.

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
    mensagens = {0: "passou (todos os retornos == esperado)",
                 1: "falhou (algum retorno != esperado)"}
    print(f"Codigo {codigo}: {mensagens[codigo]}")


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


def teste_calcular_bairro_alerta():
    carregar_sample(SAMPLE_MULTI)
    r_ok = calcular_bairro_alerta()        # 1
    carregar_sample(SAMPLE_IGUAL)
    r_nenhum = calcular_bairro_alerta()    # 0
    carregar_sample(SAMPLE_UM_BAIRRO)
    r_um_bairro = calcular_bairro_alerta()  # -1
    if r_ok == 1 and r_nenhum == 0 and r_um_bairro == -1:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_obter_bairro_alerta():
    carregar_sample(SAMPLE_MULTI)
    calcular_bairro_alerta()
    r_ok = obter_bairro_alerta()[0]  # 1
    resetar()
    r_nao_proc = obter_bairro_alerta()[0]  # 0
    if r_ok == 1 and r_nao_proc == 0:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_calcular_top_crime_pbairro():
    carregar_sample(SAMPLE_MULTI)
    r_ok = calcular_top_crime_pbairro("Copacabana")    # 1
    carregar_sample(SAMPLE_MULTI)
    r_nao_consta = calcular_top_crime_pbairro("Atlantida")  # 0
    if r_ok == 1 and r_nao_consta == 0:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_obter_top_crime_pbairro():
    carregar_sample(SAMPLE_MULTI)
    calcular_top_crime_pbairro("Copacabana")
    r_ok = obter_top_crime_pbairro("Copacabana")[0]  # 1
    resetar()
    r_nao_calc = obter_top_crime_pbairro("Copacabana")[0]  # 0
    if r_ok == 1 and r_nao_calc == 0:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def verifica(funcao, esperado):
    retorno = funcao()
    assert retorno == esperado, f"esperado {esperado!r}, obtido {retorno!r}"


def monta_testes():
    testes = unittest.TestSuite()
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_calcular_bairro_alerta, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_obter_bairro_alerta, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_calcular_top_crime_pbairro, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_obter_top_crime_pbairro, 0)))
    return testes


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(monta_testes())
