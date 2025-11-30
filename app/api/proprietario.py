from typing import List
from fastapi import APIRouter, status, Depends, Query, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from app.database import get_session
from app.models.proprietario import Proprietario, ProprietarioCreate, ProprietarioUpdate, ProprietarioPublic

router = APIRouter(prefix="/proprietarios", tags=["Proprietários"])


@router.post("/", response_model=ProprietarioPublic, status_code=status.HTTP_201_CREATED)
def criar_proprietario(proprietario: ProprietarioCreate, session: Session = Depends(get_session)):
    db_proprietario = Proprietario.model_validate(proprietario)
    session.add(db_proprietario)
    session.commit()
    session.refresh(db_proprietario)
    return db_proprietario


@router.get("/", response_model=List[ProprietarioPublic])
def listar_proprietarios(
    session: Session = Depends(get_session),
    pagina: int = Query(1, ge=1, description="Página atual"),
    registros_por_pagina: int = Query(10, ge=1, le=100, description="Itens por página")
):
    offset = (pagina - 1) * registros_por_pagina
    statement = (
        select(Proprietario)
        .options(selectinload(Proprietario.imoveis))
        .offset(offset)
        .limit(registros_por_pagina)
    )
    return session.exec(statement).all()


@router.get("/{proprietario_id}", response_model=ProprietarioPublic)
def buscar_proprietario(proprietario_id: int, session: Session = Depends(get_session)):
    """Busca um proprietário pelo ID."""
    proprietario = session.get(Proprietario, proprietario_id)
    if not proprietario:
        raise HTTPException(status_code=404, detail="Proprietário não encontrado")
    return proprietario


@router.put("/{proprietario_id}", response_model=ProprietarioPublic)
def atualizar_proprietario(
    proprietario_id: int, 
    dados: ProprietarioUpdate, 
    session: Session = Depends(get_session)
):
    """Atualiza os dados de um proprietário."""
    db_proprietario = session.get(Proprietario, proprietario_id)
    if not db_proprietario:
        raise HTTPException(status_code=404, detail="Proprietário não encontrado")
    
    dados_dict = dados.model_dump(exclude_unset=True)
    db_proprietario.sqlmodel_update(dados_dict)
    
    session.add(db_proprietario)
    session.commit()
    session.refresh(db_proprietario)
    return db_proprietario


@router.delete("/{proprietario_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_proprietario(proprietario_id: int, session: Session = Depends(get_session)):
    """Remove um proprietário do sistema."""
    db_proprietario = session.get(Proprietario, proprietario_id)
    if not db_proprietario:
        raise HTTPException(status_code=404, detail="Proprietário não encontrado")
    
    session.delete(db_proprietario)
    session.commit()
    return None