"""
Programa testador do módulo Dataframe — Rio SafeWay.

Cobre os cenários previstos na especificação (seção 5.1) para cada função de
acesso: carregar_dados, filtra_dados, adiciona_dado, remove_dados e
coluna_bairros, incluindo seus retornos e exceções possíveis.
"""

import os
import tempfile
import unittest

import pandas as pd

import dataframe


def _df_exemplo():
    """DataFrame limpo de exemplo, com coordenadas válidas do Rio."""
    return pd.DataFrame({
        "data": pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01"]),
        "latitude": [-22.9700, -22.9050, -22.9250],
        "longitude": [-43.1850, -43.1800, -43.2320],
        "tipo_crime": ["Roubo", "Furto", "Furto"],
    })


class TestCarregarDados(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def _caminho(self, nome):
        return os.path.join(self.dir, nome)

    def test_caminho_feliz(self):
        caminho = self._caminho("dados_crimes.csv")
        _df_exemplo().to_csv(caminho, index=False)
        df = dataframe.carregar_dados(caminho)
        self.assertEqual(len(df), 3)
        for coluna in dataframe.COLUNAS_OBRIGATORIAS:
            self.assertIn(coluna, df.columns)

    def test_arquivo_inexistente(self):
        with self.assertRaises(FileNotFoundError):
            dataframe.carregar_dados(self._caminho("nao_existe.csv"))

    def test_arquivo_vazio_so_cabecalho(self):
        caminho = self._caminho("dados_vazios.csv")
        with open(caminho, "w", encoding="utf-8") as f:
            f.write("data,latitude,longitude,tipo_crime\n")
        df = dataframe.carregar_dados(caminho)
        self.assertTrue(df.empty)
        for coluna in dataframe.COLUNAS_OBRIGATORIAS:
            self.assertIn(coluna, df.columns)

    def test_formato_incorreto(self):
        caminho = self._caminho("foto_gato.csv")
        with open(caminho, "w", encoding="utf-8") as f:
            f.write("coluna_a,coluna_b\n1,2\n3,4\n")
        with self.assertRaises(ValueError):
            dataframe.carregar_dados(caminho)


class TestFiltraDados(unittest.TestCase):
    def test_tabela_limpa(self):
        df = _df_exemplo()
        resultado = dataframe.filtra_dados(df)
        self.assertEqual(len(resultado), len(df))

    def test_tabela_com_nulos(self):
        df = pd.DataFrame({
            "data": [pd.Timestamp("2024-01-01"), None, pd.Timestamp("2024-03-01")],
            "latitude": [-22.97, -22.90, None],
            "longitude": [-43.18, -43.18, -43.23],
            "tipo_crime": ["Roubo", "Furto", "Furto"],
        })
        resultado = dataframe.filtra_dados(df)
        self.assertEqual(len(resultado), 1)


class TestAdicionaDado(unittest.TestCase):
    def test_caminho_feliz(self):
        df = _df_exemplo()
        resultado = dataframe.adiciona_dado(
            df, pd.Timestamp("2025-01-01"), "-22.97", "-43.18", "Roubo")
        self.assertEqual(len(resultado), len(df) + 1)
        self.assertEqual(resultado.iloc[-1]["tipo_crime"], "Roubo")

    def test_parametro_vazio(self):
        df = _df_exemplo()
        with self.assertRaises(ValueError):
            dataframe.adiciona_dado(df, pd.Timestamp("2025-01-01"), "-22.97", "-43.18", "")
        with self.assertRaises(ValueError):
            dataframe.adiciona_dado(df, pd.Timestamp("2025-01-01"), None, "-43.18", "Roubo")

    def test_tipo_data_incorreto(self):
        df = _df_exemplo()
        with self.assertRaises(TypeError):
            dataframe.adiciona_dado(df, "ontem", "-22.97", "-43.18", "Roubo")

    def test_coordenadas_absurdas(self):
        df = _df_exemplo()
        with self.assertRaises(ValueError):
            dataframe.adiciona_dado(df, pd.Timestamp("2025-01-01"), "999.999", "888.888", "Roubo")

    def test_dado_duplicado(self):
        df = _df_exemplo()
        resultado = dataframe.adiciona_dado(
            df, pd.Timestamp("2025-01-01"), "-22.97", "-43.18", "Roubo")
        resultado = dataframe.adiciona_dado(
            resultado, pd.Timestamp("2025-01-01"), "-22.97", "-43.18", "Roubo")
        self.assertEqual(len(resultado), len(df) + 2)


class TestRemoveDados(unittest.TestCase):
    def test_remocao_especifica(self):
        df = _df_exemplo()
        resultado = dataframe.remove_dados(
            df, data=pd.Timestamp("2024-01-01"), latitude=-22.9700,
            longitude=-43.1850, tipo_crime="Roubo")
        self.assertEqual(len(resultado), len(df) - 1)

    def test_remocao_em_massa(self):
        df = _df_exemplo()
        resultado = dataframe.remove_dados(df, tipo_crime="Furto")
        self.assertFalse((resultado["tipo_crime"] == "Furto").any())

    def test_dado_nao_encontrado(self):
        df = _df_exemplo()
        resultado = dataframe.remove_dados(df, tipo_crime="Sequestro")
        self.assertEqual(len(resultado), len(df))

    def test_tudo_vazio(self):
        df = _df_exemplo()
        with self.assertRaises(ValueError):
            dataframe.remove_dados(df)


class TestColunaBairros(unittest.TestCase):
    def test_caminho_feliz(self):
        df = _df_exemplo()
        resultado = dataframe.coluna_bairros(df)
        self.assertIn("bairro", resultado.columns)
        self.assertEqual(len(resultado.columns), len(df.columns) + 1)
        self.assertEqual(resultado.iloc[0]["bairro"], "Copacabana")

    def test_coordenada_nao_mapeada(self):
        df = pd.DataFrame({
            "data": pd.to_datetime(["2024-01-01"]),
            "latitude": [-23.0600],
            "longitude": [-43.1800],
            "tipo_crime": ["Roubo"],
        })
        resultado = dataframe.coluna_bairros(df)
        self.assertEqual(resultado.iloc[0]["bairro"], "Desconhecido")

    def test_tabela_vazia(self):
        df = pd.DataFrame(columns=dataframe.COLUNAS_OBRIGATORIAS)
        resultado = dataframe.coluna_bairros(df)
        self.assertTrue(resultado.empty)
        self.assertIn("bairro", resultado.columns)


if __name__ == "__main__":
    unittest.main()
