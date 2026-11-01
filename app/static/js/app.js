/**
 * CALCULATOR FAN - GERENCIADOR DE ESTADO E COMUNICAÇÃO (APP.JS)
 * Orquestra as regras aritméticas, chamadas assíncronas ao FastAPI e a Fita de Histórico.
 */

(function () {
  'use strict';

  const API_ENDPOINT = '/api/calculate';

  // Elementos do DOM
  const mainDisplay = document.getElementById('main-display');
  const subDisplay = document.getElementById('sub-display');
  const activeOpBadge = document.getElementById('active-op-badge');
  const tapeDrawer = document.getElementById('tape-drawer');
  const tapeEntries = document.getElementById('tape-entries');
  const btnToggleHistory = document.getElementById('btn-toggle-history');
  const btnCloseTape = document.getElementById('btn-close-tape');
  const btnClearTape = document.getElementById('btn-clear-tape');
  const btnExportTape = document.getElementById('btn-export-tape');
  const sessionTimeEl = document.getElementById('tape-session-time');

  // Estado da Aplicação
  const state = {
    expression: '',        // Expressão em construção (ex: "12 + 45")
    lastResult: null,      // Último resultado retornado pela API
    isCalculated: false,   // Indica se o visor exibe o resultado final
    isError: false,        // Indica se está em estado de erro
    historyTape: []        // Pilha de registros da sessão
  };

  /**
   * Atualiza os visores da calculadora.
   */
  function updateDisplay() {
    if (state.isError) {
      mainDisplay.classList.add('is-error');
      activeOpBadge.textContent = 'ERRO';
      return;
    }

    mainDisplay.classList.remove('is-error');

    if (state.isCalculated && state.lastResult !== null) {
      mainDisplay.textContent = state.lastResult;
      subDisplay.textContent = `${state.expression} =`;
      activeOpBadge.textContent = 'DONE';
    } else {
      const displayValue = state.expression.trim() || '0';
      mainDisplay.textContent = displayValue;
      subDisplay.innerHTML = '&nbsp;';

      // Detecta operador ativo para a badge
      const lastToken = state.expression.trim().split(' ').pop();
      if (['+', '-', '×', '÷', '%', '^'].includes(lastToken)) {
        activeOpBadge.textContent = `OP: ${lastToken}`;
      } else {
        activeOpBadge.textContent = state.expression ? 'DIGIT' : 'IDLE';
      }
    }
  }

  /**
   * Trata a inserção de dígitos, operadores e parênteses.
   */
  function handleInsert(value) {
    if (state.isError) {
      state.isError = false;
      state.expression = '';
    }

    const isOp = ['+', '-', '×', '÷', '%', '^'].includes(value);

    // Se acabou de calcular:
    if (state.isCalculated) {
      state.isCalculated = false;
      if (isOp) {
        // Encadeia o cálculo anterior com o novo operador
        state.expression = `${state.lastResult} ${value} `;
        updateDisplay();
        return;
      } else {
        // Se digitou número ou parênteses, reinicia nova conta
        state.expression = '';
      }
    }

    // Se for operador aritmético
    if (isOp) {
      const trimmed = state.expression.trim();
      if (!trimmed) {
        // Permite unário negativo inicial
        if (value === '-') {
          state.expression = '-';
        }
        updateDisplay();
        return;
      }

      const tokens = trimmed.split(' ');
      const lastToken = tokens[tokens.length - 1];

      // Substitui o operador anterior se for consecutivo
      if (['+', '-', '×', '÷', '%', '^'].includes(lastToken)) {
        tokens[tokens.length - 1] = value;
        state.expression = tokens.join(' ') + ' ';
      } else {
        state.expression = `${trimmed} ${value} `;
      }
    } else {
      // Dígitos ou parênteses
      state.expression += value;
    }

    updateDisplay();
  }

  /**
   * Trata a inserção do ponto decimal com validação de duplicidade.
   */
  function handleDecimal() {
    if (state.isError || state.isCalculated) {
      state.isError = false;
      state.isCalculated = false;
      state.expression = '0.';
      updateDisplay();
      return;
    }

    const tokens = state.expression.trim().split(' ');
    const currentToken = tokens[tokens.length - 1] || '';

    // Se o termo atual já possuir ponto, impede duplicidade
    if (currentToken.includes('.')) {
      return;
    }

    if (!currentToken || ['+', '-', '×', '÷', '%', '^', '('].includes(currentToken)) {
      state.expression += (state.expression.endsWith(' ') ? '' : ' ') + '0.';
    } else {
      state.expression += '.';
    }

    updateDisplay();
  }

  /**
   * Inverte o sinal (positivo/negativo) do operando ativo.
   */
  function handleNegate() {
    if (state.isCalculated && state.lastResult !== null) {
      state.isCalculated = false;
      state.expression = state.lastResult.startsWith('-')
        ? state.lastResult.substring(1)
        : `-${state.lastResult}`;
      updateDisplay();
      return;
    }

    const trimmed = state.expression.trim();
    if (!trimmed) {
      state.expression = '-';
      updateDisplay();
      return;
    }

    const tokens = trimmed.split(' ');
    let lastToken = tokens[tokens.length - 1];

    if (/^-?\d+(\.\d+)?$/.test(lastToken)) {
      if (lastToken.startsWith('-')) {
        tokens[tokens.length - 1] = lastToken.substring(1);
      } else {
        tokens[tokens.length - 1] = `-${lastToken}`;
      }
      state.expression = tokens.join(' ');
      updateDisplay();
    }
  }

  /**
   * Apaga o último caractere ou operador.
   */
  function handleBackspace() {
    if (state.isError || state.isCalculated) {
      handleClearAll();
      return;
    }

    let expr = state.expression.trimEnd();
    if (expr.length > 0) {
      state.expression = expr.slice(0, -1).trimEnd();
    }
    updateDisplay();
  }

  /**
   * Limpa todo o visor e reseta o estado (AC).
   */
  function handleClearAll() {
    state.expression = '';
    state.lastResult = null;
    state.isCalculated = false;
    state.isError = false;
    updateDisplay();
  }

  /**
   * Envia a expressão para avaliação segura no backend FastAPI.
   */
  async function handleCalculate() {
    const rawExpr = state.expression.trim();
    if (!rawExpr || state.isCalculated) return;

    activeOpBadge.textContent = 'CALC...';

    try {
      const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expression: rawExpr })
      });

      const data = await response.json();

      if (response.ok && data.status === 'success') {
        state.lastResult = data.result;
        state.isCalculated = true;
        state.isError = false;

        // Registra na fita de auditoria
        appendTapeEntry(rawExpr, data.result);
        updateDisplay();
      } else {
        state.isError = true;
        state.lastResult = null;
        mainDisplay.textContent = data.error || 'SINTAXE INVÁLIDA';
        updateDisplay();
      }
    } catch (err) {
      state.isError = true;
      mainDisplay.textContent = 'ERRO DE CONEXÃO COM O SERVIDOR';
      updateDisplay();
    }
  }

  /**
   * Registra uma nova entrada na Fita de Histórico.
   */
  function appendTapeEntry(expr, result) {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('pt-BR', { hour12: false });

    const entry = {
      id: Date.now(),
      time: timeStr,
      expression: expr,
      result: result
    };

    state.historyTape.unshift(entry);
    renderTape();
  }

  /**
   * Renderiza os cartões da Fita de Histórico.
   */
  function renderTape() {
    if (state.historyTape.length === 0) {
      tapeEntries.innerHTML = `
        <div class="tape-empty-state">
          <p>NENHUM CÁLCULO REGISTRADO</p>
          <small>Execute uma operação para imprimir na fita.</small>
        </div>
      `;
      return;
    }

    tapeEntries.innerHTML = state.historyTape.map(item => `
      <div class="tape-item" data-id="${item.id}">
        <span class="tape-item-time">[${item.time}]</span>
        <div class="tape-item-expr">${escapeHtml(item.expression)}</div>
        <div class="tape-item-result-row">
          <span class="tape-item-result">= ${escapeHtml(item.result)}</span>
          <button class="btn-recall" data-result="${escapeHtml(item.result)}" title="Carregar resultado no visor">
            RECALL
          </button>
        </div>
      </div>
    `).join('');

    // Adiciona listener para os botões de recall
    tapeEntries.querySelectorAll('.btn-recall').forEach(btn => {
      btn.addEventListener('click', function () {
        const val = this.getAttribute('data-result');
        state.isCalculated = false;
        state.isError = false;
        state.expression = val;
        updateDisplay();
      });
    });
  }

  /**
   * Exporta a fita de histórico como arquivo TXT estilizado.
   */
  function exportTapeAsTxt() {
    if (state.historyTape.length === 0) {
      alert('A fita está vazia. Realize cálculos antes de exportar.');
      return;
    }

    const dateStr = new Date().toLocaleDateString('pt-BR');
    let content = '========================================\n';
    content += '   CALCULATOR FAN - EXTRATO DE SESSÃO\n';
    content += `   DATA: ${dateStr}\n`;
    content += '========================================\n\n';

    state.historyTape.slice().reverse().forEach((item, idx) => {
      content += `[${idx + 1}] ${item.time}\n`;
      content += `EXPR : ${item.expression}\n`;
      content += `TOTAL: = ${item.result}\n`;
      content += '----------------------------------------\n';
    });

    content += '\nFIM DO RECIBO. GERADO VIA PYTHON FASTAPI.\n';

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `recibo-calculator-fan-${Date.now()}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  /**
   * Sanitizador básico de HTML para prevenir XSS no DOM.
   */
  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  /**
   * Alterna a visibilidade da Fita de Histórico.
   */
  function toggleTapeDrawer() {
    tapeDrawer.classList.toggle('is-hidden');
    btnToggleHistory.classList.toggle('is-active', !tapeDrawer.classList.contains('is-hidden'));
  }

  /**
   * Roteador de ações disparadas pelos botões ou pelo módulo de teclado.
   */
  function handleAction(action, value) {
    switch (action) {
      case 'insert':
        handleInsert(value);
        break;
      case 'decimal':
        handleDecimal();
        break;
      case 'negate':
        handleNegate();
        break;
      case 'backspace':
        handleBackspace();
        break;
      case 'clear-all':
        handleClearAll();
        break;
      case 'calculate':
        handleCalculate();
        break;
      case 'toggle-history':
        toggleTapeDrawer();
        break;
      default:
        console.warn('Ação desconhecida:', action);
    }
  }

  // Inicialização de Eventos
  document.querySelectorAll('.key').forEach(button => {
    button.addEventListener('click', () => {
      const action = button.getAttribute('data-action');
      const value = button.getAttribute('data-value');
      handleAction(action, value);
    });
  });

  btnToggleHistory.addEventListener('click', toggleTapeDrawer);
  btnCloseTape.addEventListener('click', toggleTapeDrawer);

  btnClearTape.addEventListener('click', () => {
    state.historyTape = [];
    renderTape();
  });

  btnExportTape.addEventListener('click', exportTapeAsTxt);

  // Inicializa a hora da sessão
  if (sessionTimeEl) {
    sessionTimeEl.textContent = `SESSÃO INICIADA: ${new Date().toLocaleTimeString('pt-BR')}`;
  }

  // Render inicial
  updateDisplay();
  renderTape();

  // Expõe a API global para o teclado físico
  window.CalculatorApp = {
    handleAction: handleAction
  };
})();
