from typing import List
from fastapi import APIRouter, status, Query, HTTPException
from app.models import Imovel, ImovelCreate, ImovelUpdate
from app.database import DeltaDatabase

from fastapi.responses import StreamingResponse
import io
import zipfile
import pyarrow.csv as pacsv


router = APIRouter(prefix="/imoveis", tags=["Imóveis"])

db = DeltaDatabase(table_name="imoveis")

@router.post("/", response_model=Imovel, status_code=status.HTTP_201_CREATED)
def criar_imovel(imovel: ImovelCreate):
    """Cria um novo imóvel no banco de dados."""
    imovel_data = imovel.model_dump()
    novo_id = db.insert(imovel_data)
    return Imovel(id=novo_id, **imovel_data)


@router.get("/", response_model=List[Imovel])
def listar_imoveis(
    pagina: int = Query(1, ge=1, description="Número da página"),
    registrosPorPagina: int = Query(10, ge=1, description="Quantidade de registros por página")
):
    """
    F2: Retorna uma página de imóveis cadastrados.
    """
    try:
        offset = (pagina - 1) * registrosPorPagina
        
        pa_table = db.get_all_as_arrow_table()

        if pa_table.num_rows == 0:
            return []
            
        if offset >= pa_table.num_rows:
            return [] 

        paginated_table = pa_table.slice(offset, registrosPorPagina)
        records_dict = paginated_table.to_pydict()

        keys = records_dict.keys()
        list_of_dicts = [dict(zip(keys, t)) for t in zip(*records_dict.values())]

        return list_of_dicts

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao processar paginação: {str(e)}"
        )


@router.get("/total", response_model=dict)
def total_cadastrados():
    """F4: Mostra a quantidade de entidades existentes."""
    total = db.count()
    return {"total": total}


@router.post("/vacuum", status_code=status.HTTP_200_OK, response_model=dict)
def vacuum_imoveis():
    """Executa a operação VACUUM para limpar arquivos antigos."""
    try:
        files_deleted = db.vacuum()
        
        return {
            "message": f"Operação de vacuum concluída. {len(files_deleted)} arquivos foram removidos.",
            "files": files_deleted
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro ao executar o vacuum: {e}"
        )

@router.get("/download/csv.zip", tags=["Imóveis"])
def download_imoveis_zip_streamed():
    """
    F5: Retorna todos os dados como um arquivo CSV compactado (.zip)
    via streaming.
    """
    try:
        zip_buffer = io.BytesIO()
        pa_table = db.get_all_as_arrow_table()

        if pa_table.num_rows == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Nenhum dado para exportar"
            )

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # CORREÇÃO AQUI: Removemos o 'TextIOWrapper'
            with zip_file.open('imoveis.csv', 'w') as csv_file:
                # Passamos o 'csv_file' (binário) direto para o 'write_csv'
                pacsv.write_csv(pa_table, csv_file)
        
        zip_buffer.seek(0)

        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": "attachment; filename=imoveis.zip"
            }
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar arquivo zip: {str(e)}"
        )


@router.get("/{imovel_id}", response_model=Imovel)
def buscar_imovel(imovel_id: int):
    """Busca um imóvel pelo seu ID."""
    imovel_data = db.get(imovel_id)
    if not imovel_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Imóvel com ID {imovel_id} não encontrado"
        )
    return Imovel(**imovel_data)


@router.put("/{imovel_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
def atualizar_imovel(imovel_id: int, imovel: ImovelUpdate):
    """Atualiza um imóvel existente."""
    imovel_existente = db.get(imovel_id)
    if not imovel_existente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Imóvel com ID {imovel_id} não encontrado."
        ) 
    
    imovel_data = imovel.model_dump(exclude_unset=True)
    try:
        success = db.update(imovel_id, imovel_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Imóvel com ID {imovel_id} não encontrado para atualização."
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro interno ao atualizar o imóvel: {e}"
        ) 		
    return None


@router.delete("/{imovel_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_imovel(imovel_id: int): 	
    """Deleta um imóvel existente."""
    imovel_existente = db.get(imovel_id)
    if not imovel_existente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Imóvel com ID {imovel_id} não encontrado."
        ) 
    try:
        success = db.delete(imovel_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Imóvel com ID {imovel_id} não encontrado para deleção."
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro interno ao deletar o imóvel: {e}"
        ) 		
    return None