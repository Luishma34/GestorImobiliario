from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.imovel import Imovel


class ProprietarioBase(SQLModel):
    """Modelo base com campos comuns do proprietário."""
    nome: str = Field(min_length=3, max_length=200, description="Nome completo do proprietário")
    cpf: str = Field(min_length=11, max_length=14, description="CPF do proprietário")
    email: Optional[str] = Field(default=None, max_length=100, description="Email do proprietário")
    telefone: str = Field(max_length=20, description="Telefone do proprietário")
    endereco: Optional[str] = Field(default=None, max_length=600, description="Endereço do proprietário")


class Proprietario(ProprietarioBase, table=True):
    """Modelo de tabela do banco de dados."""
    __tablename__ = "proprietarios"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relacionamento One-to-Many: Um proprietário pode ter vários imóveis
    imoveis: List["Imovel"] = Relationship(back_populates="proprietario")


class ProprietarioCreate(ProprietarioBase):
    """Schema para criação de proprietário."""
    pass


class ProprietarioUpdate(SQLModel):
    """Schema para atualização parcial de proprietário."""
    nome: Optional[str] = Field(default=None, min_length=3, max_length=200)
    cpf: Optional[str] = Field(default=None, min_length=11, max_length=14)
    email: Optional[str] = Field(default=None, max_length=100)
    telefone: Optional[str] = Field(default=None, max_length=20)
    endereco: Optional[str] = Field(default=None, max_length=600)


class ProprietarioPublic(ProprietarioBase):
    """Schema para resposta pública do proprietário."""
    id: int
