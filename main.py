"""
Módulo Main — Rio SafeWay.

Orquestrador (front-end) da aplicação. Inicia o sistema, carrega os dados e
executa o laço de menu, coordenando os módulos Dataframe, Período, Crime, Mapa
e Destaques apenas pelas interfaces (códigos de retorno e cópias de primitivos).
Nunca enxerga a tabela: todos os relatórios são montados a partir dos getters
dos TADs.

Padrão da disciplina: módulo procedural; não define classes próprias e não
guarda a base (quem guarda é o Dataframe). Trata os códigos de retorno para que
a aplicação não quebre.
"""

import crime
import dataframe
import destaques
import periodo
import mapa

ARQUIVO_DADOS = "dados_crimes.csv"


def iniciar_sistema() -> bool:
    """Carrega, limpa e enriquece os dados. Devolve True se houver base útil."""
    codigo = dataframe.carregar_dados(ARQUIVO_DADOS)
    if codigo == dataframe.DF_CondRet.FALHA:
        print(f"Arquivo '{ARQUIVO_DADOS}' não encontrado.")
        return False
    if codigo == dataframe.DF_CondRet.ERRO:
        print(f"Arquivo '{ARQUIVO_DADOS}' corrompido ou em formato incorreto.")
        return False

    dataframe.filtra_dados_invalidos()
    dataframe.processar_coluna_bairros()
    print("Sistema iniciado e dados carregados.")
    return True


def acao_filtrar_periodo() -> None:
    """Menu 1: aplica recorte temporal sobre a visão ativa."""
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
    """Menu 2: filtra a visão ativa por um tipo de crime."""
    tipo = input("Tipo de crime: ").strip()
    codigo = crime.aplicar_filtro_crime(tipo)
    if codigo == crime.CRIME_CondRet.OK:
        print(f"Filtro de crime '{tipo}' aplicado.")
    elif codigo == crime.CRIME_CondRet.FALHA:
        print("Tipo de crime inválido.")
    else:
        print(f"Nenhuma ocorrência do tipo '{tipo}' na base atual.")


def acao_limpar_filtros() -> None:
    """Menu 3: remove todos os filtros e restaura a visão completa."""
    periodo.limpar_filtro_periodo()
    crime.limpar_filtro_crime()
    print("Filtros removidos.")


def relatorio_contagem_crime() -> None:
    """Menu 5: contagem de ocorrências por tipo de crime."""
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
    """Menu 6: contagem de ocorrências por bairro."""
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
    """Menu 7: bairro em alerta (acima da média)."""
    codigo = destaques.calcular_bairro_alerta()
    if codigo == destaques.DEST_CondRet.OK:
        _, nome, qtd = destaques.obter_bairro_alerta()
        print(f"\nBairro em alerta: {nome} ({qtd} ocorrências).")
    elif codigo == destaques.DEST_CondRet.FALHA:
        print("\nNenhum bairro estritamente acima da média.")
    else:
        print("\nImpossível calcular a média (0 ou 1 bairro na base).")


def relatorio_top_crime() -> None:
    """Menu 8: crime predominante por bairro."""
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
    """Menu 4: abre o relatório completo (estatísticas e destaques)."""
    relatorio_contagem_crime()
    relatorio_contagem_bairro()
    relatorio_bairro_alerta()
    relatorio_top_crime()


def acao_mapa(funcao, nome: str) -> None:
    """Menus 9-11: gera um mapa, tratando o código de retorno."""
    codigo = funcao()
    if codigo == mapa.MAPA_CondRet.OK:
        print(f"{nome} gerado com sucesso.")
    elif codigo == mapa.MAPA_CondRet.FALHA:
        print(f"{nome} abortado: base ativa vazia.")
    else:
        print(f"{nome} abortado: coordenadas ausentes ou corrompidas.")


MENU = """
============= Rio SafeWay =============
1  - Filtrar dados por período
2  - Filtrar dados por tipo de crime
3  - Limpar filtros
4  - Abrir Relatório (estatísticas)
5  - Relatório: Contagem por Tipo de Crime
6  - Relatório: Contagem por Bairro
7  - Relatório: Bairros em Alerta (Acima da Média)
8  - Relatório: Crime Predominante por Bairro
9  - Mapa de Bolhas
10 - Mapa de Calor
11 - Mapa de Dispersão
12 - Sair
======================================"""


def main() -> None:
    """Inicia o sistema e executa o laço principal do menu."""
    iniciar_sistema()
    while True:
        print(MENU)
        opcao = input("Opção: ").strip()
        if opcao == "12":
            print("Encerrando o Rio SafeWay.")
            break
        elif opcao == "1":
            acao_filtrar_periodo()
        elif opcao == "2":
            acao_filtrar_crime()
        elif opcao == "3":
            acao_limpar_filtros()
        elif opcao == "4":
            acao_relatorio_geral()
        elif opcao == "5":
            relatorio_contagem_crime()
        elif opcao == "6":
            relatorio_contagem_bairro()
        elif opcao == "7":
            relatorio_bairro_alerta()
        elif opcao == "8":
            relatorio_top_crime()
        elif opcao == "9":
            acao_mapa(mapa.plot_bubbleMap, "Mapa de bolhas")
        elif opcao == "10":
            acao_mapa(mapa.plot_heatMap, "Mapa de calor")
        elif opcao == "11":
            acao_mapa(mapa.plot_scatterPlotMap, "Mapa de dispersão")
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
