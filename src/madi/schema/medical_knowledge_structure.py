knowledge_json_format = {
    "type": "json",
    "schema": {
        "diseases": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "disease_name": {"type": "string", "description": "Name of the disease."},
                    "symptoms": {
                        "type": "object",
                        "properties": {
                            "positive_factors": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Symptoms explicitly stated as present in the text."
                            },
                            "negative_factors": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Symptoms explicitly stated as absent in the text."
                            }
                        },
                        "required": ["positive_factors", "negative_factors"]
                    },
                    "causes": {
                        "type": "object",
                        "properties": {
                            "positive_factors": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Causes explicitly stated as present in the text."
                            },
                            "negative_factors": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Causes explicitly stated as absent in the text."
                            }
                        },
                        "required": ["positive_factors", "negative_factors"]
                    },
                    "conditions": {
                        "type": "object",
                        "properties": {
                            "positive_factors": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Conditions explicitly stated as present in the text."
                            },
                            "negative_factors": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Conditions explicitly stated as absent in the text."
                            }
                        },
                        "required": ["positive_factors", "negative_factors"]
                    }
                },
                "required": ["disease_name", "symptoms", "causes", "conditions"]
            },
            "description": "Array of diseases mentioned in the medical knowledge."
        }
    }
}
