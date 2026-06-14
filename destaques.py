"""
Módulo Destaques — Rio SafeWay.

TAD responsável pela camada de análise qualitativa/resumida: identifica os
bairros em alerta (acima da média de crimes) e o crime predominante de cada
bairro. Mantém, de forma encapsulada, o último conjunto de destaques calculado,
atualizado sempre que os filtros ou os dados mudam.

Padrão da disciplina: módulo procedural que expõe apenas funções de acesso.
O estado dos destaques vive na variável de módulo `_destaques` (estática
encapsulada) e só é acessível pelas funções deste módulo. Reaproveita o módulo
Crime para a contagem por bairro (baixo acoplamento, sem duplicação).
"""

import pandas as pd

import crime

# --- estado encapsulado: últimos destaques calculados ---
_destaques = {"bairros_alerta": [], "crime_por_bairro": {}}


def bairro_alerta(df: pd.DataFrame) -> list:
    """
    Objetivo: identificar todos os bairros cujo total de crimes seja
        estritamente maior (>) que a média de crimes por bairro no conjunto.

    Acoplamento:
        df      (entrada): pd.DataFrame com a coluna 'bairro'.
        retorno (saída): lista de tuplas (bairro (str), total (int)),
            ordenada por total decrescente.

    Retornos / exceções:
        list: bairros acima da média (ex.: [("Copacabana", 15)]). Vazia [] se
            nenhum bairro supera a média, se houver um único bairro (não há
            média comparativa) ou se a tabela estiver vazia.
        KeyError: a coluna 'bairro' não existe (propagado de conta_ocor_bairro).

    Assertiva de entrada: df possui a coluna 'bairro'.
    Assertiva de saída: todo bairro do resultado tem total > média; não há
        divisão por zero quando não há bairros.
    """
    contagem = crime.conta_ocor_bairro(df)
    if not contagem:
        return []

    media = sum(contagem.values()) / len(contagem)
    acima = [(bairro, total) for bairro, total in contagem.items() if total > media]
    acima.sort(key=lambda par: par[1], reverse=True)
    return acima


def top_crime_pbairro(df: pd.DataFrame) -> dict:
    """
    Objetivo: para cada bairro, identificar o tipo de crime mais comum.

    Acoplamento:
        df      (entrada): pd.DataFrame com colunas 'bairro' e 'tipo_crime'.
        retorno (saída): dict {bairro (str): crime predominante (str)}.

    Retornos / exceções:
        dict: mapeia cada bairro ao seu crime predominante. Em caso de empate,
            os crimes empatados são unidos pela string " e " (ex.: "Furto e
            Roubo"). Para uma tabela vazia, retorna {}.
        KeyError: as colunas 'bairro'/'tipo_crime' não existem.

    Assertiva de entrada: df possui 'bairro' e 'tipo_crime'.
    Assertiva de saída: cada bairro presente nos dados aparece como chave.
    """
    if df.empty:
        return {}
    if "bairro" not in df.columns or "tipo_crime" not in df.columns:
        raise KeyError("Colunas 'bairro' e 'tipo_crime' são obrigatórias.")

    resultado = {}
    for bairro, grupo in df.groupby("bairro"):
        contagem = grupo["tipo_crime"].value_counts()
        maximo = contagem.max()
        empatados = sorted(str(c) for c, v in contagem.items() if v == maximo)
        resultado[str(bairro)] = " e ".join(empatados)
    return resultado


def atualizar_destaques(df: pd.DataFrame) -> None:
    """
    Objetivo: recalcular e armazenar os destaques (bairros em alerta e crime
        predominante por bairro) a partir do conjunto de dados atual, refletindo
        eventuais mudanças de filtro ou de dados.

    Acoplamento:
        df (entrada): pd.DataFrame já filtrado e com a coluna 'bairro'.

    Retornos:
        None. Atualiza o estado encapsulado do módulo, consultável por
            obter_destaques().

    Assertiva de entrada: df possui as colunas 'bairro' e 'tipo_crime'.
    Assertiva de saída: o estado interno passa a refletir os destaques do df
        informado.
    """
    global _destaques
    _destaques = {
        "bairros_alerta": bairro_alerta(df),
        "crime_por_bairro": top_crime_pbairro(df),
    }


def obter_destaques() -> dict:
    """
    Objetivo: devolver uma cópia dos destaques atualmente armazenados,
        preservando o encapsulamento do estado interno.

    Acoplamento:
        retorno (saída): dict com as chaves 'bairros_alerta' (lista de tuplas)
            e 'crime_por_bairro' (dict).

    Assertiva de saída: o chamador recebe uma cópia; o estado interno não é
        exposto para escrita direta.
    """
    return {
        "bairros_alerta": list(_destaques["bairros_alerta"]),
        "crime_por_bairro": dict(_destaques["crime_por_bairro"]),
    }
