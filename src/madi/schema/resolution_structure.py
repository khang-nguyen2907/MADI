from typing import List
from pydantic import BaseModel, Field

class ResolutionResult(BaseModel):
    diagnosis: str = Field(..., description="Name of the diagnosis")
    proven: bool = Field(..., description="Whether the diagnosis is provable with given facts and rules")
    explanation: str = Field(..., description="Explanation of the inference process")
