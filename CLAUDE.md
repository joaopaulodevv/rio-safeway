# CLAUDE.md — Guia para o Trabalho de Programação Modular (PUC-Rio) — versão Python

Este arquivo orienta o desenvolvimento do trabalho da disciplina de Programação Modular em **Python**, seguindo **exatamente** o padrão de modularização ensinado em aula (originalmente em C, aqui adaptado). Consolida os conceitos relevantes das transcrições e prioriza os **critérios de avaliação** da apresentação.

> **Regra de ouro:** O trabalho é **procedural e modular** (não-OO). Cada TAD é um **módulo** (`.py`) que expõe **apenas funções de acesso**; a estrutura de dados fica **encapsulada dentro do módulo** (variável de módulo `_privada`, nunca tocada de fora).

---

## 0. Restrições inegociáveis (ler antes de codar)

- **Não criar classes próprias.** O paradigma é **procedural**: funções autocontidas organizadas em **módulos** (`arquivo.py`). Nada de `class MeuTAD:`.
- **Exceção sobre classes:** só é permitido **usar** uma classe quando ela **vier de uma biblioteca** e **obrigatoriamente precise ser instanciada** para funcionar — por exemplo `pandas.DataFrame`, `datetime.date`, `re.Pattern`, etc. Nesses casos a instância é tratada como um **valor/dado** manipulado pelas suas funções, não como o desenho do seu TAD. **Você nunca define suas próprias classes.**
- **Encapsular a estrutura do TAD.** O estado de cada TAD mora em variáveis **de módulo prefixadas com `_`** (convenção de privado em Python) e fica acessível **somente** pelas funções de acesso daquele módulo.
- **Esconder o estado.** O cliente importa **funções**, nunca a estrutura. Acesso de fora ao estado interno (ler/escrever `_variavel` de outro módulo, ou alcançar campos internos) é **proibido**.
- **Persistência só entre execuções.** Durante a execução os dados vivem em memória encapsulada. Arquivos servem **apenas** para gravar ao sair e recuperar ao iniciar — **nunca** como armazenamento de trabalho em runtime.

### Como simular "tipo opaco" em Python (substituto do ponteiro opaco do C)
O cliente recebe um **identificador/handle** (um `int`, uma chave, ou um dicionário opaco) e nunca mexe na estrutura por trás. O estado real fica numa variável `_` privada do módulo.

```python
# arvore.py  (MÓDULO SERVIDOR — esconde a estrutura)

# --- estado encapsulado: só este módulo acessa ---
_arvores = {}          # handle (int) -> estrutura interna
_proximo_id = 0

# --- códigos de retorno (equivalente ao enum do C) ---
from enum import IntEnum
class ARV_CondRet(IntEnum):     # IntEnum vem de biblioteca; uso permitido
    OK = 0
    ARVORE_VAZIA = 1
    NAO_ACHOU = 2

def criar():
    """Cria uma árvore e devolve um handle opaco."""
    global _proximo_id
    handle = _proximo_id
    _proximo_id += 1
    _arvores[handle] = {"raiz": None, "corrente": None}   # estrutura interna
    return handle

def inserir(handle, valor):
    arv = _arvores[handle]      # acesso interno OK (dentro do módulo dono)
    # ... lógica ...
    return ARV_CondRet.OK
```

```python
# mod.py  (CLIENTE — só usa a interface)
import arvore

cabeca = arvore.criar()         # OK: recebe só o handle
arvore.inserir(cabeca, 42)      # OK: usa só funções de acesso
# PROIBIDO:  arvore._arvores[cabeca]["raiz"]   <- acesso direto à estrutura -> zera o Critério 4
```

> Em C usava-se `typedef struct tpArvore *ptArvore;` para esconder os campos. Em Python o equivalente é: **handle opaco + estado em variável de módulo `_privada`**.

---

## 1. Critérios de avaliação (o que será cobrado na apresentação)

A parte mais importante. Cada item deve estar **garantido** antes da apresentação.

### Critério 1 — Aplicação funcionando (até 2,0)
| Nota | Condição |
|------|----------|
| 2,0  | Aplicação funcionando **corretamente** na hora da apresentação. |
| 1,0  | Funcionando com erros **apenas não-impeditivos**. |
| 0,0  | Não roda ou tem erros **impeditivos**. |

**Como garantir:**
- Rodar do zero em ambiente limpo (`python main.py`) imediatamente antes de apresentar; se usar libs externas, fixar versões em `requirements.txt` e testar a instalação.
- Testar o fluxo principal de ponta a ponta (criar → consultar → alterar → excluir → salvar → reabrir).
- Tratar entradas inválidas para o programa **não quebrar**: todo erro vira **código de retorno** (use o `IntEnum`), não uma exceção não-tratada que derruba a execução.
- Ter um roteiro de demonstração que exercite as funcionalidades centrais sem improviso.

### Critério 2 — Testes automatizados (até 2,0)
| Nota | Condição |
|------|----------|
| 2,0  | Testes **completos** e rodando **sem erro**. |
| 1,0  | Testes **incompletos**, mas rodando sem erro. |
| 0,0  | **Pelo menos um** teste rodando com erro. |

**Como garantir:**
- Ter um **módulo de testes** (use `unittest` ou `pytest` — uso permitido) que exercite **cada função de acesso de cada TAD**.
- Cobrir, para cada função, **todos os retornos possíveis** (`OK`, "já existe", "não achou", "parâmetro inválido", "estrutura vazia" etc.).
- Cobrir os três tipos de caso vistos em aula:
  - **Abstratos** (o que testar): inclusão OK, inclusão de existente, parâmetro nulo.
  - **Semânticos** (como testar): incluir matrícula inexistente; incluir matrícula já existente.
  - **Valorados** (executáveis): `incluir_aluno(1234, "Flávio")` → espera `0`; rodar de novo → espera `1`; `incluir_aluno("", "")` → espera `2`.

```python
# test_aluno.py
import unittest
import aluno

class TestAluno(unittest.TestCase):
    def setUp(self):
        aluno.resetar()                 # estado limpo a cada teste
    def test_inclusao_ok(self):
        self.assertEqual(aluno.incluir(1234, "Flávio"), aluno.ALU_CondRet.OK)
    def test_inclusao_duplicada(self):
        aluno.incluir(1234, "Flávio")
        self.assertEqual(aluno.incluir(1234, "André"), aluno.ALU_CondRet.JA_EXISTE)
    def test_parametro_invalido(self):
        self.assertEqual(aluno.incluir("", ""), aluno.ALU_CondRet.PARAM_INVALIDO)

if __name__ == "__main__":
    unittest.main()
```

> **Garantir 100% verde.** Um único teste com erro **zera** este critério. Rodar a suíte inteira (`python -m pytest` ou `python -m unittest`) e confirmar tudo passando antes de apresentar.

### Critério 3 — Especificação de todas as funções de acesso (até 2,0)
| Nota | Condição |
|------|----------|
| 2,0  | **Todas** as funções com especificação **completa**. |
| 1,0  | Todas têm especificação, mas **pelo menos uma incompleta**. |
| 0,0  | **Pelo menos uma** função de acesso **sem** especificação. |

**Como garantir:** especificar **toda** função de acesso em **docstring** logo abaixo do `def`, seguindo o housekeeping da aula:
- **Objetivo** (opcional só se o nome já for autoexplicativo).
- **Acoplamento** — para cada **parâmetro** de entrada e saída: nome + significado.
- **Retornos possíveis** — cada valor (do `IntEnum`) com sua descrição.
- **Assertivas de entrada** — o que deve valer antes da chamada.
- **Assertivas de saída** — o que valerá após sucesso (incluindo assertivas estruturais da estrutura de dados).
- **Hipóteses/restrições** (opcional) e **interface com usuário** (opcional).

```python
def excluir(handle, matricula):
    """
    Objetivo: exclui o aluno de dada matrícula da base encapsulada.

    Acoplamento:
        handle    (entrada): identificador opaco da base de alunos.
        matricula (entrada): inteiro, matrícula do aluno a excluir.

    Retornos:
        ALU_CondRet.OK             (0): aluno excluído.
        ALU_CondRet.NAO_ACHOU      (2): matrícula não existe na base.
        ALU_CondRet.PARAM_INVALIDO (3): matrícula nula/inválida.

    Assertiva de entrada: a base existe e contém zero ou mais alunos.
    Assertiva de saída: o aluno não está mais na base; valem as
        assertivas estruturais da base (sem duplicatas, índices íntegros).
    """
```

> Conferir uma a uma: nenhuma função de acesso pode ficar sem docstring de especificação. Basta **uma** faltando para a nota cair a 0.

### Critério 4 — Modularização de TADs (até 3,0) — **maior peso**
| Nota | Condição |
|------|----------|
| 3,0  | **Todos** os módulos com estruturas **encapsuladas**, expondo **apenas** as funções de acesso, **exatamente** no padrão da disciplina. |
| 1,5  | **Pelo menos um** módulo acessando **arquivos** para armazenamento (em vez de armazenar em estruturas encapsuladas no TAD). |
| 0,0  | **Pelo menos uma** estrutura que deveria estar encapsulada sendo **acessada diretamente** de fora. |

**Como garantir o 3,0 (padrão exato da disciplina, em Python):**
- Cada TAD é **um módulo `.py`**. O estado fica em variáveis **`_privadas` de módulo**; o módulo expõe **só funções de acesso** e o `IntEnum` de retorno.
- O cliente **importa funções**, nunca o estado:
  ```python
  import aluno
  h = aluno.criar()
  aluno.incluir(h, 1234, "Flávio")   # OK
  # PROIBIDO: aluno._base[...]        # acesso direto -> zera o critério (0,0)
  ```
- **Não definir classes próprias.** Se aparecer `class XGenerico:` definida por você representando o TAD, está fora do padrão. (Instâncias de classes **de biblioteca**, como `pd.DataFrame`, são apenas dados internos do módulo — permitido.)
- **Atenção ao 1,5:** o estado de trabalho **não** pode morar em arquivo durante a execução. Os dados ficam em **estruturas em memória encapsuladas** (dict/list em variáveis `_`). Arquivo só entra no Critério 5.
- **Atenção ao 0,0:** varrer o código procurando qualquer leitura/escrita de `_variavel` de um módulo feita por **outro** módulo, ou acesso a campos internos por fora do dono. Se existir, corrigir antes de apresentar.

> Dica de verificação: `grep -rn "modulo\._" .` para achar acessos ao estado privado feitos de fora do módulo dono.

### Critério 5 — Persistência só entre execuções (até 1,0)
| Nota | Condição |
|------|----------|
| 1,0  | **Todos** os dados encapsulados são gravados em arquivo no **final** da execução e **recuperados** numa nova execução. |
| 0,0  | **Pelo menos um** dado não for gravado ao final e recuperado depois. |

**Como garantir:**
- Cada TAD com estado expõe `gravar(caminho)` e `recuperar(caminho)`, chamadas pelo `main.py` **ao sair** e **ao iniciar**.
- A gravação/leitura é feita **pelo próprio módulo dono** (ele conhece a estrutura), preservando o encapsulamento. Formatos: `json`, `pickle` ou `csv` (todos da stdlib — uso permitido).
- Teste de aceitação: rodar → inserir dados → sair → **reabrir** → confirmar que **tudo** voltou. Validar para **todos** os dados encapsulados.
- Durante a execução, **nada** é lido/escrito em arquivo como armazenamento de trabalho (isso é o problema do Critério 4 = 1,5).

```python
# aluno.py
import json

def gravar(caminho):
    """Serializa o estado encapsulado em arquivo (chamado ao final)."""
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(_base, f, ensure_ascii=False)
    return ALU_CondRet.OK

def recuperar(caminho):
    """Recarrega o estado encapsulado de arquivo (chamado ao iniciar)."""
    global _base
    try:
        with open(caminho, encoding="utf-8") as f:
            _base = json.load(f)
    except FileNotFoundError:
        _base = {}        # primeira execução: começa vazio
    return ALU_CondRet.OK
```

**Classes de memória (da aula, mapeadas para Python):** automática (variáveis locais na pilha), estática visível (globais de módulo "públicas"), **estática encapsulada (variáveis `_privadas` de módulo — o coração do TAD)**, **dinâmica (objetos no heap: dict/list/instâncias)** e **persistente (arquivos, entre execuções)**. Em runtime os dados do TAD vivem na encapsulada/dinâmica e migram para a persistente só ao sair.

---

## 2. Conceitos de implementação (da disciplina, em Python)

### Espaço de dados
Área de armazenamento com nome de referência. Em Python: nomes ligados a objetos (`a[i]`, chave de dict, atributo de objeto de biblioteca).

### Definir × Declarar (no contexto Python)
Python não separa declaração de definição como C. Um nome passa a existir quando é **atribuído** (`a = 0` cria e liga o nome ao objeto). Mantenha a disciplina conceitual: saiba **onde** cada dado nasce e **quem** é o dono dele (o módulo do TAD).

### Tipos de dados
- **Computacionais:** `int`, `float`, `str`, `bool`.
- **Definidos pelo usuário (sem classes próprias):** combinações de `dict`, `list`, `tuple`, `namedtuple`/`IntEnum`/`dataclass` quando vierem da stdlib e forem usados como **dados**, não como desenho de TAD.
- **TAD:** um **módulo** com estado encapsulado + funções de acesso (foco do trabalho).

### Equivalências C → Python
| Conceito em C | Equivalente em Python |
|---|---|
| `enum` de retorno | `IntEnum` (com valores 0,1,2…) |
| `struct` | `dict` (ou `namedtuple`/`dataclass` da stdlib, como dado interno) |
| `union` | `dict` com chave de tipo + campo variável |
| `typedef` | alias de tipo / nomeação clara |
| `static` (encapsulado no módulo) | variável de módulo prefixada com `_` |
| `extern`/global exportado | nome de módulo importado |
| ponteiro opaco (`typedef struct *`) | handle opaco (int/chave) + estado `_privado` |
| ponteiro para função (hotspot) | passar uma **função como parâmetro** (callbacks) |
| `#include` guards / dependência circular | organizar imports; evitar import circular separando responsabilidades |

### Função como parâmetro (hotspot — equivale ao ponteiro para função em C)
```python
def processa_area(v1, v2, func):
    print(func(v1, v2))
    return OK

def area_tri(base, altura):  return base * altura / 2
def area_quad(base, altura): return base * altura

processa_area(3, 2, area_tri)    # comportamento comum + hotspot (a função)
processa_area(4, 2, area_quad)
```

---

## 3. Padrões de modularização

- **Divisão e Conquista:** vencer a complexidade por decomposição sucessiva; decidir o que é reutilizável; projetar top-down e/ou bottom-up.
- **Abstração:** separar **o quê** (requisito) de **como** (projeto/implementação); funções com nomes que expressam intenção (ex.: `apresenta_menu_executivo()`).
- **Encapsulamento:** proteger dados; expor só funções de acesso; um módulo não enxerga o estado interno do outro. **(Base do Critério 4.)** Em Python: estado em variáveis `_privadas` de módulo.
- **Wrappers:** funções que fixam parâmetros e expõem só os variáveis (ex.: `gera_relat_empresa()` chamando `gera_relatorio()` com cabeçalho/rodapé/fonte fixos). Em Python, `functools.partial` é uma forma idiomática de wrapper.

---

## 4. Qualidade da decomposição (conjunto solução)

- **Necessidade:** todo elemento é necessário.
- **Suficiência:** os elementos bastam para resolver o problema.
- **Ortogonalidade:** o que um componente faz, nenhum outro faz.
- **Complexidade:** o conjunto fica de fácil entendimento.
- **Coesão alta / acoplamento baixo:** cada módulo trata de **um** conceito (extrair módulos quando há mais de um).
- **Direção de projeto:** top-down (especialização), bottom-up (integração/reutilização) ou mista.

---

## 5. Estrutura de funções e chamadas

- **Função:** porção autocontida de código (tudo que precisa está nela: parâmetros e retornos).
- **Assinatura:** `def f(...):`.
- **Arco de chamadas:** cadeia de chamadas entre funções.
- **Recursiva direta:** `f9 -> f9`.
- **Recursiva indireta:** `f2 -> f3 -> f4 -> f2`.
- **Dependência circular entre módulos:** imports que se fecham atravessando módulos — em Python causa `ImportError`; resolver separando responsabilidades ou importando dentro da função.
- **Função morta:** sem chamadores — eliminar.

### Esquema de algoritmo (comportamento comum + hotspots)
Repetição/recursão têm um **comportamento comum** (controlar, processar estado corrente, definir próximo estado, terminar) e **hotspots** = partes específicas a instanciar (ex.: a função de comparação passada como parâmetro). **Descritor de estado** = variável(is) que definem o estado (ex.: `inf`/`sup` na busca binária; `ind` na busca sequencial).

---

## 6. Assertivas (entrada/saída)

```
AE -> [bloco de código] -> AS      (AE + Bloco => AS)
```
- **Assertiva estrutural:** regras válidas na estrutura de dados (invariantes da lista/dict/etc.).
- **Assertiva de entrada (AE):** o que deve valer antes (ex.: a estrutura tem ≥ 1 elemento; o corrente aponta para o item a remover).
- **Assertiva de saída (AS):** o que vale depois (ex.: item removido; valem as assertivas estruturais; corrente passa a apontar para o primeiro ou `None` se vazia).
> Em Python, dá para reforçar assertivas em pontos críticos com `assert`, mas **erros previstos viram código de retorno** (`IntEnum`), não exceção. As AE/AS entram na **especificação** (Critério 3).

---

## 7. TDD — Desenvolvimento Orientado a Testes

O código nasce **a partir dos casos de teste**. Fluxo: Requisito → Casos de teste → Funções de acesso → Retornos possíveis e casos de teste.

**Preparação:** definir casos **abstratos** (o que testar), **semânticos** (como testar) e **valorados** (executáveis, com retorno esperado).

**Ciclo Red-Green-Refactor, por caso de teste:**
1. Rodar a função e ver o teste **falhar** (`unittest`/`pytest`).
2. Implementar o código mínimo para **passar**.
3. Rodar e **passar**.
4. **Refatorar** o código.
5. Reexecutar o teste para garantir que a refatoração **não introduziu erros**.
6. Seguir para o próximo caso.

Exemplo de função alvo e retornos (padrão da aula):
```python
def incluir_aluno(matr, nome):
    if _existe(matr):              return ALU_CondRet.JA_EXISTE      # 1
    if not matr or not nome:       return ALU_CondRet.PARAM_INVALIDO # 2
    _base[matr] = nome
    return ALU_CondRet.OK                                           # 0
```
> Este ciclo alimenta diretamente o **Critério 2** (suíte completa e verde).

---

## 8. Refatoração

- **Definição:** melhorar o código **sem alterar o comportamento**. Objetivo: facilitar manutenção e entendimento.
- **Motivação:** duplicação, variáveis/campos mal posicionados, estilos divergentes, blocos extensos, má identação.
- **Técnicas:** extrair funções; mover variáveis para o módulo dono; **extrair módulos** (baixa→alta coesão); renomear funções; agrupar muitos parâmetros num `dict`/`namedtuple`; quebrar estruturas grandes em subestruturas.
- A refatoração melhora a **qualidade de encapsulamento** (mover estado para o módulo dono, separar conceitos) — útil para reforçar o Critério 4.

---

## 9. Reutilização

- Evita "reinventar a roda"; via de mão dupla (desenvolvedor ↔ usuário, com feedback).
- **Formas:** snippets; **módulos e pacotes** (`.py` importáveis); bibliotecas da stdlib e de terceiros.
- **Qualidade de componente reutilizável:** resolve problema geral, segue padrões amplos, é bem documentado, é unidade independente com **imports relativos/por nome de módulo** (não caminhos absolutos de disco) e dependências externas informadas (`requirements.txt`).

---

## 10. Checklist final antes da apresentação

- [ ] Roda do zero em ambiente limpo (`python main.py`); `requirements.txt` testado se houver libs. → Critério 1
- [ ] Fluxo completo demonstrável (criar/consultar/alterar/excluir). → Critério 1
- [ ] **Nenhuma classe própria** definida; só instâncias de classes **de biblioteca** que exigem instanciação (ex.: `pd.DataFrame`). → Restrição
- [ ] **Nenhum** estado `_privado` de um módulo acessado por outro (`grep -rn "modulo\._"`). → Critério 4
- [ ] Cada TAD é um módulo que expõe só funções de acesso + `IntEnum` de retorno; estado em variáveis `_`. → Critério 4
- [ ] **Toda** função de acesso com docstring de especificação (objetivo, acoplamento, retornos, AE/AS). → Critério 3
- [ ] Suíte de testes cobre todos os retornos de todas as funções e está **100% verde** (`pytest`/`unittest`). → Critério 2
- [ ] Gravar ao sair + recuperar ao iniciar funcionando para **todos** os dados (teste reabrir). → Critério 5
- [ ] Nenhum arquivo usado como armazenamento **durante** a execução. → Critério 4 (evita o 1,5) / Critério 5