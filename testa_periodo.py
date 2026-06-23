# testa_periodo.py - testes (por funções) do módulo periodo.py
#
# Estilo da referência  UMA função de teste por função de
# acesso. Cada teste_*() exercita os DIFERENTES retornos daquela função
# (1 OK, 0 FALHA, -1 ERRO), compara cada um com o esperado e DEVOLVE 0 (passou)
# ou 1 (falhou). monta_testes() confere que todos devolvem 0.

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
    mensagens = {0: "passou (todos os retornos == esperado)",
                 1: "falhou (algum retorno != esperado)"}
    print(f"Codigo {codigo}: {mensagens[codigo]}")


def carregar_sample():
    """Reseta Dataframe e Período e carrega o CSV de exemplo."""
    caminho = os.path.join(tempfile.mkdtemp(), "dados.csv")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(SAMPLE)
    dataframe.resetar()
    resetar()
    dataframe.carregar_dados(caminho)
    dataframe.filtra_dados_invalidos()


def teste_valida_periodo():
    r_ok = valida_periodo("2024-01-01", "2024-12-31")     # 1
    r_invertidas = valida_periodo("2024-12-31", "2024-01-01")  # 0
    r_um_dia = valida_periodo("2024-05-15", "2024-05-15")  # 0
    r_tipagem = valida_periodo(123, 456)                   # -1
    r_formato = valida_periodo("ontem", "hoje")            # -1
    if (r_ok == 1 and r_invertidas == 0 and r_um_dia == 0
            and r_tipagem == -1 and r_formato == -1):
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_aplicar_filtro_periodo():
    carregar_sample()
    r_ok = aplicar_filtro_periodo("2024-01-01", "2024-12-31")  # 1
    carregar_sample()
    r_falha = aplicar_filtro_periodo("2024-12-31", "2024-01-01")  # 0
    carregar_sample()
    r_sem_ocorr = aplicar_filtro_periodo("2030-01-01", "2030-12-31")  # -1
    if r_ok == 1 and r_falha == 0 and r_sem_ocorr == -1:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_limpar_filtro_periodo():
    carregar_sample()
    aplicar_filtro_periodo("2030-01-01", "2030-12-31")
    r_ok = limpar_filtro_periodo()  # 1
    if r_ok == 1:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def verifica(funcao, esperado):
    retorno = funcao()
    assert retorno == esperado, f"esperado {esperado!r}, obtido {retorno!r}"


def monta_testes():
    testes = unittest.TestSuite()
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_valida_periodo, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_aplicar_filtro_periodo, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_limpar_filtro_periodo, 0)))
    return testes


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(monta_testes())
