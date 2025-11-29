from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.contrato import Contrato


class InquilinoBase(SQLModel):
    """Modelo base com campos comuns do inquilino."""
    nome: str = Field(min_length=3, max_length=200, description="Nome completo do inquilino")
    cpf: str = Field(min_length=11, max_length=14, description="CPF do inquilino")
    email: Optional[str] = Field(default=None, max_length=100, description="Email do inquilino")
    telefone: str = Field(max_length=20, description="Telefone do inquilino")
    endereco_anterior: Optional[str] = Field(default=None, max_length=600, description="Endereço anterior do inquilino")
    renda_mensal: Optional[float] = Field(default=None, gt=0, description="Renda mensal do inquilino")


class Inquilino(InquilinoBase, table=True):
    """Modelo de tabela do banco de dados."""
    __tablename__ = "inquilinos"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relacionamento Many-to-Many com Imóvel através da tabela Contrato
    contratos: List["Contrato"] = Relationship(back_populates="inquilino")


class InquilinoCreate(InquilinoBase):
    """Schema para criação de inquilino."""
    pass


class InquilinoUpdate(SQLModel):
    """Schema para atualização parcial de inquilino."""
    nome: Optional[str] = Field(default=None, min_length=3, max_length=200)
    cpf: Optional[str] = Field(default=None, min_length=11, max_length=14)
    email: Optional[str] = Field(default=None, max_length=100)
    telefone: Optional[str] = Field(default=None, max_length=20)
    endereco_anterior: Optional[str] = Field(default=None, max_length=600)
    renda_mensal: Optional[float] = Field(default=None, gt=0)


class InquilinoPublic(InquilinoBase):
    """Schema para resposta pública do inquilino."""
    id: int
