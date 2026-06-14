"""
Módulo Main — Rio SafeWay.

Orquestrador (front-end) da aplicação. Coordena a comunicação entre os módulos
Dataframe, Período, Crime, Mapa e Destaques, recebe as interações do usuário e
direciona o fluxo de execução: carregamento dos dados, aplicação de filtros,
geração das visualizações e exibição dos destaques.

Padrão da disciplina: módulo procedural. Não define classes próprias; mantém
apenas o estado de trabalho da sessão (a tabela atual) e delega toda a lógica
às funções de acesso dos demais módulos. Trata os erros previstos (exceções
levantadas pelos módulos) para que a aplicação não quebre.
"""

import pandas as pd

import crime
import dataframe
import destaques
import mapa
import periodo

ARQUIVO_DADOS = "dados_crimes.csv"

# Estado de trabalho da sessão (vive em memória durante a execução).
_df_base = None    # conjunto completo carregado e enriquecido
_df_atual = None   # recorte atual após os filtros aplicados


def _df_vazio() -> pd.DataFrame:
    """Cria uma tabela vazia, porém com a estrutura de colunas esperada."""
    vazio = pd.DataFrame(columns=dataframe.COLUNAS_OBRIGATORIAS)
    return dataframe.coluna_bairros(vazio)


def carregar() -> None:
    """Carrega, limpa e enriquece os dados a partir do CSV (recuperação)."""
    global _df_base, _df_atual
    try:
        bruto = dataframe.carregar_dados(ARQUIVO_DADOS)
        limpo = dataframe.filtra_dados(bruto)
        _df_base = dataframe.coluna_bairros(limpo)
        print(f"Dados carregados: {len(_df_base)} ocorrências.")
    except FileNotFoundError:
        _df_base = _df_vazio()
        print(f"Arquivo '{ARQUIVO_DADOS}' não encontrado. Iniciando vazio.")
    except ValueError as erro:
        _df_base = _df_vazio()
        print(f"Erro ao carregar os dados: {erro}. Iniciando vazio.")
    _df_atual = _df_base.copy()
    destaques.atualizar_destaques(_df_atual)


def _ler_data(rotulo: str):
    """Lê uma data AAAA-MM-DD do usuário e devolve um pd.Timestamp (ou None)."""
    texto = input(f"{rotulo} (AAAA-MM-DD): ").strip()
    try:
        return pd.Timestamp(texto)
    except (ValueError, TypeError):
        print("Data inválida.")
        return None


def acao_adicionar() -> None:
    """Adiciona uma nova ocorrência ao conjunto atual."""
    global _df_base, _df_atual
    data = _ler_data("Data da ocorrência")
    if data is None:
        return
    latitude = input("Latitude: ").strip()
    longitude = input("Longitude: ").strip()
    tipo_crime = input("Tipo de crime: ").strip()
    try:
        novo = dataframe.adiciona_dado(_df_base, data, latitude, longitude, tipo_crime)
        _df_base = dataframe.coluna_bairros(novo)
        _df_atual = _df_base.copy()
        destaques.atualizar_destaques(_df_atual)
        print("Ocorrência adicionada.")
    except (ValueError, TypeError) as erro:
        print(f"Não foi possível adicionar: {erro}")


def acao_remover() -> None:
    """Remove ocorrências do conjunto atual por critérios (Enter = ignora)."""
    global _df_base, _df_atual
    print("Deixe em branco os critérios que não quiser usar.")
    tipo_crime = input("Tipo de crime: ").strip() or None
    data_txt = input("Data (AAAA-MM-DD): ").strip()
    data = pd.Timestamp(data_txt) if data_txt else None
    try:
        novo = dataframe.remove_dados(_df_base, data=data, tipo_crime=tipo_crime)
        removidos = len(_df_base) - len(novo)
        _df_base = novo
        _df_atual = _df_base.copy()
        destaques.atualizar_destaques(_df_atual)
        print(f"{removidos} ocorrência(s) removida(s).")
    except ValueError as erro:
        print(f"Não foi possível remover: {erro}")


def acao_filtrar_periodo() -> None:
    """Aplica um recorte temporal sobre o conjunto atual."""
    global _df_atual
    inicio = _ler_data("Início do período")
    fim = _ler_data("Fim do período")
    if inicio is None or fim is None:
        return
    try:
        _df_atual = periodo.filtra_dfPeriodo(_df_atual, inicio, fim)
        destaques.atualizar_destaques(_df_atual)
        print(f"Recorte aplicado: {len(_df_atual)} ocorrências no período.")
    except TypeError as erro:
        print(f"Erro no filtro de período: {erro}")


def acao_filtrar_crime() -> None:
    """Filtra o conjunto atual por um tipo de crime específico."""
    global _df_atual
    tipo = input("Tipo de crime: ").strip()
    try:
        _df_atual = crime.df_crime_espec(_df_atual, tipo)
        destaques.atualizar_destaques(_df_atual)
        print(f"Filtro aplicado: {len(_df_atual)} ocorrências do tipo '{tipo}'.")
    except TypeError as erro:
        print(f"Erro no filtro de crime: {erro}")


def acao_reset() -> None:
    """Remove os filtros, voltando ao conjunto completo."""
    global _df_atual
    _df_atual = _df_base.copy()
    destaques.atualizar_destaques(_df_atual)
    print("Filtros removidos.")


def acao_contagem_crime() -> None:
    """Mostra a contagem de ocorrências por tipo de crime."""
    contagem = crime.conta_ocor_tpCrime(_df_atual)
    if not contagem:
        print("Sem ocorrências para contar.")
        return
    print("\nOcorrências por tipo de crime:")
    for tipo, qtd in sorted(contagem.items(), key=lambda x: x[1], reverse=True):
        print(f"  {tipo}: {qtd}")


def acao_contagem_bairro() -> None:
    """Mostra a contagem de ocorrências por bairro."""
    try:
        contagem = crime.conta_ocor_bairro(_df_atual)
    except KeyError as erro:
        print(f"Erro: {erro}")
        return
    if not contagem:
        print("Sem ocorrências para contar.")
        return
    print("\nOcorrências por bairro:")
    for bairro, qtd in sorted(contagem.items(), key=lambda x: x[1], reverse=True):
        print(f"  {bairro}: {qtd}")


def acao_mapa(funcao, nome: str) -> None:
    """Gera um mapa usando a função de visualização informada."""
    try:
        if funcao(_df_atual):
            print(f"{nome} gerado com sucesso.")
        else:
            print(f"{nome} não gerado: não há coordenadas válidas.")
    except KeyError as erro:
        print(f"Erro ao gerar {nome}: {erro}")


def acao_destaques() -> None:
    """Exibe os destaques atuais (bairros em alerta e crime predominante)."""
    info = destaques.obter_destaques()
    print("\n--- Destaques ---")
    alertas = info["bairros_alerta"]
    if alertas:
        print("Bairros em alerta (acima da média de crimes):")
        for bairro, total in alertas:
            print(f"  {bairro}: {total} ocorrências")
    else:
        print("Nenhum bairro em alerta.")
    predominante = info["crime_por_bairro"]
    if predominante:
        print("Crime predominante por bairro:")
        for bairro, tipo in sorted(predominante.items()):
            print(f"  {bairro}: {tipo}")


MENU = """
========= Rio SafeWay =========
1  - Adicionar ocorrência
2  - Remover ocorrências
3  - Filtrar por período
4  - Filtrar por tipo de crime
5  - Remover filtros (dados completos)
6  - Contagem por tipo de crime
7  - Contagem por bairro
8  - Gerar bubble map
9  - Gerar heat map
10 - Gerar scatter plot map
11 - Ver destaques
0  - Sair
==============================="""


def main() -> None:
    """Laço principal: apresenta o menu e direciona as ações do usuário."""
    carregar()
    while True:
        print(MENU)
        opcao = input("Opção: ").strip()
        if opcao == "0":
            print("Encerrando o Rio SafeWay.")
            break
        elif opcao == "1":
            acao_adicionar()
        elif opcao == "2":
            acao_remover()
        elif opcao == "3":
            acao_filtrar_periodo()
        elif opcao == "4":
            acao_filtrar_crime()
        elif opcao == "5":
            acao_reset()
        elif opcao == "6":
            acao_contagem_crime()
        elif opcao == "7":
            acao_contagem_bairro()
        elif opcao == "8":
            acao_mapa(mapa.plot_bubbleMap, "Bubble map")
        elif opcao == "9":
            acao_mapa(mapa.plot_heatMap, "Heat map")
        elif opcao == "10":
            acao_mapa(mapa.plot_scatterPlotMap, "Scatter plot map")
        elif opcao == "11":
            acao_destaques()
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
