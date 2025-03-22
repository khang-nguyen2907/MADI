from typing import List, Optional
from pydantic import BaseModel, Field
class Statement(BaseModel):
    text: List[str] = Field(..., description="Logical statement(s).  A single string for facts, a list of strings for multi-part rules.")
    type: str = Field(..., description="Fact or rule")
    source: str = Field(..., description="Original text that the statement is converted from")
    relates_to: Optional[str] = Field(None, description="The disease this statement relates to. Useful for filtering.")

class LogicClause(BaseModel):
    diagnosis: str = Field(..., description="Name of a disease")
    statements: List[Statement] = Field(..., description="List of logical statements converted from diagnosis rationale")
