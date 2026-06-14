"""
Programa testador do módulo Período — Rio SafeWay.

Cobre os cenários previstos na especificação (seção 5.1) para as funções
valida_periodo e filtra_dfPeriodo, incluindo seus retornos e exceções.
"""

import unittest

import pandas as pd

import periodo


def _df_exemplo():
    """DataFrame com ocorrências distribuídas ao longo de 2024 e 2025."""
    datas = pd.to_datetime([
        "2024-01-10", "2024-04-15", "2024-07-20",
        "2024-10-05", "2025-02-14", "2025-08-30",
    ])
    return pd.DataFrame({
        "data": datas,
        "latitude": [-22.97] * 6,
        "longitude": [-43.18] * 6,
        "tipo_crime": ["Roubo"] * 6,
    })


class TestValidaPeriodo(unittest.TestCase):
    def setUp(self):
        self.df = _df_exemplo()

    def test_caminho_feliz(self):
        self.assertTrue(periodo.valida_periodo(
            self.df, pd.Timestamp("2024-01-01"), pd.Timestamp("2024-12-31")))

    def test_datas_invertidas(self):
        self.assertFalse(periodo.valida_periodo(
            self.df, pd.Timestamp("2024-12-31"), pd.Timestamp("2024-01-01")))

    def test_unico_dia(self):
        dia = pd.Timestamp("2024-07-20")
        self.assertTrue(periodo.valida_periodo(self.df, dia, dia))

    def test_fora_do_escopo(self):
        self.assertFalse(periodo.valida_periodo(
            self.df, pd.Timestamp("1990-01-01"), pd.Timestamp("1990-12-31")))

    def test_tipagem_incorreta(self):
        with self.assertRaises(TypeError):
            periodo.valida_periodo(self.df, "01/01/2026", "31/12/2026")

    def test_parametros_nulos(self):
        self.assertFalse(periodo.valida_periodo(self.df, None, pd.Timestamp("2024-12-31")))
        self.assertFalse(periodo.valida_periodo(self.df, pd.Timestamp("2024-01-01"), None))


class TestFiltraDfPeriodo(unittest.TestCase):
    def setUp(self):
        self.df = _df_exemplo()

    def test_recorte_perfeito(self):
        resultado = periodo.filtra_dfPeriodo(
            self.df, pd.Timestamp("2024-01-01"), pd.Timestamp("2024-12-31"))
        self.assertEqual(len(resultado), 4)
        self.assertGreaterEqual(resultado["data"].min(), pd.Timestamp("2024-01-01"))
        self.assertLessEqual(resultado["data"].max(), pd.Timestamp("2024-12-31"))

    def test_periodo_sem_ocorrencias(self):
        resultado = periodo.filtra_dfPeriodo(
            self.df, pd.Timestamp("2024-05-01"), pd.Timestamp("2024-05-31"))
        self.assertTrue(resultado.empty)
        for coluna in ["data", "latitude", "longitude", "tipo_crime"]:
            self.assertIn(coluna, resultado.columns)

    def test_periodo_nao_validado(self):
        resultado = periodo.filtra_dfPeriodo(
            self.df, pd.Timestamp("2024-12-31"), pd.Timestamp("2024-01-01"))
        self.assertEqual(len(resultado), len(self.df))


if __name__ == "__main__":
    unittest.main()
