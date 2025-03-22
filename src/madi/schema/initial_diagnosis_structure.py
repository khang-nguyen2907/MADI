from typing import List, Optional
from pydantic import BaseModel, Field

class Evidence(BaseModel):
    type: str = Field(..., description="Type of evidence: 'fact' or 'rule'.")
    content: str = Field(..., description="The evidence itself.")
    source: str = Field(..., description="Source of the evidence (e.g., chief complaint, medical history, PubMed URL).")
    relates_to: Optional[str] = Field(None, description="For rules, the specific disease they relate to.") # Add this field

class Disease(BaseModel):
    name: str = Field(..., description="Name of the disease.")
    evidences: List[Evidence] = Field(..., description="Evidence supporting the diagnosis.")

class PossibleDiseases(BaseModel):
    diagnoses: List[Disease] = Field(..., description="List of possible diagnoses.")

class Test(BaseModel):  # Renamed for clarity
    name: str = Field(..., description="Name of the test.")
    explanation: str = Field(..., description="Reason for the test.")

class LabTest(BaseModel):
    needed: bool = Field(..., description="Whether further lab tests are needed.")
    details: Optional[List[Test]] = Field(None, description="Details of required lab tests and their rationale (if needed).") # Optional

class ImageTest(BaseModel):
    needed: bool = Field(..., description="Whether further imaging tests are needed.")
    details: Optional[List[Test]] = Field(None, description="Details of required imaging tests and their rationale (if needed).") # Optional

class InitialDiagnosis(BaseModel):
    possible_diseases: PossibleDiseases = Field(..., description="Possible diagnoses.")
    laboratory_test: LabTest = Field(..., description="Lab test recommendations.")
    imaging_test: ImageTest = Field(..., description="Imaging test recommendations.")  # More common term