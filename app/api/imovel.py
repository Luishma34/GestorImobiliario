from fastapi import APIRouter, status, Query, HTTPException, Depends
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select, func
from app.models import Imovel, ImovelCreate, ImovelUpdate, ImovelPublic
from app.database import get_session
from enum import Enum

router = APIRouter(prefix="/imoveis", tags=["Imóveis"])

class OrdemImovel(str, Enum):
    padrao = "id"
    valor_crescente = "valor_menor"
    valor_decrescente = "valor_maior"
    bairro = "endereco"

@router.post("/", response_model=ImovelPublic, status_code=status.HTTP_201_CREATED)
def criar_imovel(imovel: ImovelCreate, session: Session = Depends(get_session)):
    """Cria um novo imóvel no banco de dados."""
    db_imovel = Imovel.model_validate(imovel)
    session.add(db_imovel)
    session.commit()
    session.refresh(db_imovel)
    return db_imovel


@router.get("/", response_model=list[ImovelPublic])
def listar_imoveis(
        session: Session = Depends(get_session),
        pagina: int = Query(1, ge=1),
        registros_por_pagina: int = Query(10, ge=1, le=100),
        bairro: str | None = Query(None, description="Filtrar por parte do endereço"),
        status_imovel: str | None = Query(None, description="Filtrar por status"),
        id_proprietario: int | None = Query(None, description="Filtrar por proprietário"),
        ordenar_por: OrdemImovel = Query(OrdemImovel.padrao, description="Critério de ordenação")
):
    """
    Lista imóveis com filtros e ordenação (Membro 3).
    """
    offset = (pagina - 1) * registros_por_pagina

    # Eager loading
    statement = select(Imovel).options(joinedload(Imovel.proprietario))

    # Filtros Dinâmicos
    if bairro:
        statement = statement.where(func.lower(Imovel.endereco).contains(bairro.lower()))

    if status_imovel:
        statement = statement.where(Imovel.status == status_imovel)

    if id_proprietario:
        statement = statement.where(Imovel.id_proprietario == id_proprietario)

    # Ordenação (Membro 3)
    if ordering_criterio := ordenar_por:
        if ordering_criterio == OrdemImovel.valor_crescente:
            statement = statement.order_by(Imovel.valor_aluguel_base.asc())
        elif ordering_criterio == OrdemImovel.valor_decrescente:
            statement = statement.order_by(Imovel.valor_aluguel_base.desc())
        elif ordering_criterio == OrdemImovel.bairro:
            statement = statement.order_by(Imovel.endereco.asc())
        else:
            statement = statement.order_by(Imovel.id.asc())

    statement = statement.offset(offset).limit(registros_por_pagina)
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
    """Busca um imóvel e seus relacionamentos de uma vez."""
    statement = select(Imovel).options(joinedload(Imovel.proprietario)).where(Imovel.id == imovel_id)
    imovel = session.exec(statement).first()

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