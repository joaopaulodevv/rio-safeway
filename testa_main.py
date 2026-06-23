# testa_main.py - testes (por funções) do módulo main.py
#
# Estilo da referência (test_main.py): UMA função de teste por função de
# orquestração da main. Cada teste_*() exercita a função, compara o resultado
# com o esperado e DEVOLVE 0 (passou) ou 1 (falhou). monta_testes() confere que
# todos devolvem 0.
#
# Para não tocar nos arquivos reais do projeto, os caminhos da main
# (ARQUIVO_DADOS e ARQUIVO_PERSISTENCIA) são redirecionados para uma pasta
# temporária antes de cada teste.

import os
import tempfile
import unittest

import dataframe
import mapa
import main

SAMPLE = (
    "data,latitude,longitude,tipo_crime\n"
    "2024-01-01,-22.9700,-43.1850,Roubo\n"
    "2024-02-01,-22.9720,-43.1830,Furto\n"
    "2024-03-01,-22.9050,-43.1800,Furto\n"
    "2024-04-01,-22.9080,-43.1760,Roubo\n"
)


def imprime_codigo(codigo):
    mensagens = {0: "passou (resultado == esperado)",
                 1: "falhou (resultado != esperado)"}
    print(f"Codigo {codigo}: {mensagens[codigo]}")


def preparar(com_persistencia=False):
    """Redireciona os arquivos da main para uma pasta temporária e zera o estado.

    Com com_persistencia=True, simula uma execução anterior que já gravou o
    estado, exercitando o ramo de recuperação de iniciar_sistema().
    """
    pasta = tempfile.mkdtemp()
    main.ARQUIVO_DADOS = os.path.join(pasta, "dados.csv")
    main.ARQUIVO_PERSISTENCIA = os.path.join(pasta, "estado.csv")
    with open(main.ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        f.write(SAMPLE)
    dataframe.resetar()
    mapa.definir_dir_saida(pasta)
    if com_persistencia:
        dataframe.carregar_dados(main.ARQUIVO_DADOS)
        dataframe.filtra_dados_invalidos()
        dataframe.processar_coluna_bairros()
        dataframe.gravar(main.ARQUIVO_PERSISTENCIA)
        dataframe.resetar()


def teste_iniciar_sistema():
    preparar()                       # primeira execução: carrega a base inicial
    r_inicial = main.iniciar_sistema()
    preparar(com_persistencia=True)  # execução seguinte: recupera o estado
    r_recupera = main.iniciar_sistema()
    if r_inicial is True and r_recupera is True:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_acao_relatorio_geral():
    preparar()
    main.iniciar_sistema()
    try:
        main.acao_relatorio_geral()
        ok = True
    except Exception:
        ok = False
    if ok:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_acao_mapa():
    preparar()
    main.iniciar_sistema()
    try:
        main.acao_mapa(mapa.plot_bubbleMap, "Mapa de bolhas")
        ok = True
    except Exception:
        ok = False
    if ok:
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def teste_acao_salvar():
    preparar()
    main.iniciar_sistema()
    main.acao_salvar()
    if os.path.exists(main.ARQUIVO_PERSISTENCIA):
        imprime_codigo(0)
        return 0
    imprime_codigo(1)
    return 1


def verifica(funcao, esperado):
    retorno = funcao()
    assert retorno == esperado, f"esperado {esperado!r}, obtido {retorno!r}"


def monta_testes():
    testes = unittest.TestSuite()
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_iniciar_sistema, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_acao_relatorio_geral, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_acao_mapa, 0)))
    testes.addTest(unittest.FunctionTestCase(lambda: verifica(teste_acao_salvar, 0)))
    return testes


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(monta_testes())
