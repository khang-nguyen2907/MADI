patient_entity_json_format = {
    "type": "json",
    "schema": {
        "chief_complaint": {
            "type": "object",
            "properties": {
                "positive_factors": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Chief complaint elements *explicitly stated* as present in the provided text."
                },
                "negative_factors": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Chief complaint elements *explicitly stated* as absent in the provided text."
                }
            },
            "required": ["positive_factors", "negative_factors"]
        },
        "medical_history": {
            "type": "object",
            "properties": {
                "positive_factors": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Medical history elements *explicitly stated* as present in the provided text."
                },
                "negative_factors": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Medical history elements *explicitly stated* as absent in the provided text."
                }
            },
            "required": ["positive_factors", "negative_factors"]
        },
        "physical_examination": {
            "type": "object",
            "properties": {
                "positive_factors": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Physical examination findings *explicitly stated* as present in the provided text."
                },
                "negative_factors": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Physical examination findings *explicitly stated* as absent or negative in the provided text."
                }
            },
            "required": ["positive_factors", "negative_factors"]
        }
    }
}