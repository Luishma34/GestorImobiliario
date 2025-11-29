from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.proprietario import Proprietario
    from app.models.contrato import Contrato


class ImovelBase(SQLModel):
    """Modelo base com campos comuns do imóvel."""
    apelido_imovel: str = Field(min_length=3, max_length=100, description="Casa da Praia Apto Centro")
    descricao: Optional[str] = Field(default=None, max_length=500, description="Descrição detalhada do imóvel")
    endereco: str = Field(max_length=600, description="Rua|Av Fulano da Silva , Bairro Bom Lugar Nº 123")
    valor_aluguel_base: float = Field(gt=0, description="Valor do aluguel do imóvel")
    tipo_imovel: str = Field(description="Casa ou Apartamento")
    status: str = Field(description="Alugado, Disponivel, Em Manutenção")
    id_proprietario: Optional[int] = Field(default=None, foreign_key="proprietarios.id", description="Id do Proprietario do Imovel")


class Imovel(ImovelBase, table=True):
    """Modelo de tabela do banco de dados."""
    __tablename__ = "imoveis"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relacionamento Many-to-One: Vários imóveis podem pertencer a um proprietário
    proprietario: Optional["Proprietario"] = Relationship(back_populates="imoveis")
    
    # Relacionamento Many-to-Many com Inquilino através da tabela Contrato
    contratos: List["Contrato"] = Relationship(back_populates="imovel")


class ImovelCreate(ImovelBase):
    """Schema para criação de imóvel."""
    pass


class ImovelUpdate(SQLModel):
    """Schema para atualização parcial de imóvel."""
    apelido_imovel: Optional[str] = Field(default=None, min_length=3, max_length=100)
    descricao: Optional[str] = Field(default=None, max_length=500)
    endereco: Optional[str] = Field(default=None, max_length=600)
    valor_aluguel_base: Optional[float] = Field(default=None, gt=0)
    tipo_imovel: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    id_proprietario: Optional[int] = Field(default=None, ge=0)


class ImovelPublic(ImovelBase):
    """Schema para resposta pública do imóvel."""
    id: int
