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
            write_deltalake(self.table_path, pa_table, mode="overwrite", schema=self.schema)

        return record_id

    def get(self, record_id: int) -> Optional[Dict[str, Any]]:
        ###GET ta com problemaaaa to resolvendo sa merda
        try:
            dataset = ds.dataset(self.table_path, format="delta")
            result_table = dataset.to_table(filter=ds.field("id") == record_id)
            if result_table.num_rows > 0:
                return {key: value[0] for key, value in result_table.to_pydict().items()}
            return None
        except (TableNotFoundError, FileNotFoundError):
            return None

    def update(self, record_id: int, data: Dict[str, Any]) -> bool:
        pass

    def delete(self, record_id: int) -> bool:
        pass

    def count(self) -> int:
        pass