"""
Módulo Dataframe — Rio SafeWay.

TAD responsável pela manipulação do conjunto de ocorrências criminais:
carregamento a partir de CSV, limpeza, inserção, remoção e enriquecimento
com a coluna de bairros. É o núcleo de dados da aplicação; os demais módulos
consomem o pd.DataFrame produzido aqui.

Padrão da disciplina (procedural/modular): este módulo expõe apenas funções
de acesso. O pd.DataFrame é uma instância de classe de biblioteca usada como
valor/dado (uso permitido); nenhuma classe própria é definida. O estado
geográfico (mapa de bairros) fica encapsulado na variável de módulo `_BAIRROS`,
acessível somente pelas funções deste módulo.
"""

import pandas as pd

# --- estado/conhecimento encapsulado: só este módulo acessa ---

# Colunas obrigatórias do conjunto de dados de ocorrências.
COLUNAS_OBRIGATORIAS = ["data", "latitude", "longitude", "tipo_crime"]

# Mapa de bairros do Rio de Janeiro: nome -> (lat_min, lat_max, lon_min, lon_max).
# Caixas delimitadoras aproximadas usadas para converter coordenadas em bairros
# de forma determinística e offline (reprodutível, sem depender de API externa).
_BAIRROS = {
    "Copacabana":      (-22.985, -22.960, -43.195, -43.172),
    "Ipanema":         (-22.992, -22.978, -43.215, -43.196),
    "Leblon":          (-22.992, -22.978, -43.235, -43.215),
    "Botafogo":        (-22.962, -22.940, -43.195, -43.172),
    "Flamengo":        (-22.940, -22.922, -43.185, -43.165),
    "Centro":          (-22.918, -22.895, -43.195, -43.165),
    "Tijuca":          (-22.935, -22.916, -43.245, -43.222),
    "Maracanã":        (-22.914, -22.905, -43.240, -43.222),
    "Gávea":           (-22.985, -22.968, -43.245, -43.225),
    "Barra da Tijuca": (-23.020, -22.985, -43.400, -43.300),
}

# Limites geográficos aproximados do município do Rio de Janeiro.
_LAT_MIN_RIO, _LAT_MAX_RIO = -23.15, -22.70
_LON_MIN_RIO, _LON_MAX_RIO = -43.85, -43.00


def _bairro_de(lat, lon):
    """Retorna o nome do bairro que contém (lat, lon) ou 'Desconhecido'."""
    if pd.isna(lat) or pd.isna(lon):
        return "Desconhecido"
    for nome, (la_min, la_max, lo_min, lo_max) in _BAIRROS.items():
        if la_min <= lat <= la_max and lo_min <= lon <= lo_max:
            return nome
    return "Desconhecido"


def carregar_dados(nome_arq: str) -> pd.DataFrame:
    """
    Objetivo: carregar as ocorrências criminais de um arquivo CSV para memória.

    Acoplamento:
        nome_arq (entrada): caminho do arquivo CSV com colunas no mínimo
            'data', 'latitude', 'longitude' e 'tipo_crime'.
        retorno  (saída): pd.DataFrame populado, com a coluna 'data' já
            convertida para datetime.

    Retornos / exceções:
        pd.DataFrame: dados carregados (vazio mas com colunas, se o arquivo
            só tiver cabeçalho).
        FileNotFoundError: o arquivo informado não existe.
        ValueError: o arquivo não pôde ser lido como CSV válido ou não possui
            as colunas obrigatórias.

    Assertiva de entrada: nome_arq é uma string com um caminho.
    Assertiva de saída: em caso de sucesso, o DataFrame possui todas as
        colunas obrigatórias e 'data' é do tipo datetime.
    """
    try:
        df = pd.read_csv(nome_arq)
    except FileNotFoundError:
        raise
    except Exception as erro:
        raise ValueError(f"Arquivo não pôde ser lido como CSV válido: {erro}")

    faltando = [c for c in COLUNAS_OBRIGATORIAS if c not in df.columns]
    if faltando:
        raise ValueError(f"Colunas obrigatórias ausentes no CSV: {faltando}")

    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    return df


def filtra_dados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Objetivo: limpar a tabela, removendo registros com dados essenciais
        inválidos ou ausentes (data, latitude ou longitude).

    Acoplamento:
        df      (entrada): pd.DataFrame de ocorrências a ser limpo.
        retorno (saída): novo pd.DataFrame sem as linhas defeituosas.

    Retornos:
        pd.DataFrame: cópia da tabela em que as linhas com 'data', 'latitude'
            ou 'longitude' nulas/inválidas foram removidas. Uma tabela já limpa
            retorna sem nenhuma linha removida.

    Assertiva de entrada: df possui as colunas 'data', 'latitude' e 'longitude'.
    Assertiva de saída: o resultado não contém nulos em 'data', 'latitude' nem
        'longitude'; latitude e longitude são numéricas.
    """
    df = df.copy()
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df = df.dropna(subset=["data", "latitude", "longitude"])
    return df.reset_index(drop=True)


def adiciona_dado(df: pd.DataFrame, data, latitude, longitude,
                  tipo_crime) -> pd.DataFrame:
    """
    Objetivo: adicionar um novo registro de ocorrência ao conjunto de dados.

    Acoplamento:
        df         (entrada): pd.DataFrame de ocorrências.
        data       (entrada): pd.Timestamp da ocorrência.
        latitude   (entrada): latitude (numérica ou string numérica).
        longitude  (entrada): longitude (numérica ou string numérica).
        tipo_crime (entrada): string não vazia com o tipo de crime.
        retorno    (saída): novo pd.DataFrame com uma linha a mais.

    Retornos / exceções:
        pd.DataFrame: tabela com tamanho_original + 1 (registros duplicados
            são permitidos: crimes distintos podem ocorrer no mesmo local/hora).
        ValueError: algum campo obrigatório é nulo/vazio, ou as coordenadas
            são inválidas/fora do Rio de Janeiro.
        TypeError: 'data' não é um pd.Timestamp.

    Assertiva de entrada: df possui as colunas obrigatórias.
    Assertiva de saída: a última linha contém exatamente os dados informados.
    """
    if data is None or latitude is None or longitude is None \
            or tipo_crime is None or tipo_crime == "":
        raise ValueError("Todos os campos são obrigatórios.")

    if not isinstance(data, pd.Timestamp):
        raise TypeError("'data' deve ser um objeto pd.Timestamp.")

    try:
        lat = float(latitude)
        lon = float(longitude)
    except (TypeError, ValueError):
        raise ValueError("Latitude e longitude devem ser numéricas.")

    if not (_LAT_MIN_RIO <= lat <= _LAT_MAX_RIO
            and _LON_MIN_RIO <= lon <= _LON_MAX_RIO):
        raise ValueError("Coordenadas fora dos limites do Rio de Janeiro.")

    nova_linha = pd.DataFrame([{
        "data": data,
        "latitude": lat,
        "longitude": lon,
        "tipo_crime": tipo_crime,
    }])
    return pd.concat([df, nova_linha], ignore_index=True)


def remove_dados(df: pd.DataFrame, data=None, latitude=None,
                 longitude=None, tipo_crime=None) -> pd.DataFrame:
    """
    Objetivo: remover registros que casem com os critérios informados.

    Acoplamento:
        df         (entrada): pd.DataFrame de ocorrências.
        data       (entrada, opcional): pd.Timestamp a casar.
        latitude   (entrada, opcional): latitude a casar.
        longitude  (entrada, opcional): longitude a casar.
        tipo_crime (entrada, opcional): tipo de crime a casar.
        retorno    (saída): novo pd.DataFrame sem os registros casados.

    Retornos / exceções:
        pd.DataFrame: tabela sem as linhas que satisfazem TODOS os critérios
            informados. Se nenhum registro casar, a tabela é devolvida
            inalterada (sem erro).
        ValueError: nenhum critério foi informado (todos None) — evita apagar
            a base inteira por acidente.

    Assertiva de entrada: df possui as colunas obrigatórias.
    Assertiva de saída: nenhuma linha remanescente casa com todos os critérios
        informados.
    """
    if data is None and latitude is None and longitude is None \
            and tipo_crime is None:
        raise ValueError("Informe ao menos um critério de remoção.")

    mask = pd.Series(True, index=df.index)
    if data is not None:
        mask &= (df["data"] == data)
    if latitude is not None:
        mask &= (df["latitude"] == float(latitude))
    if longitude is not None:
        mask &= (df["longitude"] == float(longitude))
    if tipo_crime is not None:
        mask &= (df["tipo_crime"] == tipo_crime)

    return df[~mask].reset_index(drop=True)


def coluna_bairros(df: pd.DataFrame) -> pd.DataFrame:
    """
    Objetivo: enriquecer a tabela com a coluna 'bairro', convertendo as
        coordenadas geográficas em nomes de bairros do Rio de Janeiro.

    Acoplamento:
        df      (entrada): pd.DataFrame com colunas 'latitude' e 'longitude'.
        retorno (saída): novo pd.DataFrame com a coluna 'bairro' adicionada.

    Retornos:
        pd.DataFrame: cópia da tabela com uma coluna 'bairro' a mais. Pontos
            não mapeados (mar/fora dos polígonos) recebem o valor 'Desconhecido'.
            Para uma tabela vazia, a coluna 'bairro' é criada mesmo assim.

    Assertiva de entrada: df possui 'latitude' e 'longitude'.
    Assertiva de saída: o número de colunas aumenta em 1; toda linha possui um
        valor de bairro (nome conhecido ou 'Desconhecido').
    """
    df = df.copy()
    if df.empty:
        df["bairro"] = pd.Series(dtype="object")
        return df

    df["bairro"] = [
        _bairro_de(lat, lon)
        for lat, lon in zip(df["latitude"], df["longitude"])
    ]
    return df
