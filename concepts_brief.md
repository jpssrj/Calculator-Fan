# Calculadora Fan - Calculadora Web Neubrutalista de Alta Precisão

* **Autor:** Dev & Antigravity
* **Data:** 2026-11-01
* **Status:** Concluído (Multi-Lens Brainstorm Synthesis)

---

## Overview

A **Calculadora Fan** é uma aplicação web desenvolvida em Python (FastAPI) focada na resolução das quatro operações básicas da aritmética (`+`, `-`, `×`, `÷`) com rigor matemático absoluto e uma identidade visual autoral baseada no **Neubrutalismo**. 

Diferente de calculadoras convencionais que utilizam a função insegura `eval()` ou que dependem exclusivamente do ponto flutuante binário do navegador (suscetível a distorções como `0.1 + 0.2 = 0.30000000000000004`), o projeto implementa um interpretador seguro no backend utilizando a árvore de sintaxe abstrata (`ast`) do Python em conjunto com o módulo de precisão arbitrária `decimal.Decimal`.

Visualmente, o projeto traduz a estética Neubrutalista com bordas pretas grossas (3.5px), sombras projetadas em bloco duro sem desfoque (hard shadows), paleta de cores saturadas de alto contraste e uma fita retrátil de histórico inspirada em recibos e calculadoras de fita contínua.

---

## Analysis

### 1. Identidade Visual e Ergonomia Neubrutalista
* **Geometria e Traço:** Contornos sólidos pretos (`border: 3.5px solid #000000;`) em todos os botões, displays e painéis.
* **Profundidade Mecânica:** Sombras projetadas estáticas (`box-shadow: 5px 5px 0px #000000;`). No estado ativo (`:active` ou acionamento por teclado), o elemento se desloca fisicamente (`transform: translate(3px, 3px);` com sombra reduzida para `2px 2px 0px #000000`), simulando o clique tátil de um teclado mecânico.
* **Paleta Cromática Funcional:**
  * Base da página: Amarelo pastel ou marfim retrô (`#FEFCE8` / `#FFFDF0`).
  * Chassi: Branco puro com contorno espesso.
  * Visor: Ciano elétrico (`#C4F1F9`) com tipografia monoespaçada bold.
  * Dígitos: Branco com tipografia pesada em preto.
  * Operadores: Amarelo canário (`#FFE600`) e lilás (`#A78BFA`).
  * Botão de Execução (`=`): Verde neon vibrante (`#00F5D4`) em bloco duplo.
  * Botões de Controle (`AC`, `C`): Rosa choque (`#FF0055`).
* **Fita de Histórico Retrátil:** Gaveta lateral que simula papel contínuo de caixa registradora (com recorte superior serrilhado em SVG/CSS), registrando expressão, timestamp e resultado com botão de resgate (*Recall*) direto para o visor.

### 2. Motor Backend e Segurança Aritmética
* **Parser AST Seguro (Zero `eval`):** Avaliação de expressões por inspeção de nós da AST (`ast.parse(expr, mode='eval')`) com `NodeVisitor` restritivo. Apenas nós permitidos (`Expression`, `BinOp`, `UnaryOp`, `Constant`) são aceitos. Chamadas de função, atributos ou acessos de sistema são imediatamente barrados.
* **Aritmética com `decimal.Decimal`:** Todos os operandos são instanciados diretamente via string para o tipo `Decimal` sob precisão de 34 dígitos (padrão IEEE 754 decimal128), evitando conversão intermediária em float.
* **Serialização de Resposta:** Respostas numéricas trafegam no payload JSON como string formatada para evitar que o parser JSON do navegador execute coerção automática para `Float64`.

### 3. Usabilidade e Carga Cognitiva
* **Display Duplo:** Linha superior secundária com histórico da expressão em construção; linha principal em destaque com o operando corrente ou resultado final.
* **Tratamento de Exceções:** Erros de divisão por zero e sintaxe inválida exibem mensagens humanas claras no visor (`ERRO: DIVISÃO POR ZERO`, `SINTAXE INVÁLIDA`) acompanhadas de animação de tremor (*shake*) no display.
* **Mapeamento de Teclado Físico:** Captura global de eventos de teclado (Numpad, teclas de operadores, `Enter` para calcular, `Backspace` para apagar caractere, `Escape`/`C` para limpar tela e `H` para alternar a fita de histórico).

---

## Goals vs. Non-Goals

### In-Scope Goals
* Execução à prova de falhas das 4 operações aritméticas básicas (`+`, `-`, `*`, `/`) respeitando precedência e suporte a parênteses.
* Backend em Python utilizando **FastAPI** sem dependências de banco de dados.
* Frontend nativo e independente (HTML5 semântico, CSS3 Neubrutalista nativo, Vanilla JavaScript modular).
* Avaliador matemático seguro baseado em AST + `decimal.Decimal`.
* Fita de histórico retrátil com histórico de sessão e resgate de cálculo.
* Mapeamento integral e ergonômico de atalhos de teclado.

### Out-of-Scope Non-Goals
* Funções científicas avançadas (trigonometria, matrizes, números complexos, integrais).
* Persistência de dados em banco relacional externo (o histórico é retido na memória da sessão web).
* Autenticação de usuários, contas de acesso ou sincronização em nuvem.
* Frameworks pesados de frontend (React, Angular, Vue) que demandem pipelines de build (`npm build`, `webpack`).

---

## Alternatives Weighed

1. **Uso de `eval()` no Python:**
   * *Rejeitado.* Embora reduza o código do backend a uma linha, expõe a aplicação a injeção arbitrária de código (RCE) e negações de serviço.
2. **Cálculo inteiramente no Client com JavaScript nativo:**
   * *Rejeitado.* O JavaScript utiliza o formato IEEE 754 float de 64 bits, gerando erros aritméticos elementares (`0.1 + 0.2 = 0.30000000000000004`), além de descumprir o requisito fundamental do projeto de execução e backend em Python.
3. **Execução no navegador via PyScript / WebAssembly:**
   * *Rejeitado.* PyScript impõe um download inicial de ~15MB a 20MB de runtime Python no carregamento da página, degradando a performance e a usabilidade de uma calculadora simples.

---

## Key Decisions & Staging for Next Steps

* **Decisão 1:** A estrutura do projeto será dividida em `app/engine/evaluator.py` (lógica matemática pura), `app/schemas/` (validação Pydantic), `app/main.py` (rotas e arquivos estáticos) e `app/static/` (HTML/CSS/JS).
* **Decisão 2:** O display limitará visualmente números longos a 14 caracteres com notação científica elegante caso ultrapasse, preservando o valor integral na fita de histórico.
* **Decisão 3:** A fita de histórico terá botão para exportar o registro de contas em formato de texto (`.txt`) simulando recibo fiscal.
