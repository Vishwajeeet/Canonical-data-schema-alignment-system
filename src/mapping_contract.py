from pydantic import BaseModel, Field
from typing import Optional


class SchemaMapping(BaseModel):
    source_column: str = Field(..., description="Column name from input dataset")
    target_field: str = Field(..., description="Field in canonical schema")
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: Optional[str] = Field(
        None, description="Why this mapping was suggested"
    )
