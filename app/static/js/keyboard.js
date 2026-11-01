/**
 * CALCULATOR FAN - MÓDULO DE TECLADO FÍSICO
 * Mapeamento e ergonomia de atalhos de hardware com feedback visual sincronizado.
 */

(function () {
  'use strict';

  // Mapa de normalização de teclas físicas para as ações da calculadora
  const KEY_MAP = {
    '0': { action: 'insert', value: '0' },
    '1': { action: 'insert', value: '1' },
    '2': { action: 'insert', value: '2' },
    '3': { action: 'insert', value: '3' },
    '4': { action: 'insert', value: '4' },
    '5': { action: 'insert', value: '5' },
    '6': { action: 'insert', value: '6' },
    '7': { action: 'insert', value: '7' },
    '8': { action: 'insert', value: '8' },
    '9': { action: 'insert', value: '9' },
    '.': { action: 'decimal' },
    ',': { action: 'decimal' },
    '+': { action: 'insert', value: '+' },
    '-': { action: 'insert', value: '-' },
    '*': { action: 'insert', value: '×' },
    '/': { action: 'insert', value: '÷' },
    '%': { action: 'insert', value: '%' },
    '^': { action: 'insert', value: '^' },
    '(': { action: 'insert', value: '(' },
    ')': { action: 'insert', value: ')' },
    'Enter': { action: 'calculate' },
    '=': { action: 'calculate' },
    'Backspace': { action: 'backspace' },
    'Delete': { action: 'backspace' },
    'Escape': { action: 'clear-all' },
    'c': { action: 'clear-all' },
    'C': { action: 'clear-all' },
    'h': { action: 'toggle-history' },
    'H': { action: 'toggle-history' }
  };

  /**
   * Aciona visualmente a animação de pressionamento no botão da tela.
   */
  function triggerButtonFeedback(keyConfig) {
    let selector = '';

    if (keyConfig.action === 'insert' && keyConfig.value) {
      selector = `.key[data-value="${keyConfig.value}"]`;
    } else if (keyConfig.action === 'calculate') {
      selector = '.key[data-action="calculate"]';
    } else if (keyConfig.action === 'clear-all') {
      selector = '.key[data-action="clear-all"]';
    } else if (keyConfig.action === 'backspace') {
      selector = '.key[data-action="backspace"]';
    } else if (keyConfig.action === 'decimal') {
      selector = '.key[data-action="decimal"]';
    } else if (keyConfig.action === 'toggle-history') {
      selector = '#btn-toggle-history';
    }

    if (selector) {
      const btn = document.querySelector(selector);
      if (btn) {
        btn.classList.add('is-pressed');
        setTimeout(() => {
          btn.classList.remove('is-pressed');
        }, 120);
      }
    }
  }

  /**
   * Listener global de eventos de teclado.
   */
  window.addEventListener('keydown', function (e) {
    // Se o usuário estiver interagindo com um input de texto padrão, não interceptar
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
      return;
    }

    const key = e.key;
    const mapping = KEY_MAP[key];

    if (!mapping) return;

    // Prevenção cirúrgica de atalhos nativos do navegador
    if (['/', 'Enter', 'Backspace', ' '].includes(key) || (key === 'h' && !e.ctrlKey && !e.metaKey)) {
      e.preventDefault();
    }

    // Feedback visual mecânico na interface
    triggerButtonFeedback(mapping);

    // Disparo para o orquestrador de estado global
    if (window.CalculatorApp && typeof window.CalculatorApp.handleAction === 'function') {
      window.CalculatorApp.handleAction(mapping.action, mapping.value);
    }
  });
})();
