"""
Módulo Main — Rio SafeWay.

Orquestrador (front-end) da aplicação. Inicia o sistema, recupera o estado da
execução anterior, executa o laço de menu coordenando os módulos Dataframe,
Período, Crime, Mapa e Destaques apenas pelas interfaces (códigos de retorno e
cópias de primitivos), e grava o estado ao sair. Nunca enxerga a tabela: todos
os relatórios são montados a partir dos getters dos TADs.

Padrão da disciplina: módulo procedural; não define classes próprias e não
guarda a base (quem guarda é o Dataframe). Trata os códigos de retorno para que
a aplicação não quebre.
"""

import crime
import dataframe
import destaques
import periodo
import mapa

ARQUIVO_DADOS = "dados_crimes.csv"            # base inicial (primeira execução)
ARQUIVO_PERSISTENCIA = "estado_rio_safeway.csv"  # estado gravado entre execuções


def iniciar_sistema() -> bool:
    """Recupera o estado anterior; na primeira execução, carrega a base inicial."""
    if dataframe.recuperar(ARQUIVO_PERSISTENCIA) == dataframe.DF_CondRet.OK:
        dataframe.processar_coluna_bairros()
        print("Estado da execução anterior recuperado.")
        return True

    codigo = dataframe.carregar_dados(ARQUIVO_DADOS)
    if codigo == dataframe.DF_CondRet.FALHA:
        print(f"Arquivo '{ARQUIVO_DADOS}' não encontrado.")
        return False
    if codigo == dataframe.DF_CondRet.ERRO:
        print(f"Arquivo '{ARQUIVO_DADOS}' corrompido ou em formato incorreto.")
        return False

    dataframe.filtra_dados_invalidos()
    dataframe.processar_coluna_bairros()
    print("Sistema iniciado e base inicial carregada.")
    return True


def acao_adicionar() -> None:
    """Menu 1: adiciona uma nova ocorrência à base."""
    data = input("Data (AAAA-MM-DD): ").strip()
    latitude = input("Latitude: ").strip()
    longitude = input("Longitude: ").strip()
    tipo = input("Tipo de crime: ").strip()
    codigo = dataframe.adiciona_dado(data, latitude, longitude, tipo)
    if codigo == dataframe.DF_CondRet.OK:
        print("Ocorrência adicionada.")
    elif codigo == dataframe.DF_CondRet.FORA_LIMITES:
        print("Coordenadas fora dos limites do Rio de Janeiro.")
    else:
        print("Parâmetros inválidos ou nulos.")


def acao_remover() -> None:
    """Menu 2: remove ocorrências por critérios (campo em branco é ignorado)."""
    print("Deixe em branco os critérios que não quiser usar.")
    data = input("Data (AAAA-MM-DD): ").strip() or None
    tipo = input("Tipo de crime: ").strip() or None
    lat_txt = input("Latitude: ").strip()
    lon_txt = input("Longitude: ").strip()
    latitude = float(lat_txt) if lat_txt else None
    longitude = float(lon_txt) if lon_txt else None
    codigo = dataframe.remove_dados(data=data, latitude=latitude,
                                    longitude=longitude, tipo_crime=tipo)
    if codigo == dataframe.DF_CondRet.OK:
        print("Ocorrência(s) removida(s).")
    elif codigo == dataframe.DF_CondRet.FALHA:
        print("Nenhum registro encontrado com esses critérios.")
    else:
        print("Informe ao menos um critério (remoção total não permitida).")


def acao_filtrar_periodo() -> None:
    """Menu 3: aplica recorte temporal sobre a visão ativa."""
    inicio = input("Data de início (AAAA-MM-DD): ").strip()
    fim = input("Data de fim (AAAA-MM-DD): ").strip()
    codigo = periodo.aplicar_filtro_periodo(inicio, fim)
    if codigo == periodo.PER_CondRet.OK:
        print("Filtro de período aplicado.")
    elif codigo == periodo.PER_CondRet.FALHA:
        print("Datas inválidas (invertidas, iguais ou formato incorreto).")
    else:
        print("Período válido, mas sem ocorrências no intervalo.")


def acao_filtrar_crime() -> None:
    """Menu 4: filtra a visão ativa por um tipo de crime."""
    tipo = input("Tipo de crime: ").strip()
    codigo = crime.aplicar_filtro_crime(tipo)
    if codigo == crime.CRIME_CondRet.OK:
        print(f"Filtro de crime '{tipo}' aplicado.")
    elif codigo == crime.CRIME_CondRet.FALHA:
        print("Tipo de crime inválido.")
    else:
        print(f"Nenhuma ocorrência do tipo '{tipo}' na base atual.")


def acao_limpar_filtros() -> None:
    """Menu 5: remove todos os filtros e restaura a visão completa."""
    periodo.limpar_filtro_periodo()
    crime.limpar_filtro_crime()
    print("Filtros removidos.")


def relatorio_contagem_crime() -> None:
    """Menu 7: contagem de ocorrências por tipo de crime."""
    if crime.processar_contagem_tpCrime() == crime.CRIME_CondRet.FALHA:
        print("Sem ocorrências para contar.")
        return
    _, lista = crime.obter_lista_crimes()
    print("\nOcorrências por tipo de crime:")
    contagens = []
    for tipo in lista:
        _, qtd = crime.obter_qtd_crime(tipo)
        contagens.append((tipo, qtd))
    for tipo, qtd in sorted(contagens, key=lambda x: x[1], reverse=True):
        print(f"  {tipo}: {qtd}")


def relatorio_contagem_bairro() -> None:
    """Menu 8: contagem de ocorrências por bairro."""
    codigo = crime.processar_contagem_bairro()
    if codigo == crime.CRIME_CondRet.FALHA:
        print("Sem ocorrências para contar.")
        return
    if codigo == crime.CRIME_CondRet.ERRO:
        print("Coluna de bairros não processada.")
        return
    _, lista = crime.obter_lista_bairros()
    print("\nOcorrências por bairro:")
    contagens = []
    for bairro in lista:
        _, qtd = crime.obter_qtd_bairro(bairro)
        contagens.append((bairro, qtd))
    for bairro, qtd in sorted(contagens, key=lambda x: x[1], reverse=True):
        print(f"  {bairro}: {qtd}")


def relatorio_bairro_alerta() -> None:
    """Menu 9: bairro em alerta (acima da média)."""
    codigo = destaques.calcular_bairro_alerta()
    if codigo == destaques.DEST_CondRet.OK:
        _, nome, qtd = destaques.obter_bairro_alerta()
        print(f"\nBairro em alerta: {nome} ({qtd} ocorrências).")
    elif codigo == destaques.DEST_CondRet.FALHA:
        print("\nNenhum bairro estritamente acima da média.")
    else:
        print("\nImpossível calcular a média (0 ou 1 bairro na base).")


def relatorio_top_crime() -> None:
    """Menu 10: crime predominante por bairro."""
    if crime.processar_contagem_bairro() != crime.CRIME_CondRet.OK:
        print("Sem dados para o relatório.")
        return
    _, bairros = crime.obter_lista_bairros()
    print("\nCrime predominante por bairro:")
    for bairro in sorted(bairros):
        destaques.calcular_top_crime_pbairro(bairro)
        _, tipo = destaques.obter_top_crime_pbairro(bairro)
        print(f"  {bairro}: {tipo}")


def acao_relatorio_geral() -> None:
    """Menu 6: abre o relatório completo (estatísticas e destaques)."""
    relatorio_contagem_crime()
    relatorio_contagem_bairro()
    relatorio_bairro_alerta()
    relatorio_top_crime()


def acao_mapa(funcao, nome: str) -> None:
    """Menus 11-13: gera um mapa, tratando o código de retorno."""
    codigo = funcao()
    if codigo == mapa.MAPA_CondRet.OK:
        print(f"{nome} gerado com sucesso.")
    elif codigo == mapa.MAPA_CondRet.FALHA:
        print(f"{nome} abortado: base ativa vazia.")
    else:
        print(f"{nome} abortado: coordenadas ausentes ou corrompidas.")


MENU = """
============= Rio SafeWay =============
1  - Adicionar ocorrência
2  - Remover ocorrência
3  - Filtrar dados por período
4  - Filtrar dados por tipo de crime
5  - Limpar filtros
6  - Abrir Relatório (estatísticas)
7  - Relatório: Contagem por Tipo de Crime
8  - Relatório: Contagem por Bairro
9  - Relatório: Bairros em Alerta (Acima da Média)
10 - Relatório: Crime Predominante por Bairro
11 - Mapa de Bolhas
12 - Mapa de Calor
13 - Mapa de Dispersão
0  - Sair (grava automaticamente)
======================================"""


def main() -> None:
    """Inicia o sistema, executa o laço do menu e grava o estado ao sair."""
    iniciar_sistema()
    while True:
        print(MENU)
        opcao = input("Opção: ").strip()
        if opcao == "0":
            dataframe.gravar(ARQUIVO_PERSISTENCIA)
            print("Dados gravados. Encerrando o Rio SafeWay.")
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
            acao_limpar_filtros()
        elif opcao == "6":
            acao_relatorio_geral()
        elif opcao == "7":
            relatorio_contagem_crime()
        elif opcao == "8":
            relatorio_contagem_bairro()
        elif opcao == "9":
            relatorio_bairro_alerta()
        elif opcao == "10":
            relatorio_top_crime()
        elif opcao == "11":
            acao_mapa(mapa.plot_bubbleMap, "Mapa de bolhas")
        elif opcao == "12":
            acao_mapa(mapa.plot_heatMap, "Mapa de calor")
        elif opcao == "13":
            acao_mapa(mapa.plot_scatterPlotMap, "Mapa de dispersão")
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
