"""
Programa testador do módulo Crime — Rio SafeWay.

Cobre os cenários previstos na especificação (seção 5.1) para as funções
df_crime_espec, conta_ocor_tpCrime e conta_ocor_bairro, incluindo seus
retornos e exceções.
"""

import unittest

import pandas as pd

import crime


def _df_crimes(tipos):
    """Constrói um DataFrame a partir de uma lista de tipos de crime."""
    n = len(tipos)
    return pd.DataFrame({
        "data": pd.to_datetime(["2024-01-01"] * n),
        "latitude": [-22.97] * n,
        "longitude": [-43.18] * n,
        "tipo_crime": tipos,
    })


def _df_bairros(distribuicao):
    """Constrói um DataFrame com a coluna 'bairro' a partir de {bairro: qtd}."""
    linhas = []
    for bairro, qtd in distribuicao.items():
        for _ in range(qtd):
            linhas.append({"bairro": bairro, "tipo_crime": "Furto"})
    return pd.DataFrame(linhas, columns=["bairro", "tipo_crime"])


class TestDfCrimeEspec(unittest.TestCase):
    def test_crime_existente(self):
        df = _df_crimes(["Roubo de Veículo", "Furto", "Roubo de Veículo"])
        resultado = crime.df_crime_espec(df, "Roubo de Veículo")
        self.assertEqual(len(resultado), 2)
        self.assertTrue((resultado["tipo_crime"] == "Roubo de Veículo").all())

    def test_crime_inexistente(self):
        df = _df_crimes(["Roubo", "Furto"])
        resultado = crime.df_crime_espec(df, "Crime Espacial")
        self.assertTrue(resultado.empty)
        self.assertIn("tipo_crime", resultado.columns)

    def test_case_insensitive(self):
        df = _df_crimes(["furto", "furto", "Roubo"])
        resultado = crime.df_crime_espec(df, "FURTO")
        self.assertEqual(len(resultado), 2)

    def test_tabela_vazia(self):
        df = _df_crimes([])
        resultado = crime.df_crime_espec(df, "Furto")
        self.assertTrue(resultado.empty)

    def test_parametro_incorreto(self):
        df = _df_crimes(["Furto"])
        with self.assertRaises(TypeError):
            crime.df_crime_espec(df, 123)
        with self.assertRaises(TypeError):
            crime.df_crime_espec(df, None)


class TestContaOcorTpCrime(unittest.TestCase):
    def test_contagem_multipla(self):
        df = _df_crimes(["Furto"] * 10 + ["Roubo"] * 5 + ["Homicídio"] * 2)
        contagem = crime.conta_ocor_tpCrime(df)
        self.assertEqual(contagem, {"Furto": 10, "Roubo": 5, "Homicídio": 2})
        self.assertEqual(sum(contagem.values()), len(df))

    def test_apenas_um_tipo(self):
        df = _df_crimes(["Furto"] * 15)
        self.assertEqual(crime.conta_ocor_tpCrime(df), {"Furto": 15})

    def test_tabela_vazia(self):
        df = _df_crimes([])
        self.assertEqual(crime.conta_ocor_tpCrime(df), {})

    def test_tipos_nulos(self):
        df = _df_crimes(["Furto", None, None, None])
        contagem = crime.conta_ocor_tpCrime(df)
        self.assertEqual(contagem.get("Desconhecido"), 3)
        self.assertEqual(sum(contagem.values()), len(df))


class TestContaOcorBairro(unittest.TestCase):
    def test_distribuicao_geografica(self):
        df = _df_bairros({"Copacabana": 40, "Tijuca": 25, "Ipanema": 15})
        self.assertEqual(crime.conta_ocor_bairro(df),
                         {"Copacabana": 40, "Tijuca": 25, "Ipanema": 15})

    def test_falta_coluna_bairro(self):
        df = _df_crimes(["Furto", "Roubo"])
        with self.assertRaises(KeyError):
            crime.conta_ocor_bairro(df)

    def test_bairros_desconhecidos(self):
        df = _df_bairros({"Centro": 10, "Desconhecido": 2})
        self.assertEqual(crime.conta_ocor_bairro(df),
                         {"Centro": 10, "Desconhecido": 2})

    def test_tabela_vazia(self):
        df = pd.DataFrame(columns=["bairro", "tipo_crime"])
        self.assertEqual(crime.conta_ocor_bairro(df), {})


if __name__ == "__main__":
    unittest.main()
