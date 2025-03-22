import json
from madi.agents import (
    SearchAgent, 
    ClinicianAgent, 
    SynthesizeClinicianAgent
)
from madi.llm import (
    generate_response, 
    refine_medoc, 
    summarize_medoc
)
from madi.handlers import Log
from madi.constants import ENV_VAR

from madi.prompt_engineering import (
    CLINICIAN_AGENT_ROLE, 
    CLINICIAN_AGENT_INSTRUCTIONS, 
    CLINICIAN_AGENT_CAPABILITIES, 
    SEARCH_ENGINE_AGENT_ROLE, 
    SEARCH_ENGINE_AGENT_INSTRUCTIONS, 
    SEARCH_ENGINE_AGENT_CAPABILITIES, 
    CLINICIAN_SYNTHESIZE_AGENT_ROLE, 
    CLINICIAN_SYNTHESIZE_AGENT_INSTRUCTIONS, 
    CLINICIAN_SYNTHESIZE_AGENT_CAPABILITIES, 
    KNOWLEDGE_MESSAGE, 
    KNOWLEDGE_ROLE, 
    ENTITY_MESSAGE, 
    ENTITY_ROLE

)
from groq import Groq
from madi.tools import duckgo_search, search_pubmed
from madi.schema import (
    PubmedSearchResult, 
    DDuckGoSearchResult, 
    patient_entity_json_format, 
    knowledge_json_format, 
    final_diagnosis_format

)
from madi.rule_based_systems import ResolutionBasedVerifier
from madi.utils import (
    load_default_config, 
    get_all_medical_knowledge_findings, 
    get_all_patient_findings, 
    get_all_possible_diseases, 
    normalize_text
)

logger = Log(__name__)
configs = load_default_config()

# if __name__ == "__main__": 
def diagnose(chief_complaint, medical_history, physical_examination):
    llm=Groq(
        api_key=ENV_VAR["GROQ_API_KEY"]
    )
    clinician_agent = ClinicianAgent(
        llm, 
        role=CLINICIAN_AGENT_ROLE,
        instructions=CLINICIAN_AGENT_INSTRUCTIONS,
        capabilities=CLINICIAN_AGENT_CAPABILITIES, 
        max_retries=3
    )
    search_agent = SearchAgent(
        llm, 
        role=SEARCH_ENGINE_AGENT_ROLE,
        instructions=SEARCH_ENGINE_AGENT_INSTRUCTIONS,
        capabilities=SEARCH_ENGINE_AGENT_CAPABILITIES, 
        max_retries=3
    )
    # synthesize_agent = SynthesizeClinicianAgent(
    #     llm, 
    #     role=CLINICIAN_SYNTHESIZE_AGENT_ROLE,
    #     instructions=CLINICIAN_SYNTHESIZE_AGENT_INSTRUCTIONS,
    #     capabilities=CLINICIAN_SYNTHESIZE_AGENT_CAPABILITIES, 
    #     max_retries=3
    # )

    verifier = ResolutionBasedVerifier()


    search_agent.add_tool(duckgo_search)
    search_agent.add_tool(search_pubmed)

    message = f"""Chief complain: {chief_complaint}
    Medical history: {medical_history}
    Physical examination: {physical_examination}
    """

    # RESEARCH 

    search_results = search_agent.execute(message)
    search_result_texts = []
    if isinstance(search_results, list): 
        for i, data in enumerate(search_results): 
            logger.info(f"SEARCH RESULT {i}", data)
            if isinstance(data, PubmedSearchResult):
                text = [f"""# Pubmed document {i}:"""]
                
                if data.abstract is not None: 
                    text.append(data.abstract)
                if data.methods is not None: 
                    text.append(data.methods)
                if data.results is not None: 
                    text.append(data.results)
                if data.conclusions is not None: 
                    text.append(data.conclusions)
                text = "\n".join(text)
            elif isinstance(data, DDuckGoSearchResult): 
                text = f"""Internet document {i}:
                {data.content}"""
            search_result_texts.append(text)
    logger.info("SEARCH RESULT", search_result_texts)
    logger.info("NUMBER OF MEDICAL DOCUMENTS", len(search_result_texts))

    # FIRST DIAGNOSIS

    logger.title("START TO DIAGNOSE")
    
    # Refine document

    logger.title("1ST: sUMMARIZE MEDICAL DOCUMENT")
    fist_refined_medical_documents = summarize_medoc(
        client=llm, 
        medoc=search_result_texts, 
        model=configs["madi_configs"]["llm"]["default_model_name"], 
        service=configs["madi_configs"]['llm_service'],
        temperature=configs["madi_configs"]["gen_config"]["temperature"], 
        max_completion_tokens=configs["madi_configs"]["gen_config"]["max_completion_tokens"], 
        top_p=configs["madi_configs"]["gen_config"]["top_p"], 
        stop=configs["madi_configs"]["gen_config"]["stop"],
        stream=configs["madi_configs"]["gen_config"]["stream"],
        max_retries=3,
    )

    # diagnosis_message = f"""Chief complain: {chief_complaint}
    # Medical history: {medical_history}
    # Physical examination: {physical_examination}
    # Medical document: {fist_refined_medical_documents}
    # """
    # logger.info(f"DIAGNOSIS MESSAGE: {diagnosis_message}")

    # diagnosis_result = clinician_agent.execute(diagnosis_message)
    # print("\nDIAGNOSIS RESULT:\n")
    # logger.info(f"DIAGNOSIS RESULT: {diagnosis_result}")

    # # RESEARCH MORE
    
    # additional_info = []
    # if isinstance(diagnosis_result, dict): 
    #     requires_research_message = f"""This is the thought and plan of a clinician who needs more knowledge to create final diagnosis: 
    #     Thought: {diagnosis_result["thought"]}

    #     Plan: {diagnosis_result["plan"]}
    #     """
    #     logger.info("START TO RESEARCH MORE")
    #     more_info = search_agent.execute(requires_research_message)
    #     logger.info(f"REQUIRES MORE INFO: {more_info}")
        
    #     for i, info in enumerate(more_info): 
    #         if isinstance(info, PubmedSearchResult):
    #             text = f"""# Pubmed document {i}: 
    #             {info.abstract}
    #             {info.methods}
    #             {info.results}
    #             {info.conclusions}
    #             """
    #         elif isinstance(info, DDuckGoSearchResult): 
    #             text = f"""Internet Document {i}:
    #             {info.content}"""
    #         additional_info.append(text)
        
    # search_result_texts.extend(additional_info)

    # # REFINE ADDITIONAL DOCUMENT
    # logger.info("2ND: SUMMARIZE ADDITIONAL MEDICAL DOCUMENT")
    # refined_additional_medical_documents = summarize_medoc(
    #     client=llm, 
    #     medoc=additional_info, 
    #     model=configs["madi_configs"]["llm"]["default_model_name"], 
    #     service=configs["madi_configs"]['llm_service'],
    #     temperature=configs["madi_configs"]["gen_config"]["temperature"], 
    #     max_completion_tokens=configs["madi_configs"]["gen_config"]["max_completion_tokens"], 
    #     top_p=configs["madi_configs"]["gen_config"]["top_p"], 
    #     stop=configs["madi_configs"]["gen_config"]["stop"],
    #     stream=configs["madi_configs"]["gen_config"]["stream"],
    #     max_retries=3,
    # )

    # GENERATE FINAL DIAGNOSIS

    # final_diagnosis_prompt = f"""Let's create final diagnosis: 
    # Chief complain: {chief_complaint}
    # Medical history: {medical_history}
    # Physical examination: {physical_examination}
    # Medical documents: {"\n".join(fist_refined_medical_documents + refined_additional_medical_documents)}
    # """

    final_diagnosis_prompt = f"""Let's create final diagnosis: 
    Your response must follow the schema: {json.dumps(final_diagnosis_format)}

    Chief complain: {chief_complaint}
    Medical history: {medical_history}
    Physical examination: {physical_examination}
    Medical documents: {"\n".join(fist_refined_medical_documents)}
    """

    final_diagnosis_message = [
        {
            "role": "system", 
            "content": CLINICIAN_SYNTHESIZE_AGENT_ROLE + "\n" + "\n".join(CLINICIAN_SYNTHESIZE_AGENT_INSTRUCTIONS)
        }, 
        {
            "role": "user", 
            "content": final_diagnosis_prompt
        }
    ]
    logger.info("FINAL_DIAGNOSIS MESSAGE", final_diagnosis_message)
    # # final_diagnosis = synthesize_agent.execute(final_diagnosis_message)
    final_diagnosis = generate_response(
        client=llm, 
        messages=final_diagnosis_message, 
        model=configs["madi_configs"]["llm"]["default_model_name"], 
        service=configs["madi_configs"]['llm_service'],
        temperature=configs["madi_configs"]["gen_config"]["temperature"], 
        max_completion_tokens=configs["madi_configs"]["gen_config"]["max_completion_tokens"], 
        top_p=configs["madi_configs"]["gen_config"]["top_p"], 
        stop=configs["madi_configs"]["gen_config"]["stop"],
        stream=configs["madi_configs"]["gen_config"]["stream"],
        max_retries=3,
        parse_json=True
    )

    logger.info("FINAL DIAGNOSIS", final_diagnosis)

    all_possible_diseases = get_all_possible_diseases(final_diagnosis)

    # structure key patient data
    structured_patient_data_message = [
        {
            "role": "system", 
            "content": ENTITY_ROLE
        }, 
        {
            "role": "user", 
            "content": ENTITY_MESSAGE.format(
                chief_complaint=chief_complaint,
                medical_history=medical_history,
                physical_examination=physical_examination, 
                json_format=patient_entity_json_format
            )
        }
    ]
    # TODO structure cc, mh, pe separately
    structured_patient_data = generate_response(
        client=llm, 
        messages=structured_patient_data_message, 
        model=configs["madi_configs"]["llm"]["default_model_name"], 
        service=configs["madi_configs"]['llm_service'],
        temperature=configs["madi_configs"]["gen_config"]["temperature"], 
        max_completion_tokens=configs["madi_configs"]["gen_config"]["max_completion_tokens"], 
        top_p=configs["madi_configs"]["gen_config"]["top_p"], 
        stop=configs["madi_configs"]["gen_config"]["stop"],
        stream=configs["madi_configs"]["gen_config"]["stream"],
        max_retries=3,
        parse_json=True
    )
    patient_facts = get_all_patient_findings(structured_patient_data)
    logger.info("PATIENT_FACTS", patient_facts)

    # Structure rules 
    disease_to_factors = dict()
    for i, medical_knowledge in enumerate(search_result_texts): 

        structured_medknowledge_message = [
            {
                "role": "system", 
                "content": KNOWLEDGE_ROLE
            }, 
            {
                "role": "user", 
                # "content": KNOWLEDGE_MESSAGE.format(medical_knowledge=search_result_texts[:3], json_format=knowledge_json_format
                "content": KNOWLEDGE_MESSAGE.format(medical_knowledge=medical_knowledge, json_format=knowledge_json_format)
            }
        ]
        structured_medical_knowledge = generate_response(
            client=llm, 
            messages=structured_medknowledge_message, 
            model=configs["madi_configs"]["llm"]["default_model_name"], 
            service=configs["madi_configs"]['llm_service'],
            temperature=configs["madi_configs"]["gen_config"]["temperature"], 
            max_completion_tokens=configs["madi_configs"]["gen_config"]["max_completion_tokens"], 
            top_p=configs["madi_configs"]["gen_config"]["top_p"], 
            stop=configs["madi_configs"]["gen_config"]["stop"],
            stream=configs["madi_configs"]["gen_config"]["stream"],
            max_retries=3,
            parse_json=True
        )
        logger.info(f"MEDICAL KNOWLEDGE {i}", medical_knowledge)
        logger.info(f"STRUCTURED MEDICAL KNOWLEDGE {i}", structured_medical_knowledge)
    
        disease_to_factors |= get_all_medical_knowledge_findings(structured_medical_knowledge)
    disease_factors = []
    for _, v in disease_to_factors.items(): 
        for factor in v: 
            disease_factors.append(factor)
    logger.info("All disease factors", disease_factors)
    enriched_patient_facts = verifier.enrich_patient_facts(disease_factors, patient_facts)
    logger.info("ENRICHED PATIENT_FACTS", enriched_patient_facts)
    logger.info("DISEASE_TO_FACTORS", disease_to_factors)
    

    normalized_enriched_patient_facts = []
    for fact in enriched_patient_facts:
        normalized_enriched_patient_facts.append(normalize_text(fact))

    normalized_disease_to_factors = {}
    for k, v in disease_to_factors.items():
        normalized_values = []
        for va in v:
            normalized_values.append(normalize_text(va))
        norm_k = normalize_text(k)
        normalized_disease_to_factors[norm_k] = normalized_values
    
    return all_possible_diseases, normalized_disease_to_factors, normalized_enriched_patient_facts
    

def verify(all_possible_diseases, normalized_disease_to_factors, normalized_enriched_patient_facts):
    verifier = ResolutionBasedVerifier()
    valid_diseases = []
    possible_diseases = []
    reasoning_steps = []

    for possible_disease in all_possible_diseases: 
        is_valid, reasoning, updated_patient_facts = verifier.validate_diagnosis_by_resolution(
            possible_disease,
            normalized_disease_to_factors,
            normalized_enriched_patient_facts, 
            interactive=True
        ) 
        valid_diseases.append(
            {
                "disease": possible_disease, 
                "is_valid": is_valid,
                "reasoning": reasoning
            }
        )
        possible_diseases.append(possible_disease)
        normalized_enriched_patient_facts = updated_patient_facts

        # Reasoning text
        reasoning_steps.extend([f"*{possible_disease}", ""])
        for r in reasoning: 
            reasoning_steps.append(r)



    logger.info("POSSIBLE DISEASE(S)", valid_diseases)
    logger.info("UPDATED PATIENT FACTS", normalized_enriched_patient_facts)

    return all_possible_diseases,valid_diseases, normalized_enriched_patient_facts

if __name__ == "__main__": 
    chief_complaint = "Vomiting blood for 2 days after eating."
    medical_history = "The patient experienced vomiting of coffee-colored gastric contents (approximately 100ml) accompanied by dizziness, palpitations, and weakness after consuming hard food 2 days ago. There was no abdominal distension, pain, melena, or bloody stool, nor any confusion. The patient was treated conservatively with acid-suppressing and hemostatic medications, after which symptoms of vomiting blood improved. The patient has a history of chronic Hepatitis B for three years, which has not been treated."
    physical_examination = "Pale skin and mucous membranes, flat abdomen with no visible peristaltic waves and presence of abdominal breathing. No abdominal wall vein varicosity was observed. The abdomen was soft without fluid wave or shifting dullness, and no palpable masses. There was no significant tenderness or rebound tenderness, and the liver and spleen were not palpable below the ribs. Murphy's sign was negative. No evident kidney area tenderness or percussion pain, and no abnormal vascular pulsation in the abdomen. No significant tenderness at bilateral ureteral pressure points. Liver dullness was present, with the upper boundary at the right mid-clavicular line at the fifth intercostal space, with no shifting dullness. Bowel sounds were normal."
    all_possible_diseases, normalized_disease_to_factors, normalized_enriched_patient_facts = diagnose(chief_complaint, medical_history, physical_examination)
    all_possible_diseases,valid_diseases, normalized_enriched_patient_facts = verify(all_possible_diseases, normalized_disease_to_factors, normalized_enriched_patient_facts)
        
