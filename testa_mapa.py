"""
Programa testador do módulo Mapa — Rio SafeWay.

Como plot_bubbleMap, plot_heatMap e plot_scatterPlotMap têm a mesma assinatura
e o mesmo propósito-base, os mesmos cenários (códigos de retorno) são aplicados
às três. Os mapas são gravados em diretório temporário. O Dataframe é
reiniciado e carregado a cada teste, pois os mapas consomem a visão ativa.
"""

import os
import tempfile
import unittest

import dataframe
import mapa

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

FUNCOES = [mapa.plot_bubbleMap, mapa.plot_heatMap, mapa.plot_scatterPlotMap]


def _carregar(texto, limpar=True):
    caminho = os.path.join(tempfile.mkdtemp(), "dados.csv")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)
    dataframe.resetar()
    dataframe.carregar_dados(caminho)
    if limpar:
        dataframe.filtra_dados_invalidos()


class TestPlotMapas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mapa.definir_dir_saida(tempfile.mkdtemp())

    def test_gerado_com_sucesso(self):
        _carregar(SAMPLE)
        for funcao in FUNCOES:
            self.assertEqual(funcao(), mapa.MAPA_CondRet.OK, msg=funcao.__name__)

    def test_base_ativa_vazia(self):
        _carregar(SAMPLE)
        dataframe.aplicar_filtro_interno("tipo_crime", "Sequestro", "Sequestro")
        for funcao in FUNCOES:
            self.assertEqual(funcao(), mapa.MAPA_CondRet.FALHA, msg=funcao.__name__)

    def test_coordenadas_corrompidas(self):
        _carregar(SAMPLE_SEM_COORDS, limpar=False)
        for funcao in FUNCOES:
            self.assertEqual(funcao(), mapa.MAPA_CondRet.ERRO, msg=funcao.__name__)


if __name__ == "__main__":
    unittest.main()
