# testa_crime.py - testes (por funções) do módulo crime.py
#
# Estilo da referência  UMA função de teste por função de
# acesso. Cada teste_*() exercita os DIFERENTES retornos daquela função
# (1 OK, 0 FALHA, -1 ERRO), compara cada um com o esperado e DEVOLVE 0 (passou)
# ou 1 (falhou). monta_testes() confere que todos devolvem 0.

import os
import tempfile
import unittest

import dataframe
from crime import *

SAMPLE = (
    "data,latitude,longitude,tipo_crime\n"
    "2024-01-01,-22.9700,-43.1850,Roubo\n"
    "2024-02-01,-22.9720,-43.1830,Furto\n"
    "2024-03-01,-22.9680,-43.1880,Furto\n"
    "2024-04-01,-22.9050,-43.1800,Furto\n"
    "2024-05-01,-22.9080,-43.1760,Roubo\n"
    "2024-06-01,-23.0600,-43.1800,Roubo\n"
)


def imprime_codigo(codigo):
    mensagens = {0: "passou (todos os retornos == esperado)",
                 1: "falhou (algum retorno != esperado)"}
    print(f"Codigo {codigo}: {mensagens[codigo]}")


def carregar_sample(bairros=True):
    """Reseta Dataframe e Crime e carrega o CSV de exemplo."""
    caminho = os.path.join(tempfile.mkdtemp(), "dados.csv")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(SAMPLE)
    dataframe.resetar()
    resetar()
    dataframe.carregar_dados(caminho)
    dataframe.filtra_dados_invalidos()
    if bairros:
        dataframe.processar_coluna_bairros()


def teste_aplicar_filtro_crime():
    carregar_sample()
    r_ok = aplicar_filtro_crime("Furto")        # 1
    carregar_sample()
    r_invalida = aplicar_filtro_crime("")        # 0
    carregar_sample()
    r_sem_ocorr = aplicar_filtro_crime("Sequestro")  # -1
    if r_ok == 1 and r_invalida == 0 and r_sem_ocorr == -1:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_limpar_filtro_crime():
    carregar_sample()
    aplicar_filtro_crime("Furto")
    r_ok = limpar_filtro_crime()  # 1
    if r_ok == 1:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_processar_contagem_tpCrime():
    carregar_sample()
    r_ok = processar_contagem_tpCrime()  # 1
    carregar_sample()
    aplicar_filtro_crime("Sequestro")    # esvazia a visão ativa
    r_vazia = processar_contagem_tpCrime()  # 0
    if r_ok == 1 and r_vazia == 0:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_processar_contagem_bairro():
    carregar_sample()
    r_ok = processar_contagem_bairro()  # 1
    carregar_sample()
    aplicar_filtro_crime("Sequestro")   # esvazia a visão ativa
    r_vazia = processar_contagem_bairro()  # 0
    carregar_sample(bairros=False)
    r_sem_coluna = processar_contagem_bairro()  # -1
    if r_ok == 1 and r_vazia == 0 and r_sem_coluna == -1:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_obter_qtd_crime():
    carregar_sample()
    processar_contagem_tpCrime()
    r_listado = obter_qtd_crime("Furto")[0]       # 1
    r_nao_listado = obter_qtd_crime("Homicidio")[0]  # 0
    if r_listado == 1 and r_nao_listado == 0:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_obter_qtd_bairro():
    carregar_sample()
    processar_contagem_bairro()
    r_listado = obter_qtd_bairro("Copacabana")[0]   # 1
    r_nao_listado = obter_qtd_bairro("Atlantida")[0]  # 0
    if r_listado == 1 and r_nao_listado == 0:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_obter_lista_crimes():
    carregar_sample()
    processar_contagem_tpCrime()
    r_ok = obter_lista_crimes()[0]  # 1
    if r_ok == 1:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_obter_lista_bairros():
    carregar_sample()
    processar_contagem_bairro()
    r_ok = obter_lista_bairros()[0]  # 1
    if r_ok == 1:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def verifica(funcao, esperado):
    retorno = funcao()
    assert retorno == esperado, f"esperado {esperado!r}, obtido {retorno!r}"


def monta_testes():
    testes = unittest.TestSuite()
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_aplicar_filtro_crime, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_limpar_filtro_crime, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_processar_contagem_tpCrime, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_processar_contagem_bairro, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_obter_qtd_crime, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_obter_qtd_bairro, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_obter_lista_crimes, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_obter_lista_bairros, 0)))
    return testes


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(monta_testes())
