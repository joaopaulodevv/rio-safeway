"""
Módulo Crime — Rio SafeWay.

TAD responsável pela segmentação e contagem das ocorrências. Filtra a tabela
por um tipo de crime específico e produz contagens por tipo de crime e por
bairro. Recebe os dados já filtrados (pelos módulos Dataframe e Período) e
produz informação estatística para os módulos de visualização e de destaques.

Padrão da disciplina: módulo procedural que expõe apenas funções de acesso.
Opera sobre o pd.DataFrame recebido como valor; não mantém estado próprio.
"""

import pandas as pd


def df_crime_espec(df: pd.DataFrame, crime: str) -> pd.DataFrame:
    """
    Objetivo: filtrar a tabela, mantendo apenas as ocorrências de um tipo de
        crime específico.

    Acoplamento:
        df      (entrada): pd.DataFrame de ocorrências.
        crime   (entrada): string com o tipo de crime desejado.
        retorno (saída): pd.DataFrame só com as ocorrências do crime pedido.

    Retornos / exceções:
        pd.DataFrame: linhas cujo 'tipo_crime' casa com `crime`. A comparação
            é insensível a maiúsculas/minúsculas e a espaços nas extremidades.
            Se nenhum registro casar (ou a tabela estiver vazia), devolve um
            DataFrame vazio com as colunas preservadas.
        TypeError: `crime` não é uma string.

    Assertiva de entrada: df possui a coluna 'tipo_crime'.
    Assertiva de saída: 100% das linhas do resultado têm 'tipo_crime' igual
        (normalizado) a `crime`.
    """
    if not isinstance(crime, str):
        raise TypeError("O parâmetro 'crime' deve ser uma string.")

    alvo = crime.strip().lower()
    mask = df["tipo_crime"].astype(str).str.strip().str.lower() == alvo
    return df[mask].reset_index(drop=True)


def conta_ocor_tpCrime(df: pd.DataFrame) -> dict:
    """
    Objetivo: contar quantas ocorrências existem de cada tipo de crime.

    Acoplamento:
        df      (entrada): pd.DataFrame de ocorrências.
        retorno (saída): dict {tipo_crime (str): quantidade (int)}.

    Retornos:
        dict: mapeia cada tipo de crime à sua contagem. Tipos de crime
            nulos/vazios são contabilizados sob a chave 'Desconhecido'.
            Para uma tabela vazia, retorna {}.

    Assertiva de entrada: df possui a coluna 'tipo_crime'.
    Assertiva de saída: a soma dos valores do dicionário é igual ao número de
        linhas do DataFrame.
    """
    if df.empty:
        return {}

    serie = df["tipo_crime"].fillna("Desconhecido").replace("", "Desconhecido")
    contagem = serie.value_counts()
    return {str(chave): int(valor) for chave, valor in contagem.items()}


def conta_ocor_bairro(df: pd.DataFrame) -> dict:
    """
    Objetivo: contar quantas ocorrências existem em cada bairro.

    Pré-requisito arquitetural: a coluna 'bairro' já deve ter sido criada pela
    função coluna_bairros() do módulo Dataframe.

    Acoplamento:
        df      (entrada): pd.DataFrame de ocorrências com a coluna 'bairro'.
        retorno (saída): dict {bairro (str): quantidade (int)}.

    Retornos / exceções:
        dict: mapeia cada bairro à sua contagem (incluindo 'Desconhecido' para
            coordenadas não mapeadas). Para uma tabela vazia, retorna {}.
        KeyError: a coluna 'bairro' não existe (coluna_bairros não foi executada).

    Assertiva de entrada: df possui a coluna 'bairro'.
    Assertiva de saída: a soma dos valores do dicionário é igual ao número de
        linhas do DataFrame.
    """
    if "bairro" not in df.columns:
        raise KeyError(
            "Coluna 'bairro' não encontrada. "
            "Execute coluna_bairros() do módulo Dataframe antes."
        )
    if df.empty:
        return {}

    serie = df["bairro"].fillna("Desconhecido")
    contagem = serie.value_counts()
    return {str(chave): int(valor) for chave, valor in contagem.items()}
