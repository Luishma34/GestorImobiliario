#from http.client import HTTPException
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
    pagina: int = Query(1, ge=1),
    registrosPorPagina: int = Query(10, ge=1)
):
    """
    TODO: Implementar listagem com paginação
    """
    pass

@router.get("/total", response_model=dict)
def total_cadastrados():
    total = db.count()
    return {"total": total}

@router.post("/vacuum", status_code=status.HTTP_200_OK, response_model=dict)
def vacuum_imoveis():
    try:
        files_deleted = db.vacuum()
        
        return {
            "message": f"Operação de vacuum concluída. {len(files_deleted)} arquivos foram removidos.",
            "files": files_deleted
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro ao executar o vacuum: {e}"
        )

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

@router.put("/{imovel_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
def atualizar_imovel(imovel_id: int, imovel: ImovelUpdate):
    imovel_existente = db.get(imovel_id)
    if not imovel_existente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Imóvel com ID {imovel_id} não encontrado."
        ) 
    
    imovel_data = imovel.model_dump(exclude_unset=True)
    try:
        success = db.update(imovel_id, imovel_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Imóvel com ID {imovel_id} não encontrado para atualização."
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro interno ao atualizar o imóvel: {e}"
        )    
    return None

@router.delete("/{imovel_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_imovel(imovel_id: int):   
    imovel_existente = db.get(imovel_id)
    if not imovel_existente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Imóvel com ID {imovel_id} não encontrado."
        ) 
    try:
        success = db.delete(imovel_id)
        
        if not success:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Imóvel com ID {imovel_id} não encontrado para deleção."
        )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro interno ao deletar o imóvel: {e}"
        )    
    return None

