"""
Módulo Mapa — Rio SafeWay.

TAD responsável pela visualização geoespacial das ocorrências. Concentra as
três representações gráficas previstas: bubble map, heat map e scatter plot
map. Consome os dados já filtrados/segmentados pelos módulos anteriores e gera
arquivos HTML interativos com a biblioteca folium.

Padrão da disciplina: módulo procedural que expõe apenas funções de acesso.
A configuração de saída (diretório dos arquivos HTML) fica encapsulada na
variável de módulo `_dir_saida`, acessível só pelas funções deste módulo.
folium é biblioteca externa; seus objetos são usados como dados internos.
"""

import os

import folium
import pandas as pd
from folium.plugins import HeatMap

# --- estado encapsulado: diretório onde os mapas HTML são gravados ---
_dir_saida = "."


def definir_dir_saida(caminho: str) -> None:
    """
    Objetivo: definir o diretório onde os arquivos HTML dos mapas serão salvos.

    Acoplamento:
        caminho (entrada): diretório de saída (criado se não existir).
    Assertiva de saída: os próximos mapas gerados são gravados em `caminho`.
    """
    global _dir_saida
    os.makedirs(caminho, exist_ok=True)
    _dir_saida = caminho


def _coords_validas(df: pd.DataFrame) -> pd.DataFrame:
    """Extrai as linhas com latitude/longitude numéricas e não nulas.

    Levanta KeyError se as colunas 'latitude'/'longitude' não existirem.
    """
    if "latitude" not in df.columns or "longitude" not in df.columns:
        raise KeyError("Colunas 'latitude' e 'longitude' são obrigatórias.")

    lat = pd.to_numeric(df["latitude"], errors="coerce")
    lon = pd.to_numeric(df["longitude"], errors="coerce")
    mask = lat.notna() & lon.notna()
    return pd.DataFrame({"latitude": lat[mask], "longitude": lon[mask]})


def _novo_mapa(pontos: pd.DataFrame) -> folium.Map:
    """Cria um folium.Map centralizado na média das coordenadas."""
    centro = [pontos["latitude"].mean(), pontos["longitude"].mean()]
    return folium.Map(location=centro, zoom_start=12)


def plot_bubbleMap(df: pd.DataFrame) -> bool:
    """
    Objetivo: gerar um bubble map em que o tamanho de cada bolha representa a
        quantidade de ocorrências naquela localização.

    Acoplamento:
        df      (entrada): pd.DataFrame com colunas 'latitude' e 'longitude'.
        retorno (saída): bool indicando se o mapa foi gerado.

    Retornos / exceções:
        True : o mapa foi gerado e salvo em arquivo HTML com sucesso.
        False: não havia nenhum ponto válido a desenhar (tabela vazia ou
            todas as coordenadas nulas/inválidas). A renderização é abortada.
        KeyError: as colunas 'latitude'/'longitude' não existem na tabela.

    Assertiva de entrada: df contém zero ou mais ocorrências.
    Assertiva de saída: se True, existe um arquivo HTML com as bolhas; linhas
        com coordenadas inválidas são ignoradas.
    """
    pontos = _coords_validas(df)
    if pontos.empty:
        return False

    mapa = _novo_mapa(pontos)
    agrupado = pontos.groupby(["latitude", "longitude"]).size().reset_index(name="qtd")
    for _, linha in agrupado.iterrows():
        folium.CircleMarker(
            location=[linha["latitude"], linha["longitude"]],
            radius=4 + linha["qtd"] * 2,
            popup=f"{int(linha['qtd'])} ocorrência(s)",
            color="crimson",
            fill=True,
            fill_opacity=0.5,
        ).add_to(mapa)

    mapa.save(os.path.join(_dir_saida, "mapa_bubble.html"))
    return True


def plot_heatMap(df: pd.DataFrame) -> bool:
    """
    Objetivo: gerar um heat map evidenciando, por gradiente de cor, as regiões
        com maior concentração de ocorrências.

    Acoplamento:
        df      (entrada): pd.DataFrame com colunas 'latitude' e 'longitude'.
        retorno (saída): bool indicando se o mapa foi gerado.

    Retornos / exceções:
        True : o mapa foi gerado e salvo em arquivo HTML com sucesso.
        False: não havia nenhum ponto válido a desenhar.
        KeyError: as colunas 'latitude'/'longitude' não existem na tabela.

    Assertiva de entrada: df contém zero ou mais ocorrências.
    Assertiva de saída: se True, existe um arquivo HTML com o mapa de calor.
    """
    pontos = _coords_validas(df)
    if pontos.empty:
        return False

    mapa = _novo_mapa(pontos)
    HeatMap(pontos[["latitude", "longitude"]].values.tolist()).add_to(mapa)
    mapa.save(os.path.join(_dir_saida, "mapa_heat.html"))
    return True


def plot_scatterPlotMap(df: pd.DataFrame) -> bool:
    """
    Objetivo: gerar um scatter plot map exibindo a localização pontual de cada
        ocorrência sobre o mapa da cidade.

    Acoplamento:
        df      (entrada): pd.DataFrame com colunas 'latitude' e 'longitude'.
        retorno (saída): bool indicando se o mapa foi gerado.

    Retornos / exceções:
        True : o mapa foi gerado e salvo em arquivo HTML com sucesso.
        False: não havia nenhum ponto válido a desenhar.
        KeyError: as colunas 'latitude'/'longitude' não existem na tabela.

    Assertiva de entrada: df contém zero ou mais ocorrências.
    Assertiva de saída: se True, existe um arquivo HTML com um ponto por
        ocorrência válida.
    """
    pontos = _coords_validas(df)
    if pontos.empty:
        return False

    mapa = _novo_mapa(pontos)
    for _, linha in pontos.iterrows():
        folium.CircleMarker(
            location=[linha["latitude"], linha["longitude"]],
            radius=3,
            color="blue",
            fill=True,
            fill_opacity=0.7,
        ).add_to(mapa)

    mapa.save(os.path.join(_dir_saida, "mapa_scatter.html"))
    return True
