"""Exceções do domínio de cálculo da Calculadora Fan."""

class CalculatorError(Exception):
    """Exceção base para erros na calculadora."""
    pass


class DivisionByZeroError(CalculatorError):
    """Lançada quando ocorre uma tentativa explícita ou implícita de divisão por zero."""
    pass


class SecuritySyntaxError(CalculatorError):
    """Lançada quando a expressão contém nós, chamadas ou sintaxes não permitidas."""
    pass


class InvalidExpressionError(CalculatorError):
    """Lançada quando a expressão matemática é sintaticamente malformada ou incompleta."""
    pass
