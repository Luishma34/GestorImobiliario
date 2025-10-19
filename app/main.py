from fastapi import FastAPI
from app.api import imovel
from app.api import hash

app = FastAPI(
    title="Gestor Imobiliário API",
    description="API REST para gerenciamento de imóveis usando Delta Lake",
    version="0.1.0"
)

app.include_router(imovel.router)
app.include_router(hash.router)


@app.get("/")
def root():
    """Endpoint raiz da API"""
    return {
        "message": "Gestor Imobiliário API",
        "docs": "/docs"
    }