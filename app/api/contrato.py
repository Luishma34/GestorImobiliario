from fastapi import APIRouter, status, HTTPException, Depends, Query
from fastapi.params import Depends
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select
from app.models import Contrato, ContratoCreate, ContratoPublic, Imovel, Inquilino, ContratoUpdate
from app.database import get_session

router = APIRouter(prefix="/contratos", tags=["Contratos"])


@router.post("/", response_model=ContratoPublic, status_code=status.HTTP_201_CREATED)
def criar_contrato(contrato: ContratoCreate, session: Session = Depends(get_session)):
    imovel = session.get(Imovel, contrato.id_imovel)
    if not imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")

    inquilino = session.get(Inquilino, contrato.id_inquilino)
    if not inquilino:
        raise HTTPException(status_code=404, detail="Inquilino não encontrado")

    if imovel.status == "Alugado":
        raise HTTPException(status_code=400, detail="Este imóvel já está alugado.")

    db_contrato = Contrato.model_validate(contrato)
    session.add(db_contrato)

    imovel.status = "Alugado"
    session.add(imovel)

    session.commit()
    session.refresh(db_contrato)
    return db_contrato


@router.get("/", response_model=list[ContratoPublic])
def listar_contratos(
        session: Session = Depends(get_session),
        pagina: int = Query(1, ge=1, description="Página atual"),
        registros_por_pagina: int = Query(10, ge=1, le=100, description="Itens por página")
):
    offset = (pagina - 1) * registros_por_pagina
    statement = (
        select(Contrato)
        .options(
            joinedload(Contrato.inquilino),
            joinedload(Contrato.imovel)
        )
        .offset(offset)
        .limit(registros_por_pagina)
    )

    contratos = session.exec(statement).all()
    return contratos


@router.get("/{contrato_id}", response_model=ContratoPublic)
def buscar_contrato(contrato_id: int, session: Session = Depends(get_session)):
    statement = (
        select(Contrato)
        .options(
            joinedload(Contrato.inquilino),
            joinedload(Contrato.imovel)
        )
        .where(Contrato.id == contrato_id)
    )
    contrato = session.exec(statement).first()

    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    return contrato

@router.put("/{contrato_id}", status_code=status.HTTP_204_NO_CONTENT)
def atualizar_contrato(contrato_id: int, dados: ContratoUpdate, session: Session = Depends(get_session)):
    """
    Atualiza um contrato.
    Se o status for alterado para 'Encerrado' ou 'Cancelado', o imóvel é liberado automaticamente.
    """
    db_contrato = session.get(Contrato, contrato_id)
    if not db_contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")

    dados_dict = dados.model_dump(exclude_unset=True)

    # Regra de Negócio: Se encerrar contrato, liberar imóvel
    novo_status = dados_dict.get("status")
    if novo_status and novo_status in ["Encerrado", "Cancelado"] and db_contrato.status == "Ativo":
        imovel = session.get(Imovel, db_contrato.id_imovel)
        if imovel:
            imovel.status = "Disponivel"
            session.add(imovel)

    db_contrato.sqlmodel_update(dados_dict)
    session.add(db_contrato)
    session.commit()
    return None


@router.delete("/{contrato_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_contrato(contrato_id: int, session: Session = Depends(get_session)):
    """
    Deleta um contrato.
    CUIDADO: Ao deletar um contrato ativo, o imóvel volta a ficar Disponível.
    """
    db_contrato = session.get(Contrato, contrato_id)
    if not db_contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")

    # Se deletar contrato ativo, libera o imóvel
    if db_contrato.status == "Ativo":
        imovel = session.get(Imovel, db_contrato.id_imovel)
        if imovel:
            imovel.status = "Disponivel"
            session.add(imovel)

    session.delete(db_contrato)
    session.commit()
    return None