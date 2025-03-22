from pydantic import BaseModel, Field
from typing import List

class Department(BaseModel):
    department: str = Field(..., description="a selected department from the list of hospital departments that the patient is sent to")
    reason: str = Field(..., description="The reason why the patient should be sent to the department")

class SelectedDepartments(BaseModel):
    departments: List[Department] = Field(..., description="List of department which show departments and reasons that a patients is sent to")
