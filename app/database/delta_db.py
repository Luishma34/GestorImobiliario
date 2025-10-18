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
        try:
            dt = DeltaTable(self.table_path)


            dataset = dt.to_pyarrow_dataset()

            filter_expression = ds.field("id") == record_id

            result_table = dataset.to_table(filter=filter_expression)

            if result_table.num_rows > 0:
                return {key: value[0] for key, value in result_table.to_pydict().items()}
            return None
        except (TableNotFoundError, FileNotFoundError, pa.ArrowInvalid):
            return None

    def list(self, offset: int = 0, limit: int = 100) -> List[Dict[str, Any]]:

        try:
            dt = DeltaTable(self.table_path)

            reader = dt.to_pyarrow_dataset().scanner().to_reader()

            rows_in_page = []
            rows_seen = 0
            for batch in reader:
                if rows_seen < offset + limit:
                    batch_data = batch.to_pylist()

                    start_index = max(0, offset - rows_seen)
                    end_index = min(len(batch_data), offset + limit - rows_seen)

                    rows_in_page.extend(batch_data[start_index:end_index])

                rows_seen += len(batch)

                if len(rows_in_page) >= limit:
                    break

            return rows_in_page

        except (TableNotFoundError, FileNotFoundError):
            return []

    def update(self, record_id: int, data: Dict[str, Any]) -> bool:
        pass

    def delete(self, record_id: int) -> bool:
        pass

    def count(self) -> int:
        pass