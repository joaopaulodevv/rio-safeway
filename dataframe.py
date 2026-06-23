"""
Módulo Dataframe — Rio SafeWay.

TAD que ENCAPSULA totalmente a base de dados: a tabela original (pd.DataFrame)
e a "visão ativa" (resultado após os filtros). Nenhum outro módulo recebe, lê
ou altera essa estrutura diretamente — todo o tráfego acontece por cópias de
tipos primitivos (str, int, float) através das interfaces deste módulo.

Padrão da disciplina (procedural/modular): o estado vive em variáveis de módulo
prefixadas com `_` (estática encapsulada). Os clientes importam apenas funções
de acesso e o IntEnum de retorno. O pd.DataFrame é instância de classe de
biblioteca usada como dado interno; nenhuma classe própria é definida.

Adaptação do C para Python: as interfaces que no C usariam ponteiros de saída
(ex.: `obter_registro(..., str *data, float *lat, ...)`) retornam aqui uma
tupla `(codigo, valores...)` com cópias de primitivos.
"""

from enum import IntEnum

import pandas as pd


class DF_CondRet(IntEnum):
    """Códigos de retorno do módulo Dataframe (valores conforme a especificação)."""
    OK = 1            # operação concluída com sucesso
    FALHA = 0         # situação prevista sem sucesso (vazio / não encontrado)
    ERRO = -1         # erro (arquivo corrompido / parâmetro inválido / não permitido)
    FORA_LIMITES = -2  # coordenadas fora dos limites lógicos do Rio de Janeiro


# --- estado encapsulado: só este módulo acessa ---
COLUNAS_OBRIGATORIAS = ["data", "latitude", "longitude", "tipo_crime"]

_df_original = None  # base completa carregada
_df_ativo = None     # visão ativa (após filtros)

# Mapa de bairros: nome -> (lat_min, lat_max, lon_min, lon_max). Caixas
# delimitadoras aproximadas para converter coordenadas em bairros de forma
# determinística e offline (reprodutível, sem depender de API externa).
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
    if lat is None or lon is None or pd.isna(lat) or pd.isna(lon):
        return "Desconhecido"
    for nome, (la_min, la_max, lo_min, lo_max) in _BAIRROS.items():
        if la_min <= lat <= la_max and lo_min <= lon <= lo_max:
            return nome
    return "Desconhecido"


def resetar() -> None:
    """
    Objetivo: zerar o estado encapsulado (apoio aos testes automatizados).

    Assertiva de entrada: nenhuma (a base pode ou não estar carregada).
    Assertiva de saída: a base original e a visão ativa ficam indefinidas.
    """
    global _df_original, _df_ativo
    _df_original = None
    _df_ativo = None


def carregar_dados(nome_arq: str) -> int:
    """
    Objetivo: carregar as ocorrências de um CSV para a base encapsulada.

    Acoplamento:
        nome_arq (entrada): caminho do arquivo CSV.

    Retornos:
        DF_CondRet.OK    (1): dados carregados com sucesso.
        DF_CondRet.FALHA (0): arquivo não encontrado.
        DF_CondRet.ERRO (-1): arquivo corrompido/formato incorreto (ilegível ou
            sem as colunas obrigatórias).

    Assertiva de entrada: nome_arq é uma string com um caminho.
    Assertiva de saída: em caso de OK, a base original e a visão ativa contêm
        os registros do arquivo, com 'data' já convertida para datetime.
    """
    global _df_original, _df_ativo
    try:
        df = pd.read_csv(nome_arq)
    except FileNotFoundError:
        return DF_CondRet.FALHA
    except Exception:
        return DF_CondRet.ERRO

    if any(coluna not in df.columns for coluna in COLUNAS_OBRIGATORIAS):
        return DF_CondRet.ERRO

    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    _df_original = df
    _df_ativo = df.copy()
    return DF_CondRet.OK


def gravar(caminho: str) -> int:
    """
    Objetivo: gravar em arquivo todo o estado encapsulado (base de ocorrências),
        ao final da execução, para recuperação em uma nova execução.

    Acoplamento:
        caminho (entrada): caminho do arquivo de persistência (CSV).

    Retornos:
        DF_CondRet.OK    (1): estado gravado com sucesso.
        DF_CondRet.FALHA (0): não há base carregada para gravar.

    Assertiva de entrada: a base existe (ou é None).
    Assertiva de saída: em caso de OK, o arquivo contém todas as ocorrências
        encapsuladas, incluindo a coluna 'bairro' se já processada.
    """
    if _df_original is None:
        return DF_CondRet.FALHA
    _df_original.to_csv(caminho, index=False)
    return DF_CondRet.OK


def recuperar(caminho: str) -> int:
    """
    Objetivo: recuperar o estado encapsulado gravado em uma execução anterior,
        ao iniciar a aplicação.

    Acoplamento:
        caminho (entrada): caminho do arquivo de persistência (CSV).

    Retornos:
        DF_CondRet.OK    (1): estado recuperado com sucesso.
        DF_CondRet.FALHA (0): arquivo inexistente (primeira execução).
        DF_CondRet.ERRO (-1): arquivo de persistência corrompido/inválido.

    Assertiva de entrada: caminho é uma string com um caminho de arquivo.
    Assertiva de saída: em caso de OK, a base e a visão ativa contêm exatamente
        as ocorrências gravadas, com 'data' convertida para datetime.
    """
    global _df_original, _df_ativo
    try:
        df = pd.read_csv(caminho)
    except FileNotFoundError:
        return DF_CondRet.FALHA
    except Exception:
        return DF_CondRet.ERRO

    if any(coluna not in df.columns for coluna in COLUNAS_OBRIGATORIAS):
        return DF_CondRet.ERRO

    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    _df_original = df
    _df_ativo = df.copy()
    return DF_CondRet.OK


def filtra_dados_invalidos() -> int:
    """
    Objetivo: limpar a base, removendo registros com 'data', 'latitude' ou
        'longitude' nulas/inválidas.

    Retornos:
        DF_CondRet.OK    (1): limpeza concluída.
        DF_CondRet.FALHA (0): base vazia/inexistente, nada a limpar.

    Assertiva de entrada: a base pode estar carregada ou não (None/vazia).
    Assertiva de saída: em caso de OK, a base e a visão ativa não contêm nulos
        em 'data', 'latitude' ou 'longitude'; latitude/longitude são numéricas.
    """
    global _df_original, _df_ativo
    if _df_original is None or _df_original.empty:
        return DF_CondRet.FALHA

    df = _df_original.copy()
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df = df.dropna(subset=["data", "latitude", "longitude"]).reset_index(drop=True)
    _df_original = df
    _df_ativo = df.copy()
    return DF_CondRet.OK


def adiciona_dado(data, latitude, longitude, tipo_crime) -> int:
    """
    Objetivo: adicionar uma nova ocorrência à base encapsulada.

    Acoplamento:
        data       (entrada): string de data (ex.: '2025-01-01').
        latitude   (entrada): latitude (float ou conversível).
        longitude  (entrada): longitude (float ou conversível).
        tipo_crime (entrada): string não vazia.

    Retornos:
        DF_CondRet.OK           (1): adicionado com sucesso.
        DF_CondRet.ERRO        (-1): parâmetros inválidos/nulos (campo vazio ou
            data/coordenada não conversível).
        DF_CondRet.FORA_LIMITES (-2): coordenadas fora dos limites do Rio.

    Assertiva de entrada: a base existe ou será criada vazia na primeira inserção.
    Assertiva de saída: em caso de OK, a base tem uma linha a mais; se a coluna
        'bairro' já existia, o bairro da nova linha é recalculado.
    """
    global _df_original, _df_ativo
    if data is None or latitude is None or longitude is None \
            or tipo_crime is None or str(tipo_crime).strip() == "":
        return DF_CondRet.ERRO

    try:
        ts = pd.Timestamp(data)
    except (ValueError, TypeError):
        return DF_CondRet.ERRO
    if pd.isna(ts):
        return DF_CondRet.ERRO

    try:
        lat = float(latitude)
        lon = float(longitude)
    except (ValueError, TypeError):
        return DF_CondRet.ERRO

    if not (_LAT_MIN_RIO <= lat <= _LAT_MAX_RIO
            and _LON_MIN_RIO <= lon <= _LON_MAX_RIO):
        return DF_CondRet.FORA_LIMITES

    if _df_original is None:
        _df_original = pd.DataFrame(columns=COLUNAS_OBRIGATORIAS)

    nova = {"data": ts, "latitude": lat, "longitude": lon, "tipo_crime": tipo_crime}
    _df_original = pd.concat([_df_original, pd.DataFrame([nova])], ignore_index=True)
    if "bairro" in _df_original.columns:
        _df_original.loc[_df_original.index[-1], "bairro"] = _bairro_de(lat, lon)
    _df_ativo = _df_original.copy()
    return DF_CondRet.OK


def remove_dados(data=None, latitude=None, longitude=None, tipo_crime=None) -> int:
    """
    Objetivo: remover registros que casem com TODOS os critérios informados.

    Acoplamento:
        data, latitude, longitude, tipo_crime (entrada, opcionais): critérios.

    Retornos:
        DF_CondRet.OK    (1): remoção realizada.
        DF_CondRet.FALHA (0): nenhum registro casou (ou base vazia).
        DF_CondRet.ERRO (-1): nenhum critério informado — remoção total não
            permitida (evita apagar a base por acidente).

    Assertiva de entrada: a base existe e contém zero ou mais ocorrências.
    Assertiva de saída: em caso de OK, nenhuma linha remanescente casa com
        todos os critérios informados.
    """
    global _df_original, _df_ativo
    if data is None and latitude is None and longitude is None and tipo_crime is None:
        return DF_CondRet.ERRO
    if _df_original is None or _df_original.empty:
        return DF_CondRet.FALHA

    mask = pd.Series(True, index=_df_original.index)
    if data is not None:
        mask &= (_df_original["data"] == pd.Timestamp(data))
    if latitude is not None:
        mask &= (_df_original["latitude"] == float(latitude))
    if longitude is not None:
        mask &= (_df_original["longitude"] == float(longitude))
    if tipo_crime is not None:
        mask &= (_df_original["tipo_crime"] == tipo_crime)

    if not mask.any():
        return DF_CondRet.FALHA

    _df_original = _df_original[~mask].reset_index(drop=True)
    _df_ativo = _df_original.copy()
    return DF_CondRet.OK


def processar_coluna_bairros() -> int:
    """
    Objetivo: criar/preencher a coluna 'bairro' a partir das coordenadas.

    Retornos:
        DF_CondRet.OK    (1): bairros mapeados com sucesso.
        DF_CondRet.FALHA (0): base vazia/inexistente.
        DF_CondRet.ERRO (-1): erro na conversão.

    Assertiva de entrada: a base existe e possui as colunas 'latitude' e 'longitude'.
    Assertiva de saída: em caso de OK, toda linha possui um bairro (nome
        conhecido ou 'Desconhecido') tanto na base quanto na visão ativa.
    """
    global _df_original, _df_ativo
    if _df_original is None or _df_original.empty:
        return DF_CondRet.FALHA
    try:
        df = _df_original.copy()
        df["bairro"] = [_bairro_de(la, lo)
                        for la, lo in zip(df["latitude"], df["longitude"])]
        _df_original = df
        _df_ativo = df.copy()
        return DF_CondRet.OK
    except Exception:
        return DF_CondRet.ERRO


def aplicar_filtro_interno(coluna: str, valor_inicio: str, valor_fim: str) -> int:
    """
    Objetivo: reduzir a visão ativa segundo um filtro, sem expor a tabela.
        Interface genérica usada pelos módulos Período (coluna 'data', filtro de
        intervalo) e Crime (coluna 'tipo_crime', filtro de igualdade).

    Acoplamento:
        coluna       (entrada): nome da coluna a filtrar.
        valor_inicio (entrada): limite inicial (intervalo) ou valor procurado.
        valor_fim    (entrada): limite final (intervalo); para igualdade,
            ignorado.

    Retornos:
        DF_CondRet.OK    (1): filtro aplicado e restaram dados.
        DF_CondRet.FALHA (0): filtro aplicado e a visão ativa ficou vazia
            (ou não havia visão ativa).

    Assertiva de entrada: a visão ativa existe; 'coluna' é uma coluna válida da base.
    Assertiva de saída: a visão ativa passa a conter apenas as linhas que
        satisfazem o filtro.
    """
    global _df_ativo
    if _df_ativo is None:
        return DF_CondRet.FALHA

    if coluna == "data":
        inicio = pd.Timestamp(valor_inicio)
        fim = pd.Timestamp(valor_fim)
        mask = (_df_ativo["data"] >= inicio) & (_df_ativo["data"] <= fim)
    else:
        alvo = str(valor_inicio).strip().lower()
        mask = _df_ativo[coluna].astype(str).str.strip().str.lower() == alvo

    _df_ativo = _df_ativo[mask].reset_index(drop=True)
    return DF_CondRet.OK if len(_df_ativo) > 0 else DF_CondRet.FALHA


def restaurar_visao() -> int:
    """
    Objetivo: restaurar a visão ativa para a base completa (desfaz filtros).

    Retornos:
        DF_CondRet.OK    (1): visão ativa restaurada.
        DF_CondRet.FALHA (0): não há base carregada.

    Assertiva de entrada: a base original pode estar carregada ou não.
    Assertiva de saída: em caso de OK, a visão ativa é igual à base original.
    """
    global _df_ativo
    if _df_original is None:
        return DF_CondRet.FALHA
    _df_ativo = _df_original.copy()
    return DF_CondRet.OK


def obter_registro(indice: int):
    """
    Objetivo: entregar UM registro da visão ativa, em cópias de primitivos,
        permitindo que os demais módulos consumam os dados sem ver a tabela.

    Acoplamento:
        indice (entrada): posição do registro na visão ativa (0-based).
        retorno (saída): tupla (codigo, data, latitude, longitude, tipo, bairro).

    Retornos (primeiro elemento da tupla):
        DF_CondRet.OK    (1): registro retornado; os demais campos vêm
            preenchidos (data como string 'AAAA-MM-DD'; latitude/longitude como
            float ou None; tipo/bairro como string ou None).
        DF_CondRet.FALHA (0): índice fora dos limites; demais campos None.

    Assertiva de entrada: a visão ativa existe.
    Assertiva de saída: nenhuma estrutura interna é exposta — apenas primitivos.
    """
    if _df_ativo is None or indice < 0 or indice >= len(_df_ativo):
        return (DF_CondRet.FALHA, None, None, None, None, None)

    linha = _df_ativo.iloc[indice]

    data_val = linha["data"]
    data_str = data_val.strftime("%Y-%m-%d") if pd.notna(data_val) else None

    try:
        lat = float(linha["latitude"])
        if pd.isna(lat):
            lat = None
    except (ValueError, TypeError):
        lat = None
    try:
        lon = float(linha["longitude"])
        if pd.isna(lon):
            lon = None
    except (ValueError, TypeError):
        lon = None

    tipo = str(linha["tipo_crime"]) if pd.notna(linha["tipo_crime"]) else None
    if "bairro" in _df_ativo.columns and pd.notna(linha["bairro"]):
        bairro = str(linha["bairro"])
    else:
        bairro = None

    return (DF_CondRet.OK, data_str, lat, lon, tipo, bairro)
