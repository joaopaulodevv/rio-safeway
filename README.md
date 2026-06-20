# Rio SafeWay

Aplicação de consulta visual e analítica sobre a incidência criminal no Rio de
Janeiro (INF1040 — Projeto de Programação Modular). Carrega ocorrências de um
arquivo CSV, permite filtrar por período e por tipo de crime, conta ocorrências
por crime e por bairro, gera visualizações geoespaciais (bubble map, heat map e
scatter plot map) e destaca os bairros em alerta e o crime predominante.

## Arquitetura modular

Cada TAD é um módulo (um arquivo `.py`) que **encapsula seu estado** em variáveis
de módulo prefixadas com `_` e expõe **apenas funções de acesso** e um `IntEnum`
de retorno:

| Módulo         | Arquivo        | Responsabilidade                                  |
|----------------|----------------|---------------------------------------------------|
| Dataframe      | `dataframe.py` | Carregar, limpar, inserir/remover e enriquecer    |
| Período        | `periodo.py`   | Validar e aplicar recorte temporal                |
| Crime          | `crime.py`     | Segmentar e contar por tipo de crime e por bairro |
| Mapa           | `mapa.py`      | Gerar bubble map, heat map e scatter plot map     |
| Destaques      | `destaques.py` | Bairro em alerta e crime predominante por bairro  |
| Main           | `main.py`      | Orquestrar o fluxo e a interface com o usuário     |

### Encapsulamento (tipo opaco)

O `pd.DataFrame` (base original + visão ativa após filtros) fica **totalmente
escondido** dentro do módulo Dataframe. Nenhum outro módulo recebe, lê ou altera
a tabela: todo o tráfego ocorre por **cópias de tipos primitivos** (str, int,
float) através das interfaces. Os módulos estatísticos e de mapa consomem os
dados registro a registro via `dataframe.obter_registro(indice)`.

Os erros previstos **não viram exceção**: cada função devolve um **código de
retorno** (`IntEnum`), em geral `1` (sucesso), `0` (falha prevista), `-1` (erro)
e `-2` (coordenadas fora dos limites). As interfaces que no C usariam ponteiros
de saída retornam aqui uma tupla `(codigo, valores...)`.

### Persistência entre execuções

O módulo Dataframe expõe `gravar(caminho)` e `recuperar(caminho)`. O `main.py`
chama `recuperar` ao iniciar e `gravar` ao sair (e na opção "Salvar dados"),
gravando o estado em `estado_rio_safeway.csv`. Na primeira execução, sem arquivo
de estado, carrega a base inicial `dados_crimes.csv`. Assim, ocorrências
adicionadas/removidas persistem de uma execução para a outra. Em runtime nada é
lido/escrito em arquivo como armazenamento de trabalho — os dados vivem em
memória encapsulada e só migram para o arquivo ao sair.

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Execução

```bash
python main.py
```

Os mapas são gravados como arquivos HTML (`mapa_bubble.html`, `mapa_heat.html`,
`mapa_scatter.html`) no diretório atual; abra-os no navegador.

## Testes

Cada módulo possui seu programa testador (`testa_<modulo>.py`). Os testes são
escritos como **funções** (não classes), montados em uma `TestSuite` com
`unittest.FunctionTestCase` e executados por arquivo:

```bash
python testa_dataframe.py
python testa_periodo.py
python testa_crime.py
python testa_mapa.py
python testa_destaques.py
```
