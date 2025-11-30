from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func, extract
from app.database import get_session
from app.models import Contrato, Imovel, ContratoPublic

router = APIRouter(prefix="/relatorios", tags=["Relatórios e Consultas (Membro 3)"])

@router.get("/financeiro/receita-total", response_model=dict)
def receita_total_ativa(session: Session = Depends(get_session)):
    """
    Agregação Financeira: Soma o valor de todos os contratos com status 'Ativo'.
    """
    statement = select(func.sum(Contrato.valor_aluguel)).where(Contrato.status == "Ativo")
    receita = session.exec(statement).one() or 0.0
    
    return {
        "descricao": "Receita mensal total de contratos ativos",
        "valor_total": float(receita)
    }

@router.get("/contratos/vencimento", response_model=list[ContratoPublic])
def contratos_por_vencimento(
    ano: int = Query(..., description="Ano de vencimento (ex: 2025)"),
    mes: int = Query(..., ge=1, le=12, description="Mês de vencimento (1-12)"),
    session: Session = Depends(get_session)
):
    """
    Filtro por Data: Lista contratos que vencem em um mês/ano específico.
    """
    # Filtra onde o ano e o mês da data_fim correspondem aos parâmetros
    statement = (
        select(Contrato)
        .where(extract('year', Contrato.data_fim) == ano)
        .where(extract('month', Contrato.data_fim) == mes)
    )
    
    contratos = session.exec(statement).all()
    return contratos

@router.get("/imoveis/contagem-por-categoria", response_model=list[dict])
def contagem_imoveis_categoria(session: Session = Depends(get_session)):
    """
    Agregação: Conta quantos imóveis existem por categoria (Casa, Apartamento, etc).
    """
    statement = (
        select(Imovel.tipo_imovel, func.count(Imovel.id))
        .group_by(Imovel.tipo_imovel)
    )
    results = session.exec(statement).all()
    
    return [{"categoria": row[0], "quantidade": row[1]} for row in results]