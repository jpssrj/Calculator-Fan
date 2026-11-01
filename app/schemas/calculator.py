"""Esquemas de dados Pydantic para requisições e respostas da calculadora."""

from typing import Optional
from pydantic import BaseModel, Field


class CalculateRequest(BaseModel):
    """Payload de entrada para o endpoint de cálculo."""
    expression: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Expressão matemática a ser avaliada.",
        examples=["12.5 * (4 + 6) / 2"]
    )


class CalculateResponse(BaseModel):
    """Payload de resposta com resultado serializado em string."""
    status: str = Field(
        ...,
        description="Estado da resposta: 'success' ou 'error'.",
        examples=["success"]
    )
    result: Optional[str] = Field(
        None,
        description="Resultado numérico em formato textual para preservar precisão.",
        examples=["62.5"]
    )
    expression: str = Field(
        ...,
        description="Expressão matemática original.",
        examples=["12.5 * (4 + 6) / 2"]
    )
    error: Optional[str] = Field(
        None,
        description="Mensagem de erro explicativa caso ocorra falha.",
        examples=[None]
    )
