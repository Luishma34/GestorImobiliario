from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from enum import Enum
import hashlib

router = APIRouter(prefix="/util", tags=["Utilidades"])

class HashFunction(str, Enum):
    md5 = "MD5"
    sha1 = "SHA1"
    sha256 = "SHA256"

class HashRequest(BaseModel):
    data: str
    function: HashFunction

class HashResponse(BaseModel):
    data: str
    function: str
    hash_result: str

@router.post("/hash/", response_model=HashResponse)
def get_hash(request: HashRequest):
    """
    F6: Recebe um dado (string) e o nome de uma função de hash (MD5, SHA1, SHA256)
    e retorna o hash correspondente.
    """
    try:
        data_bytes = request.data.encode('utf-8')
        h = None

        if request.function == HashFunction.md5:
            h = hashlib.md5(data_bytes)
        elif request.function == HashFunction.sha1:
            h = hashlib.sha1(data_bytes)
        elif request.function == HashFunction.sha256:
            h = hashlib.sha256(data_bytes)
        
        if h is None:
            raise HTTPException(status_code=400, detail="Função de hash inválida")

        return HashResponse(
            data=request.data,
            function=request.function.value,
            hash_result=h.hexdigest()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular hash: {str(e)}")