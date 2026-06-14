"""
Módulo Período — Rio SafeWay.

TAD responsável pelo recorte temporal das ocorrências. Valida o intervalo de
datas informado pelo usuário e, sendo ele consistente, devolve apenas as
ocorrências registradas naquele período. Atua como camada intermediária entre
os dados brutos (módulo Dataframe) e os módulos de análise (Crime, Mapa,
Destaques), garantindo que nada fora do recorte chegue aos próximos módulos.

Padrão da disciplina: módulo procedural que expõe apenas funções de acesso.
Opera sobre o pd.DataFrame recebido como valor; não mantém estado próprio.
"""

import pandas as pd


def valida_periodo(df: pd.DataFrame, inicio, fim) -> bool:
    """
    Objetivo: verificar se o intervalo [inicio, fim] é consistente e faz
        sentido para o conjunto de dados fornecido.

    Acoplamento:
        df      (entrada): pd.DataFrame de ocorrências (com a coluna 'data').
        inicio  (entrada): pd.Timestamp de início do período.
        fim     (entrada): pd.Timestamp de fim do período.
        retorno (saída): bool indicando a validade do período.

    Retornos / exceções:
        True : o período é válido — início <= fim e o intervalo intersecta a
            faixa de datas presente no DataFrame.
        False: início ocorre depois do fim; alguma data é nula; o DataFrame é
            vazio/sem coluna 'data'; ou o intervalo está totalmente fora da
            faixa de datas dos dados.
        TypeError: inicio ou fim não são pd.Timestamp.

    Assertiva de entrada: df contém zero ou mais ocorrências.
    Assertiva de saída: o valor retornado reflete a consistência do período
        frente aos dados.
    """
    if inicio is None or fim is None:
        return False

    if not isinstance(inicio, pd.Timestamp) or not isinstance(fim, pd.Timestamp):
        raise TypeError("inicio e fim devem ser objetos pd.Timestamp.")

    if inicio > fim:
        return False

    if df is None or df.empty or "data" not in df.columns:
        return False

    data_min = df["data"].min()
    data_max = df["data"].max()
    if pd.isna(data_min) or pd.isna(data_max):
        return False

    # O período precisa intersectar a faixa de datas existente nos dados.
    if fim < data_min or inicio > data_max:
        return False

    return True


def filtra_dfPeriodo(df: pd.DataFrame, inicio, fim) -> pd.DataFrame:
    """
    Objetivo: recortar a tabela, mantendo apenas as ocorrências cuja data
        esteja dentro do intervalo [inicio, fim].

    Acoplamento:
        df      (entrada): pd.DataFrame de ocorrências (com a coluna 'data').
        inicio  (entrada): pd.Timestamp de início do período.
        fim     (entrada): pd.Timestamp de fim do período.
        retorno (saída): pd.DataFrame recortado.

    Retornos / exceções:
        pd.DataFrame: novo DataFrame em que data >= inicio e data <= fim.
            Pode vir vazio (período sem ocorrências), mantendo as colunas.
            Se o período for inválido (ver valida_periodo), devolve o
            DataFrame original inalterado e emite uma mensagem ao usuário.
        TypeError: inicio ou fim não são pd.Timestamp (propagado de
            valida_periodo).

    Assertiva de entrada: df contém zero ou mais ocorrências.
    Assertiva de saída: em caso de recorte, toda linha do resultado satisfaz
        inicio <= data <= fim e as colunas são preservadas.
    """
    if not valida_periodo(df, inicio, fim):
        print("Período não válido.")
        return df

    mask = (df["data"] >= inicio) & (df["data"] <= fim)
    return df[mask].reset_index(drop=True)
