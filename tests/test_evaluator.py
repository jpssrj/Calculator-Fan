"""Testes unitários para o motor de avaliação segura com AST e decimal.Decimal."""

import pytest
from app.engine.evaluator import evaluate_expression
from app.engine.exceptions import (
    DivisionByZeroError,
    SecuritySyntaxError,
    InvalidExpressionError,
)


def test_basic_arithmetic():
    assert evaluate_expression("2 + 3") == "5"
    assert evaluate_expression("10 - 4") == "6"
    assert evaluate_expression("6 * 7") == "42"
    assert evaluate_expression("15 / 3") == "5"


def test_decimal_precision_exact():
    # 0.1 + 0.2 no JS e float padrão resulta em 0.30000000000000004
    assert evaluate_expression("0.1 + 0.2") == "0.3"
    assert evaluate_expression("0.7 + 0.1") == "0.8"
    assert evaluate_expression("1.05 * 2") == "2.1"
    assert evaluate_expression("0.3 - 0.2") == "0.1"


def test_operator_precedence_and_parentheses():
    assert evaluate_expression("2 + 3 * 4") == "14"
    assert evaluate_expression("(2 + 3) * 4") == "20"
    assert evaluate_expression("10 + 20 / (2 + 3)") == "14"
    assert evaluate_expression("2 * (3 + (4 * 2))") == "22"


def test_unicode_glyphs_and_commas():
    assert evaluate_expression("5 × 4") == "20"
    assert evaluate_expression("20 ÷ 4") == "5"
    assert evaluate_expression("2,5 + 3,5") == "6"
    assert evaluate_expression("1,25 * 4") == "5"


def test_unary_operations():
    assert evaluate_expression("-5 + 10") == "5"
    assert evaluate_expression("-(3 + 2)") == "-5"
    assert evaluate_expression("+10 - -5") == "15"


def test_power_and_modulo():
    assert evaluate_expression("2 ^ 3") == "8"
    assert evaluate_expression("3 ** 3") == "27"
    assert evaluate_expression("10 % 3") == "1"


def test_division_by_zero():
    with pytest.raises(DivisionByZeroError):
        evaluate_expression("10 / 0")

    with pytest.raises(DivisionByZeroError):
        evaluate_expression("5 / (2 - 2)")

    with pytest.raises(DivisionByZeroError):
        evaluate_expression("10 % 0")


def test_security_rejections():
    # Chamadas de função arbitrárias
    with pytest.raises((SecuritySyntaxError, InvalidExpressionError)):
        evaluate_expression("__import__('os').system('dir')")

    with pytest.raises((SecuritySyntaxError, InvalidExpressionError)):
        evaluate_expression("open('file.txt').read()")

    # Atributos e variáveis
    with pytest.raises((SecuritySyntaxError, InvalidExpressionError)):
        evaluate_expression("x + y")

    # Expressões com caracteres ilegais
    with pytest.raises(SecuritySyntaxError):
        evaluate_expression("2 + 3; print('hack')")

    with pytest.raises(SecuritySyntaxError):
        evaluate_expression("[1, 2, 3]")


def test_invalid_syntax():
    with pytest.raises(InvalidExpressionError):
        evaluate_expression("")

    with pytest.raises(InvalidExpressionError):
        evaluate_expression("   ")

    with pytest.raises(InvalidExpressionError):
        evaluate_expression("5 + +")

    with pytest.raises(InvalidExpressionError):
        evaluate_expression("(2 + 3")
