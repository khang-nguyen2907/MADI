from madi.schema import InitialDiagnosis
INITIAL_DIAGNOSIS_INSTRUCTIONS_V1 = [
    """Analyze the patient's chief complaint, medical history, and physical examination to provide a professional, detailed, and comprehensive clinical diagnosis. Include a set of possible diseases and any recommended laboratory or imaging tests, if needed.""",
    """Use DuckDuckGo Search for general background information on symptoms, conditions, or medical concepts. Formulate natural language queries (e.g., "Symptoms of appendicitis"). Use this *before* PubMed for context only, not for diagnosis or treatment decisions.""",
    """Use PubMed Search to find research articles and trials on specific diagnoses and treatments. Use precise keywords (e.g., "appendicitis diagnosis CT scan"). Use PubMed for evidence-based information, not to dictate decisions.""",
    """Each possible disease *must* be supported by both: 1) Facts from the patient's information (chief complaint, medical history, physical exam), and 2) Rules derived from scientific literature (PubMed, reputable medical journals). Do *not* create or invent rules. Rules should be as specific as possible. If a rule comes from a PubMed article, the 'source' *must* be the full URL.""",
    """For *each* possible disease, there *must* be at least one fact from the patient's information and at least one rule derived from scientific literature connecting that fact (or a combination of facts) to the diagnosis.""",
    """IMPORTANT: Your response *must* be a single JSON object conforming to the predefined schema: {schema}""".format(schema=InitialDiagnosis.model_json_schema())
]

INITIAL_DIAGNOSIS_MESSAGE_V1 = """Patient Information:

Chief Complaint: {chief_complain}
Medical History: {medical_history}
Physical Examination: {physical_examination}
"""  # Removed "POSSIBLE DISEASES" here