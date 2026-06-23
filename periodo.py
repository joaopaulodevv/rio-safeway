"""
Módulo Período — Rio SafeWay.

TAD controlador da regra temporal. Encapsula apenas as variáveis de estado do
filtro ativo (data de início e fim) e valida as regras de calendário. NÃO
guarda dados: quando um período é válido, ordena ao módulo Dataframe que reduza
a visão ativa, através da interface segura `aplicar_filtro_interno`.

Padrão da disciplina: módulo procedural; estado em variáveis `_` de módulo;
expõe só funções de acesso e o IntEnum de retorno. As datas trafegam como
strings (primitivos).
"""

from enum import IntEnum

import pandas as pd

import dataframe


class PER_CondRet(IntEnum):
    """Códigos de retorno do módulo Período."""
    OK = 1     # período válido / filtro aplicado com ocorrências
    FALHA = 0  # datas invertidas/limite de 1 dia / falha de validação
    ERRO = -1  # erro de tipagem/formato / aplicado sem ocorrências


# --- estado encapsulado: regra temporal ativa ---
_data_inicio_ativa = None
_data_fim_ativa = None


def resetar() -> None:
    """
    Objetivo: zerar o estado encapsulado (apoio aos testes automatizados).

    Assertiva de saída: as datas de início e fim do filtro temporal ativo
        ficam indefinidas.
    """
    global _data_inicio_ativa, _data_fim_ativa
    _data_inicio_ativa = None
    _data_fim_ativa = None


def valida_periodo(inicio, fim) -> int:
    """
    Objetivo: validar as regras de calendário de um intervalo de datas.

    Acoplamento:
        inicio (entrada): string de data inicial (ex.: '2026-01-01').
        fim    (entrada): string de data final.

    Retornos:
        PER_CondRet.OK    (1): período lógico e válido (inicio < fim).
        PER_CondRet.FALHA (0): datas invertidas (inicio > fim) ou limite de um
            único dia (inicio == fim).
        PER_CondRet.ERRO (-1): erro de tipagem ou formato inválido.

    Assertiva de entrada: inicio e fim deveriam ser strings de data.
    Assertiva de saída: o valor reflete apenas a consistência de calendário
        (não consulta os dados).
    """
    if not isinstance(inicio, str) or not isinstance(fim, str):
        return PER_CondRet.ERRO
    try:
        ts_inicio = pd.Timestamp(inicio)
        ts_fim = pd.Timestamp(fim)
    except (ValueError, TypeError):
        return PER_CondRet.ERRO
    if pd.isna(ts_inicio) or pd.isna(ts_fim):
        return PER_CondRet.ERRO

    if ts_inicio >= ts_fim:
        return PER_CondRet.FALHA
    return PER_CondRet.OK


def aplicar_filtro_periodo(inicio, fim) -> int:
    """
    Objetivo: validar as datas e, em caso de sucesso, ordenar ao Dataframe que
        reduza a visão ativa ao intervalo informado.

    Acoplamento:
        inicio (entrada): string de data inicial.
        fim    (entrada): string de data final.

    Retornos:
        PER_CondRet.OK    (1): filtro validado e aplicado, restaram ocorrências.
        PER_CondRet.FALHA (0): falha na validação das datas.
        PER_CondRet.ERRO (-1): validado e aplicado, mas a base resultou em zero
            ocorrências.

    Assertiva de saída: em caso de OK/ERRO, o estado temporal ativo guarda
        inicio e fim, e a visão ativa do Dataframe reflete o recorte.
    """
    global _data_inicio_ativa, _data_fim_ativa
    if valida_periodo(inicio, fim) != PER_CondRet.OK:
        return PER_CondRet.FALHA

    _data_inicio_ativa = inicio
    _data_fim_ativa = fim
    codigo = dataframe.aplicar_filtro_interno("data", inicio, fim)
    if codigo == dataframe.DF_CondRet.OK:
        return PER_CondRet.OK
    return PER_CondRet.ERRO


def limpar_filtro_periodo() -> int:
    """
    Objetivo: resetar o filtro temporal e ordenar ao Dataframe que restaure a
        visão completa.

    Retornos:
        PER_CondRet.OK (1): estado resetado e visão restaurada.

    Assertiva de saída: o estado temporal ativo fica indefinido.
    """
    global _data_inicio_ativa, _data_fim_ativa
    _data_inicio_ativa = None
    _data_fim_ativa = None
    dataframe.restaurar_visao()
    return PER_CondRet.OK
