from http.client import HTTPException
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func, extract
from app.database import get_session
from app.models import Contrato, Imovel, ContratoPublic, Proprietario

router = APIRouter(prefix="/relatorios", tags=["Relatórios e Consultas"])

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

#relatorios novos
@router.get("/financeiro/receita-total/{proprietario_id}", response_model=dict)
def receita_total_por_proprietario(
        proprietario_id: int,
        session: Session = Depends(get_session)
):
    """
    Proprietário: Soma o valor dos contratos ativos vinculados aos imóveis deste proprietário.
    """
    # Verifica se proprietário existe (opcional, mas boa prática)
    prop = session.get(Proprietario, proprietario_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Proprietário não encontrado")

    # Join: Contrato -> Imovel (onde imovel.id_proprietario == X)
    statement = (
        select(func.sum(Contrato.valor_aluguel))
        .join(Imovel)
        .where(Contrato.status == "Ativo")
        .where(Imovel.id_proprietario == proprietario_id)
    )

    receita = session.exec(statement).one() or 0.0

    return {
        "id_proprietario": proprietario_id,
        "nome_proprietario": prop.nome,
        "descricao": "Receita mensal de contratos ativos deste proprietário",
        "valor_total": float(receita)
    }


@router.get("/contratos/vencimento/{proprietario_id}", response_model=list[ContratoPublic])
def contratos_vencimento_por_proprietario(
        proprietario_id: int,
        ano: int = Query(..., description="Ano de vencimento"),
        mes: int = Query(..., ge=1, le=12, description="Mês de vencimento"),
        session: Session = Depends(get_session)
):
    """
    Proprietário: Lista contratos deste dono que vencem na data especificada.
    """
    # Join: Selecionar Contratos, juntar com Imovel, filtrar pelo dono do imóvel
    statement = (
        select(Contrato)
        .join(Imovel)
        .where(Imovel.id_proprietario == proprietario_id)
        .where(extract('year', Contrato.data_fim) == ano)
        .where(extract('month', Contrato.data_fim) == mes)
    )

    return session.exec(statement).all()


@router.get("/imoveis/contagem-por-categoria/{proprietario_id}", response_model=list[dict])
def contagem_categoria_por_proprietario(
        proprietario_id: int,
        session: Session = Depends(get_session)
):
    """
    Proprietário: Conta imóveis por categoria pertencentes a este dono específico.
    """
    statement = (
        select(Imovel.tipo_imovel, func.count(Imovel.id))
        .where(Imovel.id_proprietario == proprietario_id)
        .group_by(Imovel.tipo_imovel)
    )

    results = session.exec(statement).all()

    # Se não houver imóveis, retorna lista vazia
    return [{"categoria": row[0], "quantidade": row[1]} for row in results]

@router.get("/proprietario/{proprietario_id}/dashboardCompleto", response_model=dict)
def dashboard_proprietario(proprietario_id: int, session: Session = Depends(get_session)):
    """
    Relatório Detalhado por Proprietário:
    - Mostra o patrimônio (total de imóveis).
    - Calcula a receita mensal estimada apenas dos imóveis DESTE proprietário.
    - Lista os imóveis vinculados e seus status.
    """
    # 1. Validar se o proprietário existe
    proprietario = session.get(Proprietario, proprietario_id)
    if not proprietario:
        raise HTTPException(status_code=404, detail="Proprietário não encontrado")

    # 2. Buscar Imóveis do Proprietário
    statement_imoveis = select(Imovel).where(Imovel.id_proprietario == proprietario_id)
    imoveis = session.exec(statement_imoveis).all()

    if not imoveis:
        return {
            "proprietario": proprietario.nome,
            "mensagem": "Este proprietário não possui imóveis cadastrados."
        }

    # 3. Calcular métricas (Python puro para simplificar, já que temos a lista)
    total_imoveis = len(imoveis)
    imoveis_alugados = len([i for i in imoveis if i.status == "Alugado"])
    taxa_ocupacao = (imoveis_alugados / total_imoveis) * 100 if total_imoveis > 0 else 0

    # 4. Calcular Receita Financeira (JOIN entre Imovel e Contrato)
    # Busca contratos ativos SOMENTE dos imóveis deste proprietário
    statement_receita = (
        select(func.sum(Contrato.valor_aluguel))
        .join(Imovel)
        .where(Imovel.id_proprietario == proprietario_id)
        .where(Contrato.status == "Ativo")
    )
    receita_mensal = session.exec(statement_receita).one() or 0.0

    # 5. Montar resposta rica
    return {
        "resumo_executivo": {
            "proprietario": proprietario.nome,
            "email": proprietario.email,
            "total_imoveis": total_imoveis,
            "imoveis_alugados": imoveis_alugados,
            "imoveis_vagos": total_imoveis - imoveis_alugados,
            "taxa_ocupacao": f"{taxa_ocupacao:.1f}%",
            "receita_mensal_atual": float(receita_mensal)
        },
        "detalhamento_imoveis": [
            {
                "id": i.id,
                "apelido": i.apelido_imovel,
                "categoria": i.tipo_imovel,
                "status": i.status,
                "valor_base": i.valor_aluguel_base,
                "endereco": i.endereco
            }
            for i in imoveis
        ]
    }