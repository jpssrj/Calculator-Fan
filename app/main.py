"""Servidor FastAPI da Calculadora Fan."""

import os
from pathlib import Path
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.calculator import CalculateRequest, CalculateResponse
from app.engine.evaluator import evaluate_expression
from app.engine.exceptions import (
    DivisionByZeroError,
    SecuritySyntaxError,
    InvalidExpressionError,
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Calculadora Fan",
    description="Calculadora Web Neubrutalista de Alta Precisão (Python + FastAPI)",
    version="1.0.0",
)

# Configuração de CORS para permitir desenvolvimento flexível
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Garantir existência do diretório estático
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", tags=["Interface"])
async def serve_index():
    """Entrega a página inicial HTML5 da calculadora."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return JSONResponse(
        content={
            "app": "Calculadora Fan",
            "message": "Servidor backend ativo. Arquivos estáticos em carregamento.",
        }
    )


@app.get("/api/health", tags=["Monitoramento"])
async def health_check():
    """Endpoint de checagem de saúde e disponibilidade do serviço."""
    return {"status": "ok", "service": "Calculadora Fan API"}


@app.post(
    "/api/calculate",
    response_model=CalculateResponse,
    tags=["Operações Matemáticas"],
    summary="Avalia e computa expressão aritmética",
)
async def calculate(payload: CalculateRequest):
    """Executa a validação e avaliação aritmética determinística no backend."""
    raw_expr = payload.expression.strip()

    try:
        result_str = evaluate_expression(raw_expr)
        return CalculateResponse(
            status="success",
            result=result_str,
            expression=raw_expr,
            error=None,
        )
    except DivisionByZeroError:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=CalculateResponse(
                status="error",
                result=None,
                expression=raw_expr,
                error="ERRO: DIVISÃO POR ZERO",
            ).model_dump(),
        )
    except SecuritySyntaxError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=CalculateResponse(
                status="error",
                result=None,
                expression=raw_expr,
                error="SINTAXE INVÁLIDA OU NÃO PERMITIDA",
            ).model_dump(),
        )
    except InvalidExpressionError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=CalculateResponse(
                status="error",
                result=None,
                expression=raw_expr,
                error=str(e).upper(),
            ).model_dump(),
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=CalculateResponse(
                status="error",
                result=None,
                expression=raw_expr,
                error="ERRO INTERNO DE PROCESSAMENTO",
            ).model_dump(),
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
