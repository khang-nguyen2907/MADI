from madi.handlers import get_logger
from madi.utils import (
    load_default_config, 
    get_json_text
)
from madi.prompt_engineering import (
    LOGICAL_CONVERTER_ROLE, 
    LOGICAL_CONVERTER_INSTRUCTIONS, 
    LOGICAL_CONVERTER_MESSAGE
)
logger = get_logger(__name__)

configs = load_default_config()

def convert_logic_statement(
	clinical_diagnosis,
    schema=LogicClause.model_json_schema(),
):
    response = None
    agent = Agent(
        model=Groq(
            id=configs["madi_configs"]["groq_llm"]["init_diagnosis_model_name"],
            api_key=ENV_VAR["GROQ_API_KEY"]
        ),
        role=LOGICAL_CONVERTER_ROLE,
        instructions=LOGICAL_CONVERTER_INSTRUCTIONS,
    ) 
		# message =  f"""CHIEF COMPAIN: {chief_complain}
		# MEDICAL HISTORY: {medical_history}
		# PHYSICAL EXAMINATION: {physical_examination}
		# """
    message = LOGICAL_CONVERTER_MESSAGE.format(
            schema=schema,
            clinical_diagnosis=clinical_diagnosis
    )
    try:
        response = agent.run(message, stream=False).content
        statements = get_json_text(response)
    except Exception as e:
        logger.error(e)
        logger.error(response)

    return response