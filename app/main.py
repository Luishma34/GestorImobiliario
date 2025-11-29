from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api import imovel


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação."""
    yield


app = FastAPI(
    title="Gestor Imobiliário API",
    description="API REST para gerenciamento de imóveis usando FastAPI e SQLModel",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(imovel.router)


@app.get("/")
def root():
    """Endpoint raiz da API"""
    return {
        "message": "Gestor Imobiliário API",
        "docs": "/docs"
    }