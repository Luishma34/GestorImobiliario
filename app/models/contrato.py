from typing import Optional, TYPE_CHECKING
from datetime import date
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.inquilino import Inquilino
    from app.models.imovel import Imovel


class ContratoBase(SQLModel):
    """
    Modelo base do Contrato - Tabela intermediária para relacionamento Many-to-Many
    entre Inquilino e Imóvel.
    """
    id_inquilino: int = Field(foreign_key="inquilinos.id", description="ID do inquilino")
    id_imovel: int = Field(foreign_key="imoveis.id", description="ID do imóvel")
    data_inicio: date = Field(description="Data de início do contrato")
    data_fim: date = Field(description="Data de término do contrato")
    valor_aluguel: float = Field(gt=0, description="Valor do aluguel acordado")
    dia_vencimento: int = Field(ge=1, le=31, description="Dia do vencimento do aluguel")
    status: str = Field(default="ativo", description="Status do contrato: ativo, encerrado, cancelado")
    observacoes: Optional[str] = Field(default=None, max_length=1000, description="Observações do contrato")


class Contrato(ContratoBase, table=True):
    """
    Modelo de tabela do banco de dados.
    Esta tabela representa o relacionamento Many-to-Many entre Inquilino e Imóvel.
    Um inquilino pode ter vários contratos (alugar vários imóveis ao longo do tempo).
    Um imóvel pode ter vários contratos (ser alugado por vários inquilinos ao longo do tempo).
    """
    __tablename__ = "contratos"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relacionamentos
    inquilino: "Inquilino" = Relationship(back_populates="contratos")
    imovel: "Imovel" = Relationship(back_populates="contratos")


class ContratoCreate(ContratoBase):
    """Schema para criação de contrato."""
    pass


class ContratoUpdate(SQLModel):
    """Schema para atualização parcial de contrato."""
    data_inicio: Optional[date] = Field(default=None)
    data_fim: Optional[date] = Field(default=None)
    valor_aluguel: Optional[float] = Field(default=None, gt=0)
    dia_vencimento: Optional[int] = Field(default=None, ge=1, le=31)
    status: Optional[str] = Field(default=None)
    observacoes: Optional[str] = Field(default=None, max_length=1000)


class ContratoPublic(ContratoBase):
    """Schema para resposta pública do contrato."""
    id: int
