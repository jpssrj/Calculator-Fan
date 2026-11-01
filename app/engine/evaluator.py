"""Motor de avaliação aritmética segura utilizando AST e decimal.Decimal."""

import ast
from decimal import Decimal, getcontext, DivisionByZero, InvalidOperation, Overflow
import re
from typing import Union

from app.engine.exceptions import (
    DivisionByZeroError,
    SecuritySyntaxError,
    InvalidExpressionError,
)

# Precisão de 34 dígitos decimais (padrão IEEE 754 decimal128)
getcontext().prec = 34


def format_decimal(value: Decimal) -> str:
    """Formata um Decimal para string de forma amigável e sem perda de precisão."""
    # Normaliza zeros excedentes
    normalized = value.normalize()
    sign, digits, exponent = normalized.as_tuple()
    
    if exponent == 0:
        return str(int(normalized))
    
    # Se o expoente estiver em faixa padrão, formata como ponto fixo
    if -14 <= exponent <= 14:
        s = f"{normalized:f}"
        if "." in s:
            s = s.rstrip("0").rstrip(".")
        return s
    
    # Caso contrário, utiliza representação científica padrão
    return str(normalized)


class SafeASTEvaluator(ast.NodeVisitor):
    """Visitor seguro da Árvore de Sintaxe Abstrata (AST) para operações matemáticas."""

    ALLOWED_BINARY_OPS = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: SafeASTEvaluator._safe_div(a, b),
        ast.Pow: lambda a, b: SafeASTEvaluator._safe_pow(a, b),
        ast.Mod: lambda a, b: SafeASTEvaluator._safe_mod(a, b),
    }

    ALLOWED_UNARY_OPS = {
        ast.UAdd: lambda a: +a,
        ast.USub: lambda a: -a,
    }

    @staticmethod
    def _safe_div(a: Decimal, b: Decimal) -> Decimal:
        if b == Decimal(0):
            raise DivisionByZeroError("Divisão por zero não é permitida.")
        try:
            return a / b
        except (DivisionByZero, ZeroDivisionError):
            raise DivisionByZeroError("Divisão por zero não é permitida.")

    @staticmethod
    def _safe_pow(a: Decimal, b: Decimal) -> Decimal:
        # Prevenção contra estouro de memória e DoS com potências absurdas
        if abs(b) > Decimal(1000):
            raise InvalidExpressionError("Expoente excede o limite seguro permitido (máximo 1000).")
        try:
            return a ** b
        except (Overflow, InvalidOperation):
            raise InvalidExpressionError("Resultado da potência excede a capacidade de cálculo.")

    @staticmethod
    def _safe_mod(a: Decimal, b: Decimal) -> Decimal:
        if b == Decimal(0):
            raise DivisionByZeroError("Operação de módulo por zero não é permitida.")
        return a % b

    def visit(self, node: ast.AST) -> Decimal:
        """Visita um nó específico da AST com verificação estrita de segurança."""
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ast.AST):
        """Bloqueia categoricamente qualquer nó não explicitamente permitido."""
        raise SecuritySyntaxError(
            f"Elemento de sintaxe não permitido: '{node.__class__.__name__}'."
        )

    def visit_Expression(self, node: ast.Expression) -> Decimal:
        return self.visit(node.body)

    def visit_Constant(self, node: ast.Constant) -> Decimal:
        # Permite somente literais numéricos (int ou float convertidos via string direta)
        if isinstance(node.value, (int, float)):
            try:
                return Decimal(str(node.value))
            except InvalidOperation:
                raise InvalidExpressionError(f"Valor numérico inválido: '{node.value}'")
        raise SecuritySyntaxError(
            f"Tipo de constante não numérica não permitida: '{type(node.value).__name__}'."
        )

    def visit_BinOp(self, node: ast.BinOp) -> Decimal:
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_type = type(node.op)

        if op_type not in self.ALLOWED_BINARY_OPS:
            raise SecuritySyntaxError(f"Operador binário não permitido: '{op_type.__name__}'.")

        handler = self.ALLOWED_BINARY_OPS[op_type]
        try:
            return handler(left, right)
        except (DivisionByZeroError, InvalidExpressionError):
            raise
        except Exception as e:
            raise InvalidExpressionError(f"Erro ao processar operação: {str(e)}")

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Decimal:
        operand = self.visit(node.operand)
        op_type = type(node.op)

        if op_type not in self.ALLOWED_UNARY_OPS:
            raise SecuritySyntaxError(f"Operador unário não permitido: '{op_type.__name__}'.")

        handler = self.ALLOWED_UNARY_OPS[op_type]
        return handler(operand)


def sanitize_and_prepare_expression(expression: str) -> str:
    """Higieniza e normaliza símbolos matemáticos usuais antes da análise sintática."""
    if not expression or not expression.strip():
        raise InvalidExpressionError("A expressão matemática não pode ser vazia.")

    expr = expression.strip()

    if len(expr) > 200:
        raise InvalidExpressionError("A expressão excede o tamanho máximo permitido de 200 caracteres.")

    # Mapeamento de glifos visuais para operadores Python
    expr = expr.replace("×", "*").replace("÷", "/")
    expr = expr.replace(",", ".")
    # Mapear potência visual ^ para **
    expr = expr.replace("^", "**")

    # Rejeição de caracteres expressamente proibidos antes do parsing
    if any(char in expr for char in [";", ":", "[", "]", "{", "}", "'", '"', "\\"]):
        raise SecuritySyntaxError("Caracteres especiais não autorizados detectados na expressão.")

    return expr


def evaluate_expression(expression: str) -> str:
    """Valida e computa a expressão matemática de forma determinística."""
    sanitized = sanitize_and_prepare_expression(expression)

    try:
        parsed_tree = ast.parse(sanitized, mode="eval")
    except SyntaxError:
        raise InvalidExpressionError("Sintaxe matemática inválida ou incompleta.")

    evaluator = SafeASTEvaluator()
    result_decimal = evaluator.visit(parsed_tree)

    return format_decimal(result_decimal)
