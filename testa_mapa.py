# testa_mapa.py - testes (por funções) do módulo mapa.py
#
# Reimplementado a partir da especificação de interfaces: cada função de plotagem
# (plot_bubbleMap, plot_heatMap, plot_scatterPlotMap) tem um teste para CADA
# código de retorno documentado (1 OK, 0 FALHA, -1 ERRO). No padrão do
# teste_livro.py, cada teste_*() executa a função, imprime o código e DEVOLVE o
# código de retorno, que verifica() confere contra o esperado. Os mapas são
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
    mensagens = {
        1: "OK - mapa gerado com sucesso",
        0: "FALHA - base ativa vazia (abortado)",
        -1: "ERRO - coordenadas ausentes/corrompidas (erro fatal)",
    }
    print(f"Codigo {int(codigo)}: {mensagens.get(codigo, 'desconhecido')}")


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


# ---------------- plot_bubbleMap (1 / 0 / -1) ----------------

def teste_bubble_ok():
    carregar_sample(SAMPLE)
    codigo = plot_bubbleMap()
    imprime_codigo(codigo)
    return codigo


def teste_bubble_base_vazia():
    preparar_base_vazia()
    codigo = plot_bubbleMap()
    imprime_codigo(codigo)
    return codigo


def teste_bubble_coords_corrompidas():
    carregar_sample(SAMPLE_SEM_COORDS, limpar=False)
    codigo = plot_bubbleMap()
    imprime_codigo(codigo)
    return codigo


# ---------------- plot_heatMap (1 / 0 / -1) ----------------

def teste_heat_ok():
    carregar_sample(SAMPLE)
    codigo = plot_heatMap()
    imprime_codigo(codigo)
    return codigo


def teste_heat_base_vazia():
    preparar_base_vazia()
    codigo = plot_heatMap()
    imprime_codigo(codigo)
    return codigo


def teste_heat_coords_corrompidas():
    carregar_sample(SAMPLE_SEM_COORDS, limpar=False)
    codigo = plot_heatMap()
    imprime_codigo(codigo)
    return codigo


# ---------------- plot_scatterPlotMap (1 / 0 / -1) ----------------

def teste_scatter_ok():
    carregar_sample(SAMPLE)
    codigo = plot_scatterPlotMap()
    imprime_codigo(codigo)
    return codigo


def teste_scatter_base_vazia():
    preparar_base_vazia()
    codigo = plot_scatterPlotMap()
    imprime_codigo(codigo)
    return codigo


def teste_scatter_coords_corrompidas():
    carregar_sample(SAMPLE_SEM_COORDS, limpar=False)
    codigo = plot_scatterPlotMap()
    imprime_codigo(codigo)
    return codigo


def verifica(funcao, esperado):
    retorno = funcao()
    assert retorno == esperado, f"esperado {esperado!r}, obtido {retorno!r}"


def monta_testes():
    testes = unittest.TestSuite()
    # plot_bubbleMap: 1 / 0 / -1
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_bubble_ok, 1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_bubble_base_vazia, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_bubble_coords_corrompidas, -1)))
    # plot_heatMap: 1 / 0 / -1
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_heat_ok, 1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_heat_base_vazia, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_heat_coords_corrompidas, -1)))
    # plot_scatterPlotMap: 1 / 0 / -1
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_scatter_ok, 1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_scatter_base_vazia, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_scatter_coords_corrompidas, -1)))
    return testes


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(monta_testes())
