from http.client import HTTPException

from fastapi import APIRouter, status, Depends, Query
from sqlmodel import Session, select
from app.models import Inquilino, InquilinoCreate, InquilinoPublic, InquilinoUpdate
from app.database import get_session

router = APIRouter(prefix="/inquilinos", tags=["Inquilinos"])


@router.post("/", response_model=InquilinoPublic, status_code=status.HTTP_201_CREATED)
def criar_inquilino(inquilino: InquilinoCreate, session: Session = Depends(get_session)):
    db_inquilino = Inquilino.model_validate(inquilino)
    session.add(db_inquilino)
    session.commit()
    session.refresh(db_inquilino)
    return db_inquilino


@router.get("/", response_model=list[InquilinoPublic])
def listar_inquilinos(
        session: Session = Depends(get_session),
        pagina: int = Query(1, ge=1, description="Página atual"),
        registros_por_pagina: int = Query(10, ge=1, le=100, description="Itens por página")
):
    offset = (pagina - 1) * registros_por_pagina
    statement = select(Inquilino).offset(offset).limit(registros_por_pagina)

    inquilinos = session.exec(statement).all()
    return inquilinos


@router.get("/{inquilino_id}", response_model=InquilinoPublic)
def buscar_inquilino(inquilino_id: int, session: Session = Depends(get_session)):
    """Busca um inquilino pelo ID."""
    inquilino = session.get(Inquilino, inquilino_id)
    if not inquilino:
        raise HTTPException(status_code=404, detail="Inquilino não encontrado")
    return inquilino


@router.put("/{inquilino_id}", status_code=status.HTTP_204_NO_CONTENT)
def atualizar_inquilino(inquilino_id: int, dados: InquilinoUpdate, session: Session = Depends(get_session)):
    """Atualiza dados de um inquilino."""
    db_inquilino = session.get(Inquilino, inquilino_id)
    if not db_inquilino:
        raise HTTPException(status_code=404, detail="Inquilino não encontrado")

    inquilino_data = dados.model_dump(exclude_unset=True)
    db_inquilino.sqlmodel_update(inquilino_data)

    session.add(db_inquilino)
    session.commit()
    return None


@router.delete("/{inquilino_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_inquilino(inquilino_id: int, session: Session = Depends(get_session)):
    """Remove um inquilino do sistema."""
    db_inquilino = session.get(Inquilino, inquilino_id)
    if not db_inquilino:
        raise HTTPException(status_code=404, detail="Inquilino não encontrado")

    session.delete(db_inquilino)
    session.commit()
    return None

