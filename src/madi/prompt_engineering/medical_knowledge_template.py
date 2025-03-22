import json 
from madi.schema import knowledge_json_format

KNOWLEDGE_MESSAGE = """
Given the following medical knowledge, extract the diseases mentioned and their associated symptoms, causes, and conditions.

**Crucially, only extract information that is explicitly stated in the provided text.** Do not infer or hallucinate any information that is not directly mentioned.

- **Positive factors** are those that are explicitly stated as present or observed *in the given text*.
- **Negative factors** are those that are explicitly stated as absent or not observed *in the given text* (e.g., "absence of chronic pancreatitis features").

Your response must be strictly based on the provided text and must follow the schema: {json_format}

Medical Knowledge: {medical_knowledge}"""

KNOWLEDGE_ROLE = "you are a Medical knowledge extractor, only extract explicitly stated information."