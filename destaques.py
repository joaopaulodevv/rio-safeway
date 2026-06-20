"""
Módulo Destaques — Rio SafeWay.

TAD que encapsula, em cache, os resultados qualitativos das análises: o bairro
em alerta atual (acima da média de crimes) e o crime predominante por bairro.
Consome as estatísticas do módulo Crime (contagem por bairro) e, para o crime
predominante, percorre a visão ativa do Dataframe via `obter_registro`. Nunca
acessa a tabela diretamente.

Padrão da disciplina: módulo procedural; estado em variáveis `_` de módulo;
expõe só funções de acesso e o IntEnum de retorno.
"""

from enum import IntEnum

import crime
import dataframe


class DEST_CondRet(IntEnum):
    """Códigos de retorno do módulo Destaques."""
    OK = 1     # cálculo realizado com sucesso
    FALHA = 0  # nada acima da média / bairro não consta / não calculado ainda
    ERRO = -1  # impossível calcular média (0 ou 1 bairro na base)


# --- estado encapsulado: resultados em cache ---
_bairro_alerta_atual = None   # tupla (nome, qtd) ou None
_top_crime_por_bairro = {}    # bairro -> crime predominante


def resetar() -> None:
    """Zera os caches de destaques (apoio aos testes)."""
    global _bairro_alerta_atual, _top_crime_por_bairro
    _bairro_alerta_atual = None
    _top_crime_por_bairro = {}


def calcular_bairro_alerta() -> int:
    """
    Objetivo: identificar o bairro com total de crimes estritamente acima da
        média de crimes por bairro e guardá-lo em cache.

    Retornos:
        DEST_CondRet.OK    (1): cálculo realizado, bairro identificado.
        DEST_CondRet.FALHA (0): nenhum bairro estritamente acima da média.
        DEST_CondRet.ERRO (-1): impossível calcular a média (0 ou 1 bairro).

    Assertiva de saída: em caso de OK, o cache guarda (bairro, qtd) do bairro de
        maior contagem acima da média; nos demais casos, o cache fica vazio.
    """
    global _bairro_alerta_atual
    if crime.processar_contagem_bairro() != crime.CRIME_CondRet.OK:
        _bairro_alerta_atual = None
        return DEST_CondRet.ERRO

    _, bairros = crime.obter_lista_bairros()
    if len(bairros) <= 1:
        _bairro_alerta_atual = None
        return DEST_CondRet.ERRO

    contagens = {}
    total = 0
    for bairro in bairros:
        _, qtd = crime.obter_qtd_bairro(bairro)
        contagens[bairro] = qtd
        total += qtd

    media = total / len(bairros)
    acima = sorted(
        [(b, q) for b, q in contagens.items() if q > media],
        key=lambda par: par[1], reverse=True,
    )
    if not acima:
        _bairro_alerta_atual = None
        return DEST_CondRet.FALHA

    _bairro_alerta_atual = acima[0]
    return DEST_CondRet.OK


def obter_bairro_alerta():
    """
    Objetivo: transferir o bairro em alerta em cache para o chamador.

    Acoplamento:
        retorno (saída): tupla (codigo, nome_bairro, qtd_crimes).

    Retornos (primeiro elemento):
        DEST_CondRet.OK    (1): variáveis copiadas com sucesso.
        DEST_CondRet.FALHA (0): cálculo ainda não processado (nome None, qtd 0).
    """
    if _bairro_alerta_atual is None:
        return (DEST_CondRet.FALHA, None, 0)
    return (DEST_CondRet.OK, _bairro_alerta_atual[0], _bairro_alerta_atual[1])


def calcular_top_crime_pbairro(bairro: str) -> int:
    """
    Objetivo: calcular o crime predominante de um bairro e guardá-lo em cache.

    Acoplamento:
        bairro (entrada): bairro analisado.

    Retornos:
        DEST_CondRet.OK    (1): crime predominante calculado e armazenado.
        DEST_CondRet.FALHA (0): bairro não consta na visão ativa.

    Assertiva de saída: em caso de OK, o cache guarda, para o bairro, o crime
        de maior incidência; havendo empate, os crimes são unidos por ' e '.
    """
    global _top_crime_por_bairro
    contagem = {}
    indice = 0
    while True:
        codigo, _, _, _, tipo, b = dataframe.obter_registro(indice)
        if codigo != dataframe.DF_CondRet.OK:
            break
        if b == bairro:
            chave = tipo if tipo else "Desconhecido"
            contagem[chave] = contagem.get(chave, 0) + 1
        indice += 1

    if not contagem:
        return DEST_CondRet.FALHA

    maximo = max(contagem.values())
    empatados = sorted(c for c, v in contagem.items() if v == maximo)
    _top_crime_por_bairro[bairro] = " e ".join(empatados)
    return DEST_CondRet.OK


def obter_top_crime_pbairro(bairro: str):
    """
    Objetivo: transferir o crime predominante em cache de um bairro.

    Acoplamento:
        bairro (entrada): bairro consultado.
        retorno (saída): tupla (codigo, crime_predominante).

    Retornos (primeiro elemento):
        DEST_CondRet.OK    (1): variável preenchida.
        DEST_CondRet.FALHA (0): cálculo não realizado para este bairro (None).
    """
    if bairro in _top_crime_por_bairro:
        return (DEST_CondRet.OK, _top_crime_por_bairro[bairro])
    return (DEST_CondRet.FALHA, None)
