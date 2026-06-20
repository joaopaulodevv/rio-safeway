"""
Programa testador do módulo Crime — Rio SafeWay.

Cobre os códigos de retorno de aplicar_filtro_crime, limpar_filtro_crime,
processar_contagem_tpCrime, processar_contagem_bairro e dos getters. O Dataframe
é reiniciado e carregado a cada teste.
"""

import os
import tempfile
import unittest

import crime
import dataframe

SAMPLE = (
    "data,latitude,longitude,tipo_crime\n"
    "2024-01-01,-22.9700,-43.1850,Roubo\n"
    "2024-02-01,-22.9720,-43.1830,Furto\n"
    "2024-03-01,-22.9680,-43.1880,Furto\n"
    "2024-04-01,-22.9050,-43.1800,Furto\n"
    "2024-05-01,-22.9080,-43.1760,Roubo\n"
    "2024-06-01,-23.0600,-43.1800,Roubo\n"
)


def _carregar(processar_bairros=True):
    caminho = os.path.join(tempfile.mkdtemp(), "dados.csv")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(SAMPLE)
    dataframe.resetar()
    crime.resetar()
    dataframe.carregar_dados(caminho)
    dataframe.filtra_dados_invalidos()
    if processar_bairros:
        dataframe.processar_coluna_bairros()


def _contar_ativo():
    qtd = 0
    while dataframe.obter_registro(qtd)[0] == dataframe.DF_CondRet.OK:
        qtd += 1
    return qtd


class TestAplicarFiltroCrime(unittest.TestCase):
    def setUp(self):
        _carregar()

    def test_filtro_com_registros(self):
        self.assertEqual(crime.aplicar_filtro_crime("Furto"), crime.CRIME_CondRet.OK)
        self.assertEqual(_contar_ativo(), 3)

    def test_string_invalida(self):
        self.assertEqual(crime.aplicar_filtro_crime(""), crime.CRIME_CondRet.FALHA)
        self.assertEqual(crime.aplicar_filtro_crime(None), crime.CRIME_CondRet.FALHA)

    def test_crime_sem_ocorrencias(self):
        self.assertEqual(crime.aplicar_filtro_crime("Sequestro"), crime.CRIME_CondRet.ERRO)
        self.assertEqual(_contar_ativo(), 0)


class TestLimparFiltroCrime(unittest.TestCase):
    def test_restaura_visao(self):
        _carregar()
        crime.aplicar_filtro_crime("Furto")
        self.assertEqual(_contar_ativo(), 3)
        self.assertEqual(crime.limpar_filtro_crime(), crime.CRIME_CondRet.OK)
        self.assertEqual(_contar_ativo(), 6)


class TestProcessarContagemTpCrime(unittest.TestCase):
    def test_estatistica_gerada(self):
        _carregar()
        self.assertEqual(crime.processar_contagem_tpCrime(), crime.CRIME_CondRet.OK)
        self.assertEqual(crime.obter_qtd_crime("Furto"), (crime.CRIME_CondRet.OK, 3))
        self.assertEqual(crime.obter_qtd_crime("Roubo"), (crime.CRIME_CondRet.OK, 3))

    def test_visao_vazia(self):
        _carregar()
        crime.aplicar_filtro_crime("Sequestro")
        self.assertEqual(crime.processar_contagem_tpCrime(), crime.CRIME_CondRet.FALHA)


class TestProcessarContagemBairro(unittest.TestCase):
    def test_estatistica_gerada(self):
        _carregar()
        self.assertEqual(crime.processar_contagem_bairro(), crime.CRIME_CondRet.OK)
        self.assertEqual(crime.obter_qtd_bairro("Copacabana"), (crime.CRIME_CondRet.OK, 3))
        self.assertEqual(crime.obter_qtd_bairro("Desconhecido"), (crime.CRIME_CondRet.OK, 1))

    def test_visao_vazia(self):
        _carregar()
        crime.aplicar_filtro_crime("Sequestro")
        self.assertEqual(crime.processar_contagem_bairro(), crime.CRIME_CondRet.FALHA)

    def test_coluna_bairro_nao_processada(self):
        _carregar(processar_bairros=False)
        self.assertEqual(crime.processar_contagem_bairro(), crime.CRIME_CondRet.ERRO)


class TestObterQtdCrime(unittest.TestCase):
    def setUp(self):
        _carregar()
        crime.processar_contagem_tpCrime()

    def test_crime_listado(self):
        self.assertEqual(crime.obter_qtd_crime("Furto"), (crime.CRIME_CondRet.OK, 3))

    def test_crime_nao_listado(self):
        self.assertEqual(crime.obter_qtd_crime("Homicídio"), (crime.CRIME_CondRet.FALHA, 0))


if __name__ == "__main__":
    unittest.main()
