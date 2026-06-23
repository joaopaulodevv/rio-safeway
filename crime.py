"""
Módulo Crime — Rio SafeWay.

TAD que encapsula as estatísticas pré-calculadas (contagem por tipo de crime e
por bairro) e o estado do filtro de crime ativo. Consome a visão ativa do
Dataframe registro a registro (via `obter_registro`), sem nunca tocar a tabela
diretamente.

Padrão da disciplina: módulo procedural; estado em variáveis `_` de módulo;
expõe só funções de acesso e o IntEnum de retorno. As estatísticas são
devolvidas como cópias de primitivos (inteiros e listas de strings).
"""

from enum import IntEnum

import dataframe


class CRIME_CondRet(IntEnum):
    """Códigos de retorno do módulo Crime."""
    OK = 1     # operação concluída com sucesso
    FALHA = 0  # visão vazia / string inválida / não listado
    ERRO = -1  # sem ocorrências do crime / coluna bairro não processada


# --- estado encapsulado: estatísticas e filtro ativo ---
_contagem_tpCrime = {}
_contagem_bairro = {}
_filtro_crime_ativo = None


def resetar() -> None:
    """
    Objetivo: zerar o estado encapsulado (apoio aos testes automatizados).

    Assertiva de saída: as contagens por tipo de crime e por bairro ficam
        vazias e o filtro de crime ativo fica indefinido.
    """
    global _contagem_tpCrime, _contagem_bairro, _filtro_crime_ativo
    _contagem_tpCrime = {}
    _contagem_bairro = {}
    _filtro_crime_ativo = None


def aplicar_filtro_crime(crime: str) -> int:
    """
    Objetivo: validar a string e ordenar ao Dataframe que filtre a visão ativa
        por um tipo de crime.

    Acoplamento:
        crime (entrada): string com o tipo de crime.

    Retornos:
        CRIME_CondRet.OK    (1): filtro aplicado, há registros.
        CRIME_CondRet.FALHA (0): string de busca inválida (vazia/não string).
        CRIME_CondRet.ERRO (-1): crime sem ocorrências na base atual.

    Assertiva de saída: em caso de OK/ERRO, a visão ativa só contém o crime
        pedido e o filtro ativo guarda a string.
    """
    global _filtro_crime_ativo
    if not isinstance(crime, str) or crime.strip() == "":
        return CRIME_CondRet.FALHA

    _filtro_crime_ativo = crime
    codigo = dataframe.aplicar_filtro_interno("tipo_crime", crime, crime)
    if codigo == dataframe.DF_CondRet.OK:
        return CRIME_CondRet.OK
    return CRIME_CondRet.ERRO


def limpar_filtro_crime() -> int:
    """
    Objetivo: resetar o filtro de crime e ordenar ao Dataframe que restaure a
        visão completa.

    Retornos:
        CRIME_CondRet.OK (1): estado resetado e visão restaurada.

    Assertiva de saída: o filtro de crime ativo fica indefinido.
    """
    global _filtro_crime_ativo
    _filtro_crime_ativo = None
    dataframe.restaurar_visao()
    return CRIME_CondRet.OK


def processar_contagem_tpCrime() -> int:
    """
    Objetivo: percorrer a visão ativa e consolidar a contagem por tipo de crime
        no estado encapsulado.

    Retornos:
        CRIME_CondRet.OK    (1): estatística gerada com sucesso.
        CRIME_CondRet.FALHA (0): visão ativa vazia.

    Assertiva de saída: em caso de OK, _contagem_tpCrime mapeia cada tipo (ou
        'Desconhecido') à sua quantidade; a soma é o nº de registros da visão.
    """
    global _contagem_tpCrime
    contagem = {}
    indice = 0
    tem_registro = False
    while True:
        codigo, _, _, _, tipo, _ = dataframe.obter_registro(indice)
        if codigo != dataframe.DF_CondRet.OK:
            break
        tem_registro = True
        chave = tipo if tipo else "Desconhecido"
        contagem[chave] = contagem.get(chave, 0) + 1
        indice += 1

    if not tem_registro:
        _contagem_tpCrime = {}
        return CRIME_CondRet.FALHA
    _contagem_tpCrime = contagem
    return CRIME_CondRet.OK


def processar_contagem_bairro() -> int:
    """
    Objetivo: percorrer a visão ativa e consolidar a contagem por bairro.

    Retornos:
        CRIME_CondRet.OK    (1): estatística gerada com sucesso.
        CRIME_CondRet.FALHA (0): visão ativa vazia.
        CRIME_CondRet.ERRO (-1): coluna bairro não processada (registros sem
            bairro — falta executar processar_coluna_bairros no Dataframe).

    Assertiva de saída: em caso de OK, _contagem_bairro mapeia cada bairro à sua
        quantidade; a soma é o nº de registros da visão.
    """
    global _contagem_bairro
    contagem = {}
    indice = 0
    tem_registro = False
    while True:
        codigo, _, _, _, _, bairro = dataframe.obter_registro(indice)
        if codigo != dataframe.DF_CondRet.OK:
            break
        tem_registro = True
        if bairro is None:
            _contagem_bairro = {}
            return CRIME_CondRet.ERRO
        contagem[bairro] = contagem.get(bairro, 0) + 1
        indice += 1

    if not tem_registro:
        _contagem_bairro = {}
        return CRIME_CondRet.FALHA
    _contagem_bairro = contagem
    return CRIME_CondRet.OK


def obter_qtd_crime(crime: str):
    """
    Objetivo: devolver a quantidade já calculada de um tipo de crime.

    Acoplamento:
        crime (entrada): tipo de crime consultado.
        retorno (saída): tupla (codigo, quantidade).

    Retornos (primeiro elemento):
        CRIME_CondRet.OK    (1): quantidade preenchida.
        CRIME_CondRet.FALHA (0): crime não consta nas estatísticas (qtd = 0).
    """
    if crime in _contagem_tpCrime:
        return (CRIME_CondRet.OK, _contagem_tpCrime[crime])
    return (CRIME_CondRet.FALHA, 0)


def obter_qtd_bairro(bairro: str):
    """
    Objetivo: devolver a quantidade já calculada de ocorrências em um bairro.

    Acoplamento:
        bairro (entrada): bairro consultado.
        retorno (saída): tupla (codigo, quantidade).

    Retornos (primeiro elemento):
        CRIME_CondRet.OK    (1): quantidade preenchida.
        CRIME_CondRet.FALHA (0): bairro não consta nas estatísticas (qtd = 0).
    """
    if bairro in _contagem_bairro:
        return (CRIME_CondRet.OK, _contagem_bairro[bairro])
    return (CRIME_CondRet.FALHA, 0)


def obter_lista_crimes():
    """
    Objetivo: listar os tipos de crime presentes nas estatísticas.

    Acoplamento:
        retorno (saída): tupla (codigo, lista de strings).

    Retornos (primeiro elemento):
        CRIME_CondRet.OK (1): lista (possivelmente vazia) devolvida.
    """
    return (CRIME_CondRet.OK, list(_contagem_tpCrime.keys()))


def obter_lista_bairros():
    """
    Objetivo: listar os bairros presentes nas estatísticas.

    Acoplamento:
        retorno (saída): tupla (codigo, lista de strings).

    Retornos (primeiro elemento):
        CRIME_CondRet.OK (1): lista (possivelmente vazia) devolvida.
    """
    return (CRIME_CondRet.OK, list(_contagem_bairro.keys()))
