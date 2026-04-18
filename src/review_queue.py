from typing import List, Dict, Optional


class ReviewQueue:
    def __init__(self):
        self._items: Dict[int, Dict] = {}
        self._next_id: int = 1
    
    def add_item(self, mapping: dict, reason: str) -> int:
        item_id = self._next_id
        self._next_id += 1
        
        self._items[item_id] = {
            "id": item_id,
            "mapping": mapping,
            "reason": reason,
            "status": "pending"
        }
        
        return item_id
    
    def list_items(self, status: Optional[str] = None) -> List[dict]:
        items = list(self._items.values())
    
        if status is not None:
            items = [item for item in items if item["status"] == status]
    
        return [item.copy() for item in items]
    
    def get_item(self, item_id: int) -> Optional[dict]:
        item = self._items.get(item_id)
        return item.copy() if item else None
    
    def resolve_item(self, item_id: int, decision: str) -> bool:
        if decision not in ("approved", "rejected"):
            return False
        
        item = self._items.get(item_id)
        if item is None:
            return False
        
        item["status"] = decision
        return True
