from typing import List
from typing import Dict
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class OutputComparison(BaseModel):
    name: str
    additions: List[str] = []
    removals: List[str] = []


class Output(BaseModel):
    revision: UUID
    previous: Optional[UUID] = None
    created: datetime
    comparison: Optional[List[OutputComparison]] = []
    current_fields: Dict[str, List[str]]
