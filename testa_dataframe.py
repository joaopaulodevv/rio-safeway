# testa_dataframe.py - testes (por funções) do módulo dataframe.py
#
# Reimplementado a partir da especificação de interfaces: cada função de acesso
# tem um teste para CADA código de retorno documentado (1 OK, 0 FALHA,
# -1 ERRO, -2 FORA_LIMITES). No padrão do teste_livro.py, cada teste_*() executa
# a função, imprime o código e DEVOLVE o código de retorno, que verifica()
# confere contra o esperado.

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
    mensagens = {
        1: "OK - operacao concluida com sucesso",
        0: "FALHA - situacao prevista (vazio / nao encontrado)",
        -1: "ERRO - arquivo/parametro invalido ou operacao nao permitida",
        -2: "FORA_LIMITES - coordenadas fora dos limites do Rio",
    }
    print(f"Codigo {int(codigo)}: {mensagens.get(codigo, 'desconhecido')}")


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


# ---------------- carregar_dados (1 / 0 / -1) ----------------

def teste_carregar_ok():
    resetar()
    codigo = carregar_dados(caminho_csv(SAMPLE))
    imprime_codigo(codigo)
    return codigo


def teste_carregar_arquivo_inexistente():
    resetar()
    codigo = carregar_dados("/caminho/que/nao/existe.csv")
    imprime_codigo(codigo)
    return codigo


def teste_carregar_corrompido():
    resetar()
    codigo = carregar_dados(caminho_csv(SAMPLE_CORROMPIDO))
    imprime_codigo(codigo)
    return codigo


# ---------------- filtra_dados_invalidos (1 / 0) ----------------

def teste_filtra_ok():
    carregar(filtrar=False)
    codigo = filtra_dados_invalidos()
    imprime_codigo(codigo)
    return codigo


def teste_filtra_base_vazia():
    resetar()
    codigo = filtra_dados_invalidos()
    imprime_codigo(codigo)
    return codigo


# ---------------- adiciona_dado (1 / -1 / -2) ----------------

def teste_adiciona_ok():
    carregar()
    codigo = adiciona_dado("2024-04-01", -22.9680, -43.1880, "Furto")
    imprime_codigo(codigo)
    return codigo


def teste_adiciona_param_invalido():
    carregar()
    codigo = adiciona_dado("2024-04-01", -22.9680, -43.1880, "")
    imprime_codigo(codigo)
    return codigo


def teste_adiciona_fora_limites():
    carregar()
    codigo = adiciona_dado("2024-04-01", 0.0, 0.0, "Roubo")
    imprime_codigo(codigo)
    return codigo


# ---------------- remove_dados (1 / 0 / -1) ----------------

def teste_remove_ok():
    carregar()
    codigo = remove_dados(tipo_crime="Roubo")
    imprime_codigo(codigo)
    return codigo


def teste_remove_nao_encontrado():
    carregar()
    codigo = remove_dados(tipo_crime="Homicidio")
    imprime_codigo(codigo)
    return codigo


def teste_remove_total_nao_permitida():
    carregar()
    codigo = remove_dados()
    imprime_codigo(codigo)
    return codigo


# ---------------- processar_coluna_bairros (1 / 0 / -1) ----------------

def teste_bairros_ok():
    carregar()
    codigo = processar_coluna_bairros()
    imprime_codigo(codigo)
    return codigo


def teste_bairros_base_vazia():
    resetar()
    codigo = processar_coluna_bairros()
    imprime_codigo(codigo)
    return codigo


def teste_bairros_erro_conversao():
    carregar(SAMPLE_LATLON_INVALIDA, filtrar=False)
    codigo = processar_coluna_bairros()
    imprime_codigo(codigo)
    return codigo


# ---------------- aplicar_filtro_interno (1 / 0) ----------------

def teste_filtro_interno_restaram():
    carregar()
    codigo = aplicar_filtro_interno("tipo_crime", "Furto", "Furto")
    imprime_codigo(codigo)
    return codigo


def teste_filtro_interno_vazio():
    carregar()
    codigo = aplicar_filtro_interno("tipo_crime", "Inexistente", "Inexistente")
    imprime_codigo(codigo)
    return codigo


# ---------------- obter_registro (1 / 0) ----------------

def teste_obter_registro_ok():
    carregar()
    codigo = obter_registro(0)[0]
    imprime_codigo(codigo)
    return codigo


def teste_obter_registro_fora_limites():
    carregar()
    codigo = obter_registro(9999)[0]
    imprime_codigo(codigo)
    return codigo


# ---------------- restaurar_visao (1 / 0) ----------------

def teste_restaurar_ok():
    carregar()
    aplicar_filtro_interno("tipo_crime", "Furto", "Furto")
    codigo = restaurar_visao()
    imprime_codigo(codigo)
    return codigo


def teste_restaurar_sem_base():
    resetar()
    codigo = restaurar_visao()
    imprime_codigo(codigo)
    return codigo


# ---------------- gravar / recuperar - persistência (1 / 0 / -1) ----------------

def teste_gravar_ok():
    carregar()
    codigo = gravar(os.path.join(tempfile.mkdtemp(), "estado.csv"))
    imprime_codigo(codigo)
    return codigo


def teste_gravar_sem_base():
    resetar()
    codigo = gravar(os.path.join(tempfile.mkdtemp(), "estado.csv"))
    imprime_codigo(codigo)
    return codigo


def teste_recuperar_ok():
    carregar()
    caminho = os.path.join(tempfile.mkdtemp(), "estado.csv")
    gravar(caminho)
    resetar()
    codigo = recuperar(caminho)
    imprime_codigo(codigo)
    return codigo


def teste_recuperar_inexistente():
    resetar()
    codigo = recuperar("/caminho/que/nao/existe.csv")
    imprime_codigo(codigo)
    return codigo


def teste_recuperar_corrompido():
    resetar()
    codigo = recuperar(caminho_csv(SAMPLE_CORROMPIDO))
    imprime_codigo(codigo)
    return codigo


def verifica(funcao, esperado):
    retorno = funcao()
    assert retorno == esperado, f"esperado {esperado!r}, obtido {retorno!r}"


def monta_testes():
    testes = unittest.TestSuite()
    # carregar_dados: 1 / 0 / -1
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_carregar_ok, 1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_carregar_arquivo_inexistente, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_carregar_corrompido, -1)))
    # filtra_dados_invalidos: 1 / 0
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_filtra_ok, 1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_filtra_base_vazia, 0)))
    # adiciona_dado: 1 / -1 / -2
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_adiciona_ok, 1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_adiciona_param_invalido, -1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_adiciona_fora_limites, -2)))
    # remove_dados: 1 / 0 / -1
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_remove_ok, 1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_remove_nao_encontrado, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_remove_total_nao_permitida, -1)))
    # processar_coluna_bairros: 1 / 0 / -1
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_bairros_ok, 1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_bairros_base_vazia, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_bairros_erro_conversao, -1)))
    # aplicar_filtro_interno: 1 / 0
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_filtro_interno_restaram, 1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_filtro_interno_vazio, 0)))
    # obter_registro: 1 / 0
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_obter_registro_ok, 1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_obter_registro_fora_limites, 0)))
    # restaurar_visao: 1 / 0
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_restaurar_ok, 1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_restaurar_sem_base, 0)))
    # gravar: 1 / 0
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_gravar_ok, 1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_gravar_sem_base, 0)))
    # recuperar: 1 / 0 / -1
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_recuperar_ok, 1)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_recuperar_inexistente, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_recuperar_corrompido, -1)))
    return testes


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(monta_testes())
