from pathlib import Path
from typing import List, Dict, Any, Optional
import threading
import os
import pyarrow as pa
from deltalake import write_deltalake, DeltaTable
from deltalake.exceptions import TableNotFoundError
import pyarrow.dataset as ds


class DeltaDatabase:
    def __init__(self, table_name: str, base_path: str = "./data"):
        self.table_name = table_name
        self.base_path = Path(base_path)
        self.table_path = str(self.base_path / table_name)
        self.seq_file_path = self.base_path / f"{table_name}.seq"
        self._lock = threading.Lock()

        self.schema = pa.schema([
            pa.field("id", pa.int64()),
            pa.field("apelido_imovel", pa.string()),
            pa.field("descricao", pa.string()),
            pa.field("endereco", pa.string()),
            pa.field("valor_aluguel_base", pa.float64()),
            pa.field("tipo_imovel", pa.string()),
            pa.field("status", pa.string()),
            pa.field("id_proprietario", pa.int64())
        ])

        os.makedirs(self.base_path, exist_ok=True)
        if not self.seq_file_path.exists():
            with open(self.seq_file_path, 'w') as f:
                f.write('0')

    def _get_next_id(self) -> int:
        with self._lock:
            with open(self.seq_file_path, 'r+') as file:
                current_id = int(file.read().strip())
                next_id = current_id + 1
                file.seek(0)
                file.write(str(next_id))
                file.truncate()
                return next_id

    def insert(self, data: Dict[str, Any]) -> int:
        record_id = self._get_next_id()
        data_with_id = {"id": record_id, **data}

        pa_table = pa.Table.from_pydict(
            {k: [v] for k, v in data_with_id.items()},
            schema=self.schema
        )

        try:
            write_deltalake(self.table_path, pa_table, mode="append")
        except TableNotFoundError:
            write_deltalake(self.table_path, pa_table, mode="overwrite", schema=self.schema, configuration={"delta.enableChangeDataFeed": "true"})

        return record_id

    def get(self, record_id: int) -> Optional[Dict[str, Any]]:
        try:
            dt = DeltaTable(self.table_path)
            
            dataset = dt.to_pyarrow_dataset()
            
            result_table = dataset.to_table(filter=ds.field("id") == record_id)
            
            if result_table.num_rows > 0:
                py_dict = result_table.to_pydict()
                return {key: value[0] for key, value in py_dict.items()}
        except Exception as e:
            print(f"Ocorreu um erro inesperado ao buscar o registro {record_id}: {e}")

        return None
       

    def update(self, record_id: int, data: Dict[str, Any]) -> bool:
        try:
            dt = DeltaTable(self.table_path)
            
            result_metrics = dt.update(
                new_values=data,
                predicate=f"id = {record_id}"
            )

            if result_metrics.get('num_updated_rows', 0) > 0:
                return True
            else:
                return False

        except TableNotFoundError:
            return False
        except Exception as e:
            print(f"Erro inesperado ao atualizar o registro {record_id}: {e}")
            raise e


    def delete(self, record_id: int) -> bool:
        try:
            dt = DeltaTable(self.table_path)
            
            result_metrics = dt.delete(predicate=f"id = {record_id}")

            if result_metrics.get('num_deleted_rows', 0) > 0:
                return True
            else:
                return False

        except TableNotFoundError:
            return False
        except Exception as e:
            print(f"Erro inesperado ao deletar o registro {record_id}: {e}")
            raise e

    def count(self) -> int:
        try:
            dt = DeltaTable(self.table_path)
            return dt.to_pyarrow_dataset().count_rows()
        except TableNotFoundError:
            return 0
        except Exception as e:
            print(f"Erro inesperado ao contar os registros: {e}")
            raise e
        
    def vacuum(self) -> List[str]:
        try:
            dt = DeltaTable(self.table_path)
            files_deleted = dt.vacuum(retention_hours=0, enforce_retention_duration=False)
            return files_deleted
        except TableNotFoundError:
            return []
        except Exception as e:
            print(f"Erro inesperado ao executar o vacuum na tabela: {e}")
            raise e