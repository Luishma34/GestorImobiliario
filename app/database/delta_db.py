from pathlib import Path
from typing import List, Dict, Any, Optional


class DeltaDatabase:
    def __init__(self, table_name: str, base_path: str = "./data"):
        self.table_name = table_name
        self.base_path = Path(base_path)
        self.table_path = self.base_path / table_name
        
        # TODO: Implementar inicialização

    def insert(self, data: Dict[str, Any]) -> int:
        pass

    def get(self, record_id: int) -> Optional[Dict[str, Any]]:
        pass

    def list(self, offset: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        pass

    def update(self, record_id: int, data: Dict[str, Any]) -> bool:
        pass

    def delete(self, record_id: int) -> bool:
        pass

    def count(self) -> int:
        pass
