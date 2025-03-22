import json 
from madi.schema import patient_entity_json_format

ENTITY_MESSAGE = """Given patient's chief complaint, medical history, and physical examination, extract relevant entities and categorize them into positive and negative factors.

**Crucially, only extract information that is explicitly stated in the provided text.** Do not infer or hallucinate any information that is not directly mentioned.

- **Positive factors** are those that are explicitly stated as present or observed *in the given text*.
- **Negative factors** are those that are explicitly stated as absent or not observed *in the given text* (e.g., "no abdominal pain," "Murphy's sign negative").

Your response must be strictly based on the provided text and must follow the schema: {json_format}

Chief complaint: {chief_complaint}
Medical history: {medical_history}
Physical examination: {physical_examination}"""

ENTITY_ROLE = "you are a Medical entity extractor, only extract explicitly stated information."