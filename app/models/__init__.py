"""
Modelos de entidades do sistema
"""

from .imovel import Imovel, ImovelCreate, ImovelUpdate, ImovelPublic
from .proprietario import Proprietario, ProprietarioCreate, ProprietarioUpdate, ProprietarioPublic
from .inquilino import Inquilino, InquilinoCreate, InquilinoUpdate, InquilinoPublic
from .contrato import Contrato, ContratoCreate, ContratoUpdate, ContratoPublic

__all__ = [
    "Imovel", "ImovelCreate", "ImovelUpdate", "ImovelPublic",
    "Proprietario", "ProprietarioCreate", "ProprietarioUpdate", "ProprietarioPublic",
    "Inquilino", "InquilinoCreate", "InquilinoUpdate", "InquilinoPublic",
    "Contrato", "ContratoCreate", "ContratoUpdate", "ContratoPublic",
]
