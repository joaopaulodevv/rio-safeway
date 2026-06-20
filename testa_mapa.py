# testa_mapa.py - testes (por funções) do módulo mapa.py
#
# Como plot_bubbleMap, plot_heatMap e plot_scatterPlotMap têm a mesma assinatura
# e propósito-base, cada caso devolve a tripla de códigos das três funções, que
# é comparada com a tripla esperada. Os mapas são gravados em diretório temporário.

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


def carregar_sample(texto, limpar=True):
    """Reseta o Dataframe e carrega o CSV informado."""
    caminho = os.path.join(tempfile.mkdtemp(), "dados.csv")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)
    dataframe.resetar()
    dataframe.carregar_dados(caminho)
    if limpar:
        dataframe.filtra_dados_invalidos()


def codigos_dos_mapas():
    """Roda as três funções de mapa e devolve a tripla de códigos."""
    return (plot_bubbleMap(), plot_heatMap(), plot_scatterPlotMap())


# ---------------- plot_bubbleMap / plot_heatMap / plot_scatterPlotMap ----------------

def teste_mapas_sucesso():
    carregar_sample(SAMPLE)
    return codigos_dos_mapas()


def teste_mapas_base_vazia():
    carregar_sample(SAMPLE)
    dataframe.aplicar_filtro_interno("tipo_crime", "Sequestro", "Sequestro")
    return codigos_dos_mapas()


def teste_mapas_coords_corrompidas():
    carregar_sample(SAMPLE_SEM_COORDS, limpar=False)
    return codigos_dos_mapas()


def verifica(funcao, esperado):
    retorno = funcao()
    assert retorno == esperado, f"esperado {esperado!r}, obtido {retorno!r}"


def monta_testes():
    testes = unittest.TestSuite()
    ok = (MAPA_CondRet.OK, MAPA_CondRet.OK, MAPA_CondRet.OK)
    falha = (MAPA_CondRet.FALHA, MAPA_CondRet.FALHA, MAPA_CondRet.FALHA)
    erro = (MAPA_CondRet.ERRO, MAPA_CondRet.ERRO, MAPA_CondRet.ERRO)
    casos = [
        (teste_mapas_sucesso, ok),
        (teste_mapas_base_vazia, falha),
        (teste_mapas_coords_corrompidas, erro),
    ]
    for funcao, esperado in casos:
        testes.addTest(unittest.FunctionTestCase(
            lambda f=funcao, e=esperado: verifica(f, e)))
    return testes


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(monta_testes())
