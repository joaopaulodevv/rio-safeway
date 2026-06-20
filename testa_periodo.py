"""
Programa testador do módulo Período — Rio SafeWay.

Cobre os códigos de retorno de valida_periodo, aplicar_filtro_periodo e
limpar_filtro_periodo. O Dataframe é reiniciado e carregado a cada teste, pois
o filtro de período opera sobre a visão ativa por meio dele.
"""

import os
import tempfile
import unittest

import dataframe
import periodo

SAMPLE = (
    "data,latitude,longitude,tipo_crime\n"
    "2024-01-01,-22.9700,-43.1850,Roubo\n"
    "2024-03-01,-22.9720,-43.1830,Furto\n"
    "2024-06-01,-22.9050,-43.1800,Furto\n"
)


def _carregar():
    caminho = os.path.join(tempfile.mkdtemp(), "dados.csv")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(SAMPLE)
    dataframe.resetar()
    periodo.resetar()
    dataframe.carregar_dados(caminho)
    dataframe.processar_coluna_bairros()


def _contar_ativo():
    qtd = 0
    while dataframe.obter_registro(qtd)[0] == dataframe.DF_CondRet.OK:
        qtd += 1
    return qtd


class TestValidaPeriodo(unittest.TestCase):
    def test_periodo_valido(self):
        self.assertEqual(periodo.valida_periodo("2024-01-01", "2024-12-31"),
                         periodo.PER_CondRet.OK)

    def test_datas_invertidas(self):
        self.assertEqual(periodo.valida_periodo("2024-12-31", "2024-01-01"),
                         periodo.PER_CondRet.FALHA)

    def test_limite_um_dia(self):
        self.assertEqual(periodo.valida_periodo("2024-05-15", "2024-05-15"),
                         periodo.PER_CondRet.FALHA)

    def test_tipagem_incorreta(self):
        self.assertEqual(periodo.valida_periodo(123, 456), periodo.PER_CondRet.ERRO)

    def test_formato_invalido(self):
        self.assertEqual(periodo.valida_periodo("ontem", "hoje"),
                         periodo.PER_CondRet.ERRO)

    def test_parametros_nulos(self):
        self.assertEqual(periodo.valida_periodo(None, "2024-12-31"),
                         periodo.PER_CondRet.ERRO)


class TestAplicarFiltroPeriodo(unittest.TestCase):
    def setUp(self):
        _carregar()

    def test_aplicado_com_ocorrencias(self):
        self.assertEqual(periodo.aplicar_filtro_periodo("2024-01-01", "2024-12-31"),
                         periodo.PER_CondRet.OK)
        self.assertEqual(_contar_ativo(), 3)

    def test_falha_validacao(self):
        self.assertEqual(periodo.aplicar_filtro_periodo("2024-12-31", "2024-01-01"),
                         periodo.PER_CondRet.FALHA)

    def test_aplicado_sem_ocorrencias(self):
        self.assertEqual(periodo.aplicar_filtro_periodo("2030-01-01", "2030-12-31"),
                         periodo.PER_CondRet.ERRO)
        self.assertEqual(_contar_ativo(), 0)


class TestLimparFiltroPeriodo(unittest.TestCase):
    def test_restaura_visao(self):
        _carregar()
        periodo.aplicar_filtro_periodo("2030-01-01", "2030-12-31")
        self.assertEqual(_contar_ativo(), 0)
        self.assertEqual(periodo.limpar_filtro_periodo(), periodo.PER_CondRet.OK)
        self.assertEqual(_contar_ativo(), 3)


if __name__ == "__main__":
    unittest.main()
