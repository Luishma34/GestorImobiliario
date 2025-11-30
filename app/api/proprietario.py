from typing import List
from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from app.database import get_session
from app.models.proprietario import Proprietario, ProprietarioCreate, ProprietarioPublic

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