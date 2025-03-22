from phi.agent import Agent
from phi.model.groq import Groq
from pydantic import BaseModel, Field
from typing import List

from madi.constants import ENV_VAR
from madi.prompt_engineering import (
    TEAMUP_INSTRUCTIONS_V1, 
    TEAMUP_ROLE_V1
)
from madi.utils import load_default_config
from madi.schema import SelectedDepartments

configs = load_default_config()

hospital_guide_agent = Agent(
    model=Groq(
        id=configs["madi_configs"]["llm"]["hospital_guide_model_name"],
        api_key=ENV_VAR["GROQ_API_KEY"]
    ),
    role=TEAMUP_ROLE_V1,
    instructions=TEAMUP_INSTRUCTIONS_V1,
    response_model=SelectedDepartments,
) 

def select_departments(
    message: str,
    agent: Agent, 
    stream: bool = False
) -> SelectedDepartments:
    response = agent.run(message, stream=stream)
    return response.content

def setup_clinician_team(
    department: SelectedDepartments,
    num_clinicians: int = 1,
) -> List[str]:

    clinician_team = []

    for doj in department.departments:
        for cl in range(num_clinicians):
            department_name = doj.department

            clinician_team.append(department_name)
    return clinician_team

if __name__ == "__main__": 
    message = '''The following is the patient's information:
    Middle-aged male, XX years old. (We anonymize the age information in the sample data presented.).
    Chief Complaint: Vomiting blood for 2 days after eating.

    Your selected department:'''
    selected_departments = select_departments(message, hospital_guide_agent)
    clinician_team = setup_clinician_team(selected_departments)
    print(clinician_team)