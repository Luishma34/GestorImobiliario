from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import imovel, inquilino, contrato, proprietario, relatorios

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação."""
    yield

app = FastAPI(
    title="Gestor Imobiliário API",
    description="API REST para gerenciamento de imóveis",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(imovel.router)
app.include_router(inquilino.router)
app.include_router(contrato.router)
app.include_router(proprietario.router)
# Adicionado router do Membro 3
app.include_router(relatorios.router)

@app.get("/")
def root():
    return {
        "message": "Gestor Imobiliário API está rodando!",
        "docs": "/docs"
    }