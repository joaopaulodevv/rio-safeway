# testa_dataframe.py - testes (por funções) do módulo dataframe.py
#
# UMA função de teste por função de
# acesso. Cada teste_*() exercita os DIFERENTES retornos daquela função
# (1 OK, 0 FALHA, -1 ERRO, -2 FORA_LIMITES), compara cada um com o esperado e
# DEVOLVE 0 (passou) ou 1 (falhou). monta_testes() confere que todos devolvem 0.

import os
import tempfile
import unittest

from dataframe import *

# Base válida (coordenadas dentro do Rio de Janeiro).
SAMPLE = (
    "data,latitude,longitude,tipo_crime\n"
    "2024-01-01,-22.9700,-43.1850,Roubo\n"
    "2024-02-01,-22.9720,-43.1830,Furto\n"
    "2024-03-01,-22.9050,-43.1800,Furto\n"
)
# Arquivo sem as colunas obrigatórias (corrompido / formato incorreto).
SAMPLE_CORROMPIDO = "coluna_a,coluna_b\n1,2\n3,4\n"
# Latitude/longitude não numéricas (força erro de conversão em bairros).
SAMPLE_LATLON_INVALIDA = (
    "data,latitude,longitude,tipo_crime\n"
    "2024-01-01,abc,def,Roubo\n"
)


def imprime_codigo(codigo):
    mensagens = {0: "passou (todos os retornos == esperado)",
                 1: "falhou (algum retorno != esperado)"}
    print(f"Codigo {codigo}: {mensagens[codigo]}")


def caminho_csv(texto):
    """Grava o texto num CSV temporário e devolve o caminho."""
    caminho = os.path.join(tempfile.mkdtemp(), "dados.csv")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)
    return caminho


def carregar(texto=SAMPLE, filtrar=True, bairros=False):
    """Reseta o módulo e carrega o CSV, opcionalmente limpando/mapeando bairros."""
    resetar()
    carregar_dados(caminho_csv(texto))
    if filtrar:
        filtra_dados_invalidos()
    if bairros:
        processar_coluna_bairros()


def teste_carregar_dados():
    resetar()
    r_ok = carregar_dados(caminho_csv(SAMPLE))                  # 1
    resetar()
    r_inexistente = carregar_dados("/caminho/que/nao/existe.csv")  # 0
    resetar()
    r_corrompido = carregar_dados(caminho_csv(SAMPLE_CORROMPIDO))  # -1
    if r_ok == 1 and r_inexistente == 0 and r_corrompido == -1:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_filtra_dados_invalidos():
    carregar(filtrar=False)
    r_ok = filtra_dados_invalidos()      # 1
    resetar()
    r_vazia = filtra_dados_invalidos()   # 0
    if r_ok == 1 and r_vazia == 0:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_adiciona_dado():
    carregar()
    r_ok = adiciona_dado("2024-04-01", -22.9680, -43.1880, "Furto")  # 1
    carregar()
    r_invalido = adiciona_dado("2024-04-01", -22.9680, -43.1880, "")  # -1
    carregar()
    r_fora = adiciona_dado("2024-04-01", 0.0, 0.0, "Roubo")           # -2
    if r_ok == 1 and r_invalido == -1 and r_fora == -2:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_remove_dados():
    carregar()
    r_ok = remove_dados(tipo_crime="Roubo")           # 1
    carregar()
    r_nao_achou = remove_dados(tipo_crime="Homicidio")  # 0
    carregar()
    r_total = remove_dados()                            # -1
    if r_ok == 1 and r_nao_achou == 0 and r_total == -1:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_processar_coluna_bairros():
    carregar()
    r_ok = processar_coluna_bairros()    # 1
    resetar()
    r_vazia = processar_coluna_bairros()  # 0
    carregar(SAMPLE_LATLON_INVALIDA, filtrar=False)
    r_erro = processar_coluna_bairros()   # -1
    if r_ok == 1 and r_vazia == 0 and r_erro == -1:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_aplicar_filtro_interno():
    carregar()
    r_restaram = aplicar_filtro_interno("tipo_crime", "Furto", "Furto")        # 1
    carregar()
    r_vazio = aplicar_filtro_interno("tipo_crime", "Inexistente", "Inexistente")  # 0
    if r_restaram == 1 and r_vazio == 0:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_obter_registro():
    carregar()
    r_ok = obter_registro(0)[0]      # 1
    r_fora = obter_registro(9999)[0]  # 0
    if r_ok == 1 and r_fora == 0:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_restaurar_visao():
    carregar()
    aplicar_filtro_interno("tipo_crime", "Furto", "Furto")
    r_ok = restaurar_visao()      # 1
    resetar()
    r_sem_base = restaurar_visao()  # 0
    if r_ok == 1 and r_sem_base == 0:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_gravar():
    carregar()
    r_ok = gravar(os.path.join(tempfile.mkdtemp(), "estado.csv"))  # 1
    resetar()
    r_sem_base = gravar(os.path.join(tempfile.mkdtemp(), "estado.csv"))  # 0
    if r_ok == 1 and r_sem_base == 0:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_recuperar():
    carregar()
    caminho = os.path.join(tempfile.mkdtemp(), "estado.csv")
    gravar(caminho)
    resetar()
    r_ok = recuperar(caminho)                          # 1
    resetar()
    r_inexistente = recuperar("/caminho/que/nao/existe.csv")  # 0
    resetar()
    r_corrompido = recuperar(caminho_csv(SAMPLE_CORROMPIDO))  # -1
    if r_ok == 1 and r_inexistente == 0 and r_corrompido == -1:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def verifica(funcao, esperado):
    retorno = funcao()
    assert retorno == esperado, f"esperado {esperado!r}, obtido {retorno!r}"


def monta_testes():
    testes = unittest.TestSuite()
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_carregar_dados, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_filtra_dados_invalidos, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_adiciona_dado, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_remove_dados, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_processar_coluna_bairros, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_aplicar_filtro_interno, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_obter_registro, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_restaurar_visao, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_gravar, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_recuperar, 0)))
    return testes


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(monta_testes())
