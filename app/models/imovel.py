from typing import Optional
from pydantic import BaseModel, Field


class ImovelBase(BaseModel):
    apelido_imovel: str = Field(..., min_length=3, max_length=100, description="Casa da Praia Apto Centro")
    descricao: Optional[str] = Field(..., max_length=500, description="Descrição detalhada do imóvel")
    endereco: str = Field(..., max_length=600, description="Rua|Av Fulano da Silva , Bairro Bom Lugar Nº 123")
    valor_aluguel_base: float = Field(..., gt=0, description="Valor do alguel  do imóvel")
    tipo_imovel: str = Field(..., description="Casa ou Apartamento")
    status: str = Field(...,  description="Alugado, Disponivel, Em Manutenção")
    id_proprietario: int =Field(...,ge=0, description="Id do Proprietario do Imovel" )


class ImovelCreate(ImovelBase):
    pass


class ImovelUpdate(ImovelBase):
    pass


class Imovel(ImovelBase):
    id: int
