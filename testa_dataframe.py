"""
Programa testador do módulo Dataframe — Rio SafeWay.

Exercita cada função de acesso cobrindo todos os códigos de retorno previstos
na especificação de interfaces. O estado encapsulado é reiniciado a cada teste
com dataframe.resetar() e recarregado a partir de um CSV temporário.
"""

import os
import tempfile
import unittest

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


def _escrever(texto):
    """Grava um CSV temporário e devolve o caminho."""
    caminho = os.path.join(tempfile.mkdtemp(), "dados.csv")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)
    return caminho


def _carregar(texto=SAMPLE):
    """Reseta o módulo e carrega o CSV informado."""
    dataframe.resetar()
    return dataframe.carregar_dados(_escrever(texto))


def _contar_ativo():
    """Conta os registros da visão ativa via obter_registro."""
    qtd = 0
    while dataframe.obter_registro(qtd)[0] == dataframe.DF_CondRet.OK:
        qtd += 1
    return qtd


class TestCarregarDados(unittest.TestCase):
    def test_caminho_feliz(self):
        self.assertEqual(_carregar(), dataframe.DF_CondRet.OK)
        self.assertEqual(_contar_ativo(), 6)

    def test_arquivo_inexistente(self):
        dataframe.resetar()
        self.assertEqual(
            dataframe.carregar_dados("/nao/existe/arquivo.csv"),
            dataframe.DF_CondRet.FALHA)

    def test_arquivo_corrompido(self):
        dataframe.resetar()
        caminho = _escrever("coluna_a,coluna_b\n1,2\n")
        self.assertEqual(dataframe.carregar_dados(caminho), dataframe.DF_CondRet.ERRO)


class TestFiltraDadosInvalidos(unittest.TestCase):
    def test_limpeza_concluida(self):
        _carregar()
        self.assertEqual(dataframe.filtra_dados_invalidos(), dataframe.DF_CondRet.OK)

    def test_remove_linhas_defeituosas(self):
        texto = SAMPLE + "2024-07-01,,-43.18,Furto\n2024-08-01,-22.97,,Roubo\n"
        _carregar(texto)
        dataframe.filtra_dados_invalidos()
        self.assertEqual(_contar_ativo(), 6)

    def test_base_vazia(self):
        dataframe.resetar()
        self.assertEqual(dataframe.filtra_dados_invalidos(), dataframe.DF_CondRet.FALHA)


class TestAdicionaDado(unittest.TestCase):
    def setUp(self):
        _carregar()

    def test_caminho_feliz(self):
        self.assertEqual(
            dataframe.adiciona_dado("2025-01-01", -22.97, -43.18, "Roubo"),
            dataframe.DF_CondRet.OK)
        self.assertEqual(_contar_ativo(), 7)

    def test_parametro_invalido(self):
        self.assertEqual(
            dataframe.adiciona_dado("2025-01-01", -22.97, -43.18, ""),
            dataframe.DF_CondRet.ERRO)
        self.assertEqual(
            dataframe.adiciona_dado("2025-01-01", None, -43.18, "Roubo"),
            dataframe.DF_CondRet.ERRO)

    def test_data_invalida(self):
        self.assertEqual(
            dataframe.adiciona_dado("ontem", -22.97, -43.18, "Roubo"),
            dataframe.DF_CondRet.ERRO)

    def test_coordenadas_fora_limites(self):
        self.assertEqual(
            dataframe.adiciona_dado("2025-01-01", 999.999, 888.888, "Roubo"),
            dataframe.DF_CondRet.FORA_LIMITES)

    def test_dado_duplicado(self):
        self.assertEqual(
            dataframe.adiciona_dado("2024-01-01", -22.9700, -43.1850, "Roubo"),
            dataframe.DF_CondRet.OK)
        self.assertEqual(_contar_ativo(), 7)


class TestRemoveDados(unittest.TestCase):
    def setUp(self):
        _carregar()

    def test_remocao_especifica(self):
        self.assertEqual(
            dataframe.remove_dados(data="2024-01-01", latitude=-22.9700,
                                   longitude=-43.1850, tipo_crime="Roubo"),
            dataframe.DF_CondRet.OK)
        self.assertEqual(_contar_ativo(), 5)

    def test_registro_nao_encontrado(self):
        self.assertEqual(
            dataframe.remove_dados(tipo_crime="Sequestro"),
            dataframe.DF_CondRet.FALHA)

    def test_remocao_total_nao_permitida(self):
        self.assertEqual(dataframe.remove_dados(), dataframe.DF_CondRet.ERRO)


class TestProcessarColunaBairros(unittest.TestCase):
    def test_mapeamento_sucesso(self):
        _carregar()
        self.assertEqual(dataframe.processar_coluna_bairros(), dataframe.DF_CondRet.OK)
        self.assertEqual(dataframe.obter_registro(0)[5], "Copacabana")
        self.assertEqual(dataframe.obter_registro(5)[5], "Desconhecido")

    def test_base_vazia(self):
        dataframe.resetar()
        self.assertEqual(dataframe.processar_coluna_bairros(), dataframe.DF_CondRet.FALHA)


class TestAplicarFiltroInterno(unittest.TestCase):
    def setUp(self):
        _carregar()

    def test_restaram_dados(self):
        self.assertEqual(
            dataframe.aplicar_filtro_interno("tipo_crime", "Furto", "Furto"),
            dataframe.DF_CondRet.OK)
        self.assertEqual(_contar_ativo(), 3)

    def test_visao_ficou_vazia(self):
        self.assertEqual(
            dataframe.aplicar_filtro_interno("tipo_crime", "Sequestro", "Sequestro"),
            dataframe.DF_CondRet.FALHA)
        self.assertEqual(_contar_ativo(), 0)

    def test_filtro_data(self):
        self.assertEqual(
            dataframe.aplicar_filtro_interno("data", "2024-01-01", "2024-03-31"),
            dataframe.DF_CondRet.OK)
        self.assertEqual(_contar_ativo(), 3)


class TestObterRegistro(unittest.TestCase):
    def setUp(self):
        _carregar()
        dataframe.processar_coluna_bairros()

    def test_registro_valido(self):
        codigo, data, lat, lon, tipo, bairro = dataframe.obter_registro(0)
        self.assertEqual(codigo, dataframe.DF_CondRet.OK)
        self.assertEqual(data, "2024-01-01")
        self.assertAlmostEqual(lat, -22.97)
        self.assertAlmostEqual(lon, -43.185)
        self.assertEqual(tipo, "Roubo")
        self.assertEqual(bairro, "Copacabana")

    def test_indice_fora_dos_limites(self):
        self.assertEqual(dataframe.obter_registro(999)[0], dataframe.DF_CondRet.FALHA)
        self.assertEqual(dataframe.obter_registro(-1)[0], dataframe.DF_CondRet.FALHA)


if __name__ == "__main__":
    unittest.main()
