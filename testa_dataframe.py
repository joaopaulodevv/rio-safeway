# testa_dataframe.py - testes (por funções) do módulo dataframe.py
#
# Cada caso de teste é uma função teste_*() que prepara o estado encapsulado
# (resetar) e devolve o valor a ser verificado (código de retorno ou resultado).
# A função verifica() confere o valor esperado e monta_testes() registra todos
# os casos numa TestSuite executada por FunctionTestCase.

import os
import tempfile
import unittest

from dataframe import *

SAMPLE = (
    "data,latitude,longitude,tipo_crime\n"
    "2024-01-01,-22.9700,-43.1850,Roubo\n"
    "2024-02-01,-22.9720,-43.1830,Furto\n"
    "2024-03-01,-22.9680,-43.1880,Furto\n"
    "2024-04-01,-22.9050,-43.1800,Furto\n"
    "2024-05-01,-22.9080,-43.1760,Roubo\n"
    "2024-06-01,-23.0600,-43.1800,Roubo\n"
)


def escrever_csv(texto):
    """Grava um CSV temporário e devolve o caminho."""
    caminho = os.path.join(tempfile.mkdtemp(), "dados.csv")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)
    return caminho


def carregar_sample(texto=SAMPLE):
    """Reseta o módulo e carrega o CSV informado."""
    resetar()
    carregar_dados(escrever_csv(texto))


def contar_ativo():
    """Conta os registros da visão ativa via obter_registro."""
    qtd = 0
    while obter_registro(qtd)[0] == DF_CondRet.OK:
        qtd += 1
    return qtd


# ---------------- carregar_dados ----------------

def teste_carregar_caminho_feliz():
    resetar()
    return carregar_dados(escrever_csv(SAMPLE))


def teste_carregar_inexistente():
    resetar()
    return carregar_dados("/nao/existe/arquivo.csv")


def teste_carregar_corrompido():
    resetar()
    return carregar_dados(escrever_csv("coluna_a,coluna_b\n1,2\n"))


def teste_conta_apos_carregar():
    carregar_sample()
    return contar_ativo()


# ---------------- filtra_dados_invalidos ----------------

def teste_filtra_ok():
    carregar_sample()
    return filtra_dados_invalidos()


def teste_filtra_remove_linhas():
    carregar_sample(SAMPLE + "2024-07-01,,-43.18,Furto\n2024-08-01,-22.97,,Roubo\n")
    filtra_dados_invalidos()
    return contar_ativo()


def teste_filtra_base_vazia():
    resetar()
    return filtra_dados_invalidos()


# ---------------- adiciona_dado ----------------

def teste_adiciona_ok():
    carregar_sample()
    return adiciona_dado("2025-01-01", -22.97, -43.18, "Roubo")


def teste_adiciona_conta():
    carregar_sample()
    adiciona_dado("2025-01-01", -22.97, -43.18, "Roubo")
    return contar_ativo()


def teste_adiciona_param_invalido():
    carregar_sample()
    return adiciona_dado("2025-01-01", -22.97, -43.18, "")


def teste_adiciona_data_invalida():
    carregar_sample()
    return adiciona_dado("ontem", -22.97, -43.18, "Roubo")


def teste_adiciona_fora_limites():
    carregar_sample()
    return adiciona_dado("2025-01-01", 999.999, 888.888, "Roubo")


def teste_adiciona_duplicado():
    carregar_sample()
    adiciona_dado("2024-01-01", -22.9700, -43.1850, "Roubo")
    return contar_ativo()


# ---------------- remove_dados ----------------

def teste_remove_especifica():
    carregar_sample()
    return remove_dados(data="2024-01-01", latitude=-22.9700,
                        longitude=-43.1850, tipo_crime="Roubo")


def teste_remove_conta():
    carregar_sample()
    remove_dados(data="2024-01-01", latitude=-22.9700,
                 longitude=-43.1850, tipo_crime="Roubo")
    return contar_ativo()


def teste_remove_nao_encontrado():
    carregar_sample()
    return remove_dados(tipo_crime="Sequestro")


def teste_remove_total_proibida():
    carregar_sample()
    return remove_dados()


# ---------------- processar_coluna_bairros ----------------

def teste_bairros_ok():
    carregar_sample()
    return processar_coluna_bairros()


def teste_bairros_valor_copacabana():
    carregar_sample()
    processar_coluna_bairros()
    return obter_registro(0)[5]


def teste_bairros_desconhecido():
    carregar_sample()
    processar_coluna_bairros()
    return obter_registro(5)[5]


def teste_bairros_base_vazia():
    resetar()
    return processar_coluna_bairros()


# ---------------- aplicar_filtro_interno ----------------

def teste_filtro_interno_restou():
    carregar_sample()
    return aplicar_filtro_interno("tipo_crime", "Furto", "Furto")


def teste_filtro_interno_conta():
    carregar_sample()
    aplicar_filtro_interno("tipo_crime", "Furto", "Furto")
    return contar_ativo()


def teste_filtro_interno_vazio():
    carregar_sample()
    return aplicar_filtro_interno("tipo_crime", "Sequestro", "Sequestro")


# ---------------- obter_registro ----------------

def teste_obter_registro_valido():
    carregar_sample()
    return obter_registro(0)[0]


def teste_obter_registro_campos():
    carregar_sample()
    processar_coluna_bairros()
    _, data, _, _, tipo, bairro = obter_registro(0)
    return (data, tipo, bairro)


def teste_obter_registro_fora():
    carregar_sample()
    return obter_registro(999)[0]


# ---------------- gravar / recuperar (persistência) ----------------

def teste_gravar_ok():
    carregar_sample()
    return gravar(escrever_csv(""))


def teste_recuperar_roundtrip():
    carregar_sample()
    adiciona_dado("2025-01-01", -22.97, -43.18, "Roubo")
    caminho = escrever_csv("")
    gravar(caminho)
    resetar()
    recuperar(caminho)
    return contar_ativo()


def teste_recuperar_inexistente():
    resetar()
    return recuperar("/nao/existe/estado.csv")


def teste_gravar_base_vazia():
    resetar()
    return gravar(escrever_csv(""))


def verifica(funcao, esperado):
    retorno = funcao()
    assert retorno == esperado, f"esperado {esperado!r}, obtido {retorno!r}"


def monta_testes():
    testes = unittest.TestSuite()
    casos = [
        (teste_carregar_caminho_feliz, DF_CondRet.OK),
        (teste_carregar_inexistente, DF_CondRet.FALHA),
        (teste_carregar_corrompido, DF_CondRet.ERRO),
        (teste_conta_apos_carregar, 6),
        (teste_filtra_ok, DF_CondRet.OK),
        (teste_filtra_remove_linhas, 6),
        (teste_filtra_base_vazia, DF_CondRet.FALHA),
        (teste_adiciona_ok, DF_CondRet.OK),
        (teste_adiciona_conta, 7),
        (teste_adiciona_param_invalido, DF_CondRet.ERRO),
        (teste_adiciona_data_invalida, DF_CondRet.ERRO),
        (teste_adiciona_fora_limites, DF_CondRet.FORA_LIMITES),
        (teste_adiciona_duplicado, 7),
        (teste_remove_especifica, DF_CondRet.OK),
        (teste_remove_conta, 5),
        (teste_remove_nao_encontrado, DF_CondRet.FALHA),
        (teste_remove_total_proibida, DF_CondRet.ERRO),
        (teste_bairros_ok, DF_CondRet.OK),
        (teste_bairros_valor_copacabana, "Copacabana"),
        (teste_bairros_desconhecido, "Desconhecido"),
        (teste_bairros_base_vazia, DF_CondRet.FALHA),
        (teste_filtro_interno_restou, DF_CondRet.OK),
        (teste_filtro_interno_conta, 3),
        (teste_filtro_interno_vazio, DF_CondRet.FALHA),
        (teste_obter_registro_valido, DF_CondRet.OK),
        (teste_obter_registro_campos, ("2024-01-01", "Roubo", "Copacabana")),
        (teste_obter_registro_fora, DF_CondRet.FALHA),
        (teste_gravar_ok, DF_CondRet.OK),
        (teste_recuperar_roundtrip, 7),
        (teste_recuperar_inexistente, DF_CondRet.FALHA),
        (teste_gravar_base_vazia, DF_CondRet.FALHA),
    ]
    for funcao, esperado in casos:
        testes.addTest(unittest.FunctionTestCase(
            lambda f=funcao, e=esperado: verifica(f, e)))
    return testes


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(monta_testes())
