from typing import Optional
import time
import json
from phi.agent import Agent
from phi.model.groq import Groq
from pydantic import BaseModel, Field
from typing import List

from madi.constants import ENV_VAR
from madi.utils import (
    load_default_config, 
    get_json_text
)
from madi.llm import gen_text
from madi.tools import (
    phi_duckgo_search, 
    phi_pubmed_search
)
from madi.constants import department_dictionary
from madi.prompt_engineering import (
    INITIAL_DIAGNOSIS_INSTRUCTIONS_V1, 
    INITIAL_DIAGNOSIS_MESSAGE_V1, 
    CLINICIAN_LEADER_ROLE_V1, 
    CLINICIAN_LEADER_INSTRUCTIONS_V1, 
    CLINICIAN_LEADER_MESSAGE_V1
)
from madi.schema import InitialDiagnosis
from madi.handlers import Log

logger = Log(__name__)

configs = load_default_config()

duckgo_search_tool = phi_duckgo_search()
pubmed_search_tool = phi_pubmed_search()

def init_diagnosis(
	clinician_team: List[str],
	chief_complain: str,
	medical_history: str,
	physical_examination: str, 
    max_retries: int = 3
):
    results = {}
    for clinician_agent in clinician_team:
        response = None
        agent = Agent(
            model=Groq(
                id=configs["madi_configs"]["groq_llm"]["init_diagnosis_model_name"],
                api_key=ENV_VAR["GROQ_API_KEY"]
            ),
            role=department_dictionary[clinician_agent]["role"],
            instructions=INITIAL_DIAGNOSIS_INSTRUCTIONS_V1,
            tools=[duckgo_search_tool, pubmed_search_tool],
        ) 
        message = INITIAL_DIAGNOSIS_MESSAGE_V1.format(
                schema=InitialDiagnosis.model_json_schema(),
                chief_complain=chief_complain,
                medical_history=medical_history,
                physical_examination=physical_examination
        )
        # TODO: create generate functions because there are retries, 
        # there are try catch for run, try catch for parsing 
        # try:
        #     # TODO: retry when parsing get wrong: empty, service unaccessable
        #     response = agent.run(message, stream=False).content
        #     if "```json" in response: 
        #         diagnosis = get_json_text(response)
        #     else: 
        #         diagnosis = response
        # except Exception as e:
        #     logger.error(e)
        #     print("Response:", response)
        #     diagnosis = response
        diagnosis = gen_text(
            agent, 
            message, 
            max_retries, 
            True
        )
        results[clinician_agent] = diagnosis
        
    return results

def synthesize(results, max_retries: int = 3):
    leader_agent = Agent(
        model=Groq(
            id=configs["madi_configs"]["groq_llm"]["leader_model_name"],
            api_key=ENV_VAR["GROQ_API_KEY"]
        ),
        role=CLINICIAN_LEADER_ROLE_V1,
        instructions=CLINICIAN_LEADER_INSTRUCTIONS_V1
    ) 
    diagnoses = [f"{k} clinician:\n{v}" for k, v in results.items()]
    leader_message = CLINICIAN_LEADER_MESSAGE_V1.format(
            schema=InitialDiagnosis.model_json_schema(),
            diagnoses="\n\n".join(diagnoses)

    )
    # leader_response = leader_agent.run(str(leader_message), stream=False).content
    # try: 
    #     diagnosis = get_json_text(leader_response)
    # except Exception as e: 
    #     logger.error(e)
    #     diagnosis = leader_response
    
    diagnosis = gen_text(
        leader_agent, 
        leader_message, 
        max_retries, 
        True
    )
    return diagnosis

if __name__ == "__main__": 
    clinician_team=['Gastroenterology', 'Emergency']
    chief_complaint = "Vomiting blood for 2 days after eating."
    medical_history = "The patient experienced vomiting of coffee-colored gastric contents (approximately 100ml) accompanied by dizziness, palpitations, and weakness after consuming hard food 2 days ago. There was no abdominal distension, pain, melena, or bloody stool, nor any confusion. The patient was treated conservatively with acid-suppressing and hemostatic medications, after which symptoms of vomiting blood improved. The patient has a history of chronic Hepatitis B for three years, which has not been treated."
    physical_examination = "Pale skin and mucous membranes, flat abdomen with no visible peristaltic waves and presence of abdominal breathing. No abdominal wall vein varicosity was observed. The abdomen was soft without fluid wave or shifting dullness, and no palpable masses. There was no significant tenderness or rebound tenderness, and the liver and spleen were not palpable below the ribs. Murphy's sign was negative. No evident kidney area tenderness or percussion pain, and no abnormal vascular pulsation in the abdomen. No significant tenderness at bilateral ureteral pressure points. Liver dullness was present, with the upper boundary at the right mid-clavicular line at the fifth intercostal space, with no shifting dullness. Bowel sounds were normal."


    clinician_diagnoses = init_diagnosis(
        clinician_team,
        chief_complaint,
        medical_history,
        physical_examination
    )

    # logger.info(clinician_diagnoses)
    print("\nCLINICIAN DIAGNOSES\n")
    print(clinician_diagnoses)

    print("\nCOMBINED DIAGNOSIS\n")
    combined_diagnosis = synthesize(clinician_diagnoses)
    print(combined_diagnosis)