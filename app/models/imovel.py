from typing import Optional
from pydantic import BaseModel


class ImovelBase(BaseModel):
    pass


class ImovelCreate(ImovelBase):
    pass


class ImovelUpdate(BaseModel):
    pass


class Imovel(ImovelBase):
    id: int
