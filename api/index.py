"""Ponto de entrada serverless para deploy na Vercel."""

import sys
from pathlib import Path

# Garante que o diretório raiz do projeto esteja acessível no PYTHONPATH da Serverless Function
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.main import app

# Exporta a instância ASGI para o runtime da Vercel
__all__ = ["app"]
