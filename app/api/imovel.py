
from typing import List
from fastapi import APIRouter, status, Query, HTTPException
from app.models import Imovel, ImovelCreate, ImovelUpdate
from app.database import DeltaDatabase

router = APIRouter(prefix="/imoveis", tags=["Imóveis"])

# Instância do banco de dados
db = DeltaDatabase(table_name="imoveis")

@router.post("/", response_model=Imovel, status_code=status.HTTP_201_CREATED)
def criar_imovel(imovel: ImovelCreate):
    """Cria um novo imóvel no banco de dados."""
    imovel_data = imovel.model_dump()
    novo_id = db.insert(imovel_data)
    return Imovel(id=novo_id, **imovel_data)


@router.get("/", response_model=List[Imovel])
def listar_imoveis(
    pagina: int = Query(1, ge=1, description="Número da página"),
    registrosPorPagina: int = Query(10, ge=1, description="Quantidade de registros por página")
):
    """
    IMPLEMENTAÇÃO: Lista todos os imóveis com paginação.
    """
    offset = (pagina - 1) * registrosPorPagina
    imoveis = db.list(offset=offset, limit=registrosPorPagina)
    return imoveis


@router.get("/{imovel_id}", response_model=Imovel)
def buscar_imovel(imovel_id: int):
    """Busca um imóvel pelo seu ID."""
    imovel_data = db.get(imovel_id)
    if not imovel_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Imóvel com ID {imovel_id} não encontrado"
        )
    return Imovel(**imovel_data)

@router.put("/{imovel_id}", response_model=Imovel)
def atualizar_imovel(imovel_id: int, imovel: ImovelUpdate):
    pass


@router.delete("/{imovel_id}", status_code=204)
def deletar_imovel(imovel_id: int):
    pass
