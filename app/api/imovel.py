from typing import List
from fastapi import APIRouter, HTTPException, Query
from app.models import Imovel, ImovelCreate, ImovelUpdate
from app.database import DeltaDatabase

router = APIRouter(prefix="/imoveis", tags=["Imóveis"])

# Instância do banco de dados
db = DeltaDatabase(table_name="imoveis")


@router.post("/", response_model=Imovel, status_code=201)
def criar_imovel(imovel: ImovelCreate):
    pass


@router.get("/", response_model=List[Imovel])
def listar_imoveis(
    pagina: int = Query(1, ge=1),
    registrosPorPagina: int = Query(10, ge=1)
):
    """
    TODO: Implementar listagem com paginação
    """
    pass


@router.get("/{imovel_id}", response_model=Imovel)
def buscar_imovel(imovel_id: int):
    pass


@router.put("/{imovel_id}", response_model=Imovel)
def atualizar_imovel(imovel_id: int, imovel: ImovelUpdate):
    pass


@router.delete("/{imovel_id}", status_code=204)
def deletar_imovel(imovel_id: int):
    pass
