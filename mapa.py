"""
Módulo Mapa — Rio SafeWay.

TAD de visualização geoespacial. Encapsula as configurações visuais estáticas
(diretório de saída, raios, cores, zoom) e gera as três representações: bubble
map, heat map e scatter plot map. Solicita as coordenadas à base registro a
registro (via `obter_registro`); nunca acessa a tabela diretamente.

Padrão da disciplina: módulo procedural; estado/configuração em variáveis `_`
de módulo; expõe só funções de acesso e o IntEnum de retorno. folium é
biblioteca externa cujas instâncias são usadas como dados internos.
"""

import os
from enum import IntEnum

import folium
from folium.plugins import HeatMap

import dataframe


class MAPA_CondRet(IntEnum):
    """Códigos de retorno do módulo Mapa."""
    OK = 1     # mapa gerado com sucesso
    FALHA = 0  # base ativa vazia (abortado)
    ERRO = -1  # coordenadas ausentes/corrompidas (erro fatal)


# --- configuração encapsulada ---
_dir_saida = "."
_ZOOM_INICIAL = 12


def definir_dir_saida(caminho: str) -> None:
    """
    Objetivo: definir o diretório onde os mapas HTML serão gravados.

    Acoplamento:
        caminho (entrada): diretório de saída (criado se não existir).
    Assertiva de saída: os próximos mapas são gravados em `caminho`.
    """
    global _dir_saida
    os.makedirs(caminho, exist_ok=True)
    _dir_saida = caminho


def _coletar_pontos():
    """Percorre a visão ativa e devolve (tem_registro, [(lat, lon), ...])."""
    pontos = []
    tem_registro = False
    indice = 0
    while True:
        codigo, _, lat, lon, _, _ = dataframe.obter_registro(indice)
        if codigo != dataframe.DF_CondRet.OK:
            break
        tem_registro = True
        if lat is not None and lon is not None:
            pontos.append((lat, lon))
        indice += 1
    return tem_registro, pontos


def _centro(pontos):
    """Centro do mapa = média das coordenadas."""
    lat_media = sum(p[0] for p in pontos) / len(pontos)
    lon_media = sum(p[1] for p in pontos) / len(pontos)
    return [lat_media, lon_media]


def _gerar(pontos, desenhar, nome_arquivo):
    """Cria o mapa, aplica `desenhar(mapa)` e salva. Devolve o caminho."""
    mapa = folium.Map(location=_centro(pontos), zoom_start=_ZOOM_INICIAL)
    desenhar(mapa)
    caminho = os.path.join(_dir_saida, nome_arquivo)
    mapa.save(caminho)
    return caminho


def plot_bubbleMap() -> int:
    """
    Objetivo: gerar um bubble map (tamanho da bolha = nº de ocorrências no
        ponto), consumindo as coordenadas da visão ativa.

    Retornos:
        MAPA_CondRet.OK    (1): mapa gerado e salvo em HTML.
        MAPA_CondRet.FALHA (0): base ativa vazia (abortado).
        MAPA_CondRet.ERRO (-1): coordenadas ausentes/corrompidas (nenhum ponto
            válido a desenhar).

    Assertiva de saída: em caso de OK, existe um arquivo HTML com as bolhas.
    """
    tem_registro, pontos = _coletar_pontos()
    if not tem_registro:
        return MAPA_CondRet.FALHA
    if not pontos:
        return MAPA_CondRet.ERRO

    def desenhar(mapa):
        """Hotspot: desenha as bolhas agregadas por coordenada no mapa."""
        agrupado = {}
        for lat, lon in pontos:
            agrupado[(lat, lon)] = agrupado.get((lat, lon), 0) + 1
        for (lat, lon), qtd in agrupado.items():
            folium.CircleMarker(
                location=[lat, lon], radius=4 + qtd * 2,
                popup=f"{qtd} ocorrência(s)", color="crimson",
                fill=True, fill_opacity=0.5,
            ).add_to(mapa)

    _gerar(pontos, desenhar, "mapa_bubble.html")
    return MAPA_CondRet.OK


def plot_heatMap() -> int:
    """
    Objetivo: gerar um heat map evidenciando, por gradiente de cor, a
        concentração de ocorrências, consumindo as coordenadas da visão ativa.

    Retornos:
        MAPA_CondRet.OK    (1): mapa gerado e salvo em HTML.
        MAPA_CondRet.FALHA (0): base ativa vazia (abortado).
        MAPA_CondRet.ERRO (-1): coordenadas ausentes/corrompidas.

    Assertiva de saída: em caso de OK, existe um arquivo HTML com o mapa de calor.
    """
    tem_registro, pontos = _coletar_pontos()
    if not tem_registro:
        return MAPA_CondRet.FALHA
    if not pontos:
        return MAPA_CondRet.ERRO

    _gerar(pontos, lambda mapa: HeatMap([list(p) for p in pontos]).add_to(mapa),
           "mapa_heat.html")
    return MAPA_CondRet.OK


def plot_scatterPlotMap() -> int:
    """
    Objetivo: gerar um scatter plot map com a localização pontual de cada
        ocorrência, consumindo as coordenadas da visão ativa.

    Retornos:
        MAPA_CondRet.OK    (1): mapa gerado e salvo em HTML.
        MAPA_CondRet.FALHA (0): base ativa vazia (abortado).
        MAPA_CondRet.ERRO (-1): coordenadas ausentes/corrompidas.

    Assertiva de saída: em caso de OK, existe um arquivo HTML com um ponto por
        ocorrência válida.
    """
    tem_registro, pontos = _coletar_pontos()
    if not tem_registro:
        return MAPA_CondRet.FALHA
    if not pontos:
        return MAPA_CondRet.ERRO

    def desenhar(mapa):
        """Hotspot: desenha um ponto por ocorrência válida no mapa."""
        for lat, lon in pontos:
            folium.CircleMarker(
                location=[lat, lon], radius=3, color="blue",
                fill=True, fill_opacity=0.7,
            ).add_to(mapa)

    _gerar(pontos, desenhar, "mapa_scatter.html")
    return MAPA_CondRet.OK
