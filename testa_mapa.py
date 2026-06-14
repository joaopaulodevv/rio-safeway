"""
Programa testador do módulo Mapa — Rio SafeWay.

Como plot_bubbleMap, plot_heatMap e plot_scatterPlotMap têm a mesma assinatura
e o mesmo propósito-base, os cenários previstos (seção 5.1) são aplicados às
três funções. Os mapas são gerados em um diretório temporário.
"""

import tempfile
import unittest

import pandas as pd

import mapa

FUNCOES = [mapa.plot_bubbleMap, mapa.plot_heatMap, mapa.plot_scatterPlotMap]


def _df_coords(lats, lons):
    return pd.DataFrame({"latitude": lats, "longitude": lons})


class TestPlotMapas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mapa.definir_dir_saida(tempfile.mkdtemp())

    def test_caminho_feliz(self):
        df = _df_coords([-22.97, -22.90, -22.95], [-43.18, -43.18, -43.18])
        for funcao in FUNCOES:
            self.assertTrue(funcao(df), msg=funcao.__name__)

    def test_tabela_vazia(self):
        df = _df_coords([], [])
        for funcao in FUNCOES:
            self.assertFalse(funcao(df), msg=funcao.__name__)

    def test_ausencia_colunas_geograficas(self):
        df = pd.DataFrame({"tipo_crime": ["Roubo", "Furto"]})
        for funcao in FUNCOES:
            with self.assertRaises(KeyError, msg=funcao.__name__):
                funcao(df)

    def test_coordenadas_parcialmente_corrompidas(self):
        lats = [-22.97, -22.90, None, float("nan"), -22.95]
        lons = [-43.18, -43.18, -43.18, -43.18, None]
        df = _df_coords(lats, lons)
        for funcao in FUNCOES:
            self.assertTrue(funcao(df), msg=funcao.__name__)

    def test_corrupcao_total(self):
        df = _df_coords([None, float("nan")], [None, float("nan")])
        for funcao in FUNCOES:
            self.assertFalse(funcao(df), msg=funcao.__name__)


if __name__ == "__main__":
    unittest.main()
