from pydantic import BaseModel
from typing import List, Dict, Any

class EnrichmentRequest(BaseModel):

    rows: List[Dict[str, Any]]