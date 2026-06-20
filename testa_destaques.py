"""
Programa testador do módulo Destaques — Rio SafeWay.

Cobre os códigos de retorno de calcular_bairro_alerta, obter_bairro_alerta,
calcular_top_crime_pbairro e obter_top_crime_pbairro. Reinicia Dataframe, Crime
e Destaques a cada teste e carrega conjuntos específicos.
"""

import os
import tempfile
import unittest

import crime
import dataframe
import destaques

# Copa 3 (Roubo,Furto,Furto), Centro 2 (Furto,Roubo), Desconhecido 1 -> média 2
SAMPLE_MULTI = (
    "data,latitude,longitude,tipo_crime\n"
    "2024-01-01,-22.9700,-43.1850,Roubo\n"
    "2024-02-01,-22.9720,-43.1830,Furto\n"
    "2024-03-01,-22.9680,-43.1880,Furto\n"
    "2024-04-01,-22.9050,-43.1800,Furto\n"
    "2024-05-01,-22.9080,-43.1760,Roubo\n"
    "2024-06-01,-23.0600,-43.1800,Roubo\n"
)
# Copa 2, Centro 2 -> média 2, ninguém estritamente acima
SAMPLE_IGUAL = (
    "data,latitude,longitude,tipo_crime\n"
    "2024-01-01,-22.9700,-43.1850,Roubo\n"
    "2024-02-01,-22.9720,-43.1830,Furto\n"
    "2024-03-01,-22.9050,-43.1800,Furto\n"
    "2024-04-01,-22.9080,-43.1760,Roubo\n"
)
# Apenas Copacabana -> 1 bairro
SAMPLE_UM_BAIRRO = (
    "data,latitude,longitude,tipo_crime\n"
    "2024-01-01,-22.9700,-43.1850,Roubo\n"
    "2024-02-01,-22.9720,-43.1830,Furto\n"
    "2024-03-01,-22.9680,-43.1880,Furto\n"
)
# Copacabana com empate Furto 1 x Roubo 1
SAMPLE_EMPATE = (
    "data,latitude,longitude,tipo_crime\n"
    "2024-01-01,-22.9700,-43.1850,Furto\n"
    "2024-02-01,-22.9720,-43.1830,Roubo\n"
)


def _carregar(texto):
    caminho = os.path.join(tempfile.mkdtemp(), "dados.csv")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)
    dataframe.resetar()
    crime.resetar()
    destaques.resetar()
    dataframe.carregar_dados(caminho)
    dataframe.filtra_dados_invalidos()
    dataframe.processar_coluna_bairros()


class TestCalcularBairroAlerta(unittest.TestCase):
    def test_bairro_identificado(self):
        _carregar(SAMPLE_MULTI)
        self.assertEqual(destaques.calcular_bairro_alerta(), destaques.DEST_CondRet.OK)
        self.assertEqual(destaques.obter_bairro_alerta(),
                         (destaques.DEST_CondRet.OK, "Copacabana", 3))

    def test_nenhum_acima_da_media(self):
        _carregar(SAMPLE_IGUAL)
        self.assertEqual(destaques.calcular_bairro_alerta(), destaques.DEST_CondRet.FALHA)

    def test_um_unico_bairro(self):
        _carregar(SAMPLE_UM_BAIRRO)
        self.assertEqual(destaques.calcular_bairro_alerta(), destaques.DEST_CondRet.ERRO)


class TestObterBairroAlerta(unittest.TestCase):
    def test_antes_de_calcular(self):
        destaques.resetar()
        self.assertEqual(destaques.obter_bairro_alerta(),
                         (destaques.DEST_CondRet.FALHA, None, 0))


class TestCalcularTopCrimePbairro(unittest.TestCase):
    def test_bairro_existente(self):
        _carregar(SAMPLE_MULTI)
        self.assertEqual(destaques.calcular_top_crime_pbairro("Copacabana"),
                         destaques.DEST_CondRet.OK)
        self.assertEqual(destaques.obter_top_crime_pbairro("Copacabana"),
                         (destaques.DEST_CondRet.OK, "Furto"))

    def test_empate(self):
        _carregar(SAMPLE_EMPATE)
        destaques.calcular_top_crime_pbairro("Copacabana")
        self.assertEqual(destaques.obter_top_crime_pbairro("Copacabana"),
                         (destaques.DEST_CondRet.OK, "Furto e Roubo"))

    def test_bairro_inexistente(self):
        _carregar(SAMPLE_MULTI)
        self.assertEqual(destaques.calcular_top_crime_pbairro("Atlântida"),
                         destaques.DEST_CondRet.FALHA)


class TestObterTopCrimePbairro(unittest.TestCase):
    def test_antes_de_calcular(self):
        destaques.resetar()
        self.assertEqual(destaques.obter_top_crime_pbairro("Copacabana"),
                         (destaques.DEST_CondRet.FALHA, None))


if __name__ == "__main__":
    unittest.main()
