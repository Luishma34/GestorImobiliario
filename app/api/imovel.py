from typing import List
from fastapi import APIRouter, status, Query, HTTPException, Depends
from sqlmodel import Session, select, func

from app.models import Imovel, ImovelCreate, ImovelUpdate, ImovelPublic
from app.database import get_session

router = APIRouter(prefix="/imoveis", tags=["Imóveis"])


@router.post("/", response_model=ImovelPublic, status_code=status.HTTP_201_CREATED)
def criar_imovel(imovel: ImovelCreate, session: Session = Depends(get_session)):
    """Cria um novo imóvel no banco de dados."""
    db_imovel = Imovel.model_validate(imovel)
    session.add(db_imovel)
    session.commit()
    session.refresh(db_imovel)
    return db_imovel


@router.get("/", response_model=List[ImovelPublic])
def listar_imoveis(
    pagina: int = Query(1, ge=1, description="Número da página"),
    registrosPorPagina: int = Query(10, ge=1, le=100, description="Quantidade de registros por página"),
    session: Session = Depends(get_session)
):
    """
    Retorna uma página de imóveis cadastrados.
    """
    offset = (pagina - 1) * registrosPorPagina
    statement = select(Imovel).offset(offset).limit(registrosPorPagina)
    imoveis = session.exec(statement).all()
    return imoveis


@router.get("/total", response_model=dict)
def total_cadastrados(session: Session = Depends(get_session)):
    """Mostra a quantidade de entidades existentes."""
    statement = select(func.count()).select_from(Imovel)
    total = session.exec(statement).one()
    return {"total": total}


@router.get("/{imovel_id}", response_model=ImovelPublic)
def buscar_imovel(imovel_id: int, session: Session = Depends(get_session)):
    """Busca um imóvel pelo seu ID."""
    imovel = session.get(Imovel, imovel_id)
    if not imovel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Imóvel com ID {imovel_id} não encontrado"
        )
    return imovel


@router.put("/{imovel_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
def atualizar_imovel(
    imovel_id: int,
    imovel: ImovelUpdate,
    session: Session = Depends(get_session)
):
    """Atualiza um imóvel existente."""
    db_imovel = session.get(Imovel, imovel_id)
    if not db_imovel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Imóvel com ID {imovel_id} não encontrado."
        )
    
    imovel_data = imovel.model_dump(exclude_unset=True)
    db_imovel.sqlmodel_update(imovel_data)
    session.add(db_imovel)
    session.commit()
    return None


@router.delete("/{imovel_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_imovel(imovel_id: int, session: Session = Depends(get_session)):
    """Deleta um imóvel existente."""
    db_imovel = session.get(Imovel, imovel_id)
    if not db_imovel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Imóvel com ID {imovel_id} não encontrado."
        )
    
    session.delete(db_imovel)
    session.commit()
    return None