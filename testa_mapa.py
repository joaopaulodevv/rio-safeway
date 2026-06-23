# testa_mapa.py - testes (por funções) do módulo mapa.py
#
# Estilo da referência  UMA função de teste por função de
# plotagem. Cada teste_*() exercita os DIFERENTES retornos daquela função
# (1 OK, 0 FALHA, -1 ERRO), compara cada um com o esperado e DEVOLVE 0 (passou)
# ou 1 (falhou). monta_testes() confere que todos devolvem 0. Os mapas são
# gravados em diretório temporário.

import os
import tempfile
import unittest

import dataframe
from mapa import *

SAMPLE = (
    "data,latitude,longitude,tipo_crime\n"
    "2024-01-01,-22.9700,-43.1850,Roubo\n"
    "2024-02-01,-22.9050,-43.1800,Furto\n"
    "2024-03-01,-22.9250,-43.2320,Furto\n"
)
SAMPLE_SEM_COORDS = (
    "data,latitude,longitude,tipo_crime\n"
    "2024-01-01,,,Roubo\n"
    "2024-02-01,,,Furto\n"
)

definir_dir_saida(tempfile.mkdtemp())


def imprime_codigo(codigo):
    mensagens = {0: "passou (todos os retornos == esperado)",
                 1: "falhou (algum retorno != esperado)"}
    print(f"Codigo {codigo}: {mensagens[codigo]}")


def carregar_sample(texto, limpar=True):
    """Reseta o Dataframe e carrega o CSV informado."""
    caminho = os.path.join(tempfile.mkdtemp(), "dados.csv")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)
    dataframe.resetar()
    dataframe.carregar_dados(caminho)
    if limpar:
        dataframe.filtra_dados_invalidos()


def preparar_base_vazia():
    """Carrega a base e aplica um filtro que esvazia a visão ativa."""
    carregar_sample(SAMPLE)
    dataframe.aplicar_filtro_interno("tipo_crime", "Sequestro", "Sequestro")


def teste_plot_bubbleMap():
    carregar_sample(SAMPLE)
    r_ok = plot_bubbleMap()       # 1
    preparar_base_vazia()
    r_vazia = plot_bubbleMap()    # 0
    carregar_sample(SAMPLE_SEM_COORDS, limpar=False)
    r_corromp = plot_bubbleMap()  # -1
    if r_ok == 1 and r_vazia == 0 and r_corromp == -1:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_plot_heatMap():
    carregar_sample(SAMPLE)
    r_ok = plot_heatMap()       # 1
    preparar_base_vazia()
    r_vazia = plot_heatMap()    # 0
    carregar_sample(SAMPLE_SEM_COORDS, limpar=False)
    r_corromp = plot_heatMap()  # -1
    if r_ok == 1 and r_vazia == 0 and r_corromp == -1:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_plot_scatterPlotMap():
    carregar_sample(SAMPLE)
    r_ok = plot_scatterPlotMap()       # 1
    preparar_base_vazia()
    r_vazia = plot_scatterPlotMap()    # 0
    carregar_sample(SAMPLE_SEM_COORDS, limpar=False)
    r_corromp = plot_scatterPlotMap()  # -1
    if r_ok == 1 and r_vazia == 0 and r_corromp == -1:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def verifica(funcao, esperado):
    retorno = funcao()
    assert retorno == esperado, f"esperado {esperado!r}, obtido {retorno!r}"


def monta_testes():
    testes = unittest.TestSuite()
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_plot_bubbleMap, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_plot_heatMap, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_plot_scatterPlotMap, 0)))
    return testes


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(monta_testes())
