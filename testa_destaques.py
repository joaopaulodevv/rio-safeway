"""
Programa testador do módulo Destaques — Rio SafeWay.

Cobre os cenários previstos na especificação (seção 5.1) para as funções
bairro_alerta e top_crime_pbairro, além de verificar a atualização do estado
encapsulado por atualizar_destaques.
"""

import unittest

import pandas as pd

import destaques


def _df_alerta(distribuicao):
    """DataFrame com {bairro: qtd} ocorrências (tipo de crime fixo)."""
    linhas = []
    for bairro, qtd in distribuicao.items():
        for _ in range(qtd):
            linhas.append({"bairro": bairro, "tipo_crime": "Furto"})
    return pd.DataFrame(linhas, columns=["bairro", "tipo_crime"])


def _df_top(pares):
    """DataFrame a partir de uma lista de (bairro, tipo_crime)."""
    return pd.DataFrame(pares, columns=["bairro", "tipo_crime"])


class TestBairroAlerta(unittest.TestCase):
    def test_multiplos_acima_da_media(self):
        df = _df_alerta({"Copacabana": 15, "Ipanema": 10, "Leblon": 5})
        self.assertEqual(destaques.bairro_alerta(df), [("Copacabana", 15)])

    def test_ponto_fora_da_curva(self):
        dist = {"Centro": 100}
        for i in range(9):
            dist[f"Bairro{i}"] = 1
        df = _df_alerta(dist)
        self.assertEqual(destaques.bairro_alerta(df), [("Centro", 100)])

    def test_distribuicao_igual(self):
        df = _df_alerta({"Gávea": 20, "Botafogo": 20, "Flamengo": 20})
        self.assertEqual(destaques.bairro_alerta(df), [])

    def test_um_unico_bairro(self):
        df = _df_alerta({"Tijuca": 50})
        self.assertEqual(destaques.bairro_alerta(df), [])

    def test_tabela_vazia(self):
        df = pd.DataFrame(columns=["bairro", "tipo_crime"])
        self.assertEqual(destaques.bairro_alerta(df), [])


class TestTopCrimePbairro(unittest.TestCase):
    def test_distribuicao_clara(self):
        df = _df_top([
            ("Botafogo", "Furto de Bicicleta"),
            ("Botafogo", "Furto de Bicicleta"),
            ("Botafogo", "Roubo"),
            ("Maracanã", "Roubo a Transeunte"),
            ("Maracanã", "Roubo a Transeunte"),
            ("Maracanã", "Furto"),
        ])
        self.assertEqual(destaques.top_crime_pbairro(df), {
            "Botafogo": "Furto de Bicicleta",
            "Maracanã": "Roubo a Transeunte",
        })

    def test_empate(self):
        pares = [("Gávea", "Furto")] * 5 + [("Gávea", "Roubo")] * 5
        df = _df_top(pares)
        self.assertEqual(destaques.top_crime_pbairro(df), {"Gávea": "Furto e Roubo"})

    def test_tabela_vazia(self):
        df = pd.DataFrame(columns=["bairro", "tipo_crime"])
        self.assertEqual(destaques.top_crime_pbairro(df), {})


class TestAtualizarDestaques(unittest.TestCase):
    def test_estado_encapsulado(self):
        df = _df_alerta({"Copacabana": 15, "Ipanema": 10, "Leblon": 5})
        destaques.atualizar_destaques(df)
        info = destaques.obter_destaques()
        self.assertEqual(info["bairros_alerta"], [("Copacabana", 15)])
        self.assertIn("Copacabana", info["crime_por_bairro"])


if __name__ == "__main__":
    unittest.main()
