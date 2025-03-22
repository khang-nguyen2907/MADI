search_agent_json_format = {
    "type": "json",
    "schema": {
        "requires_tools": {
            "type": "boolean",
            "description": "whether tools are needed for this query"
        },
        "direct_response": {
            "type": "string",
            "description": "response when no tools are needed",
            "optional": True
        },
        "thought": {
            "type": "string",
            "description": "reasoning about how to solve the task (when tools are needed)",
            "optional": True
        },
        "plan": {
            "type": "array",
            "items": {"type": "string"},
            "description": "steps to solve the task (when tools are needed)",
            "optional": True
        },
        "tool_calls": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "tool": {
                        "type": "string",
                        "description": "name of the tool"
                    },
                    "args": {
                        "type": "object",
                        "description": "parameters for the tool"
                    }
                }
            },
            "description": "tools to call in sequence (when tools are needed)",
            "optional": True
        }
    },
    "examples": [
        {
            "query": "Convert 100 USD to EUR",
            "response": {
                "requires_tools": True,
                "thought": "I need to use the currency conversion tool to convert USD to EUR",
                "plan": [
                    "Use convert_currency tool to convert 100 USD to EUR",
                    "Return the conversion result"
                ],
                "tool_calls": [
                    {
                        "tool": "convert_currency",
                        "args": {
                            "amount": 100,
                            "from_currency": "USD",
                            "to_currency": "EUR"
                        }
                    }
                ]
            }
        },
        {
            "query": "What's 500 Japanese Yen in British Pounds?",
            "response": {
                "requires_tools": True,
                "thought": "I need to convert JPY to GBP using the currency converter",
                "plan": [
                    "Use convert_currency tool to convert 500 JPY to GBP",
                    "Return the conversion result"
                ],
                "tool_calls": [
                    {
                        "tool": "convert_currency",
                        "args": {
                            "amount": 500,
                            "from_currency": "JPY",
                            "to_currency": "GBP"
                        }
                    }
                ]
            }
        },
        {
            "query": "What currency does Japan use?",
            "response": {
                "requires_tools": False,
                "direct_response": "Japan uses the Japanese Yen (JPY) as its official currency. This is common knowledge that doesn't require using the currency conversion tool."
            }
        }
    ]
}

clinician_agent_json_format = {
    "type": "json",
    "schema": {
        "requires_more_docs": {
            "type": "boolean",
            "description": "Whether additional medical documents are required to diagnose more correctly"
        },
        "direct_response": {
            "type": "array",
            'items': {
                "type": "object", 
                "properties": {
                    "possible_disease": {
                        "type": "string", 
                        "description": "name of possible disease that the patient gets"
                    }, 
                    "evidences": {
                        "type": "array", 
                        "items": {
                            "type": "object", 
                            "properties": {
                                "symptoms": {
                                    "type": "array", 
                                    "items": {"type": "string"}, 
                                    "description": "Which symptoms from given patient's chief complain, medical history and physical does the diagnosis derive from?"
                                }, 
                                "references": {
                                    "type": "array", 
                                    "items": {"type": "string"}, 
                                    "description":"Which medical documents of documents are provided to strengthen the decision of that diagnosis."
                                }
                            }
                        }
                    }
                }
            },
            "description": "response patient's possible disease when given medical documents are sufficient to diagnose.",
            "optional": True
        },
        "thought": {
            "type": "string",
            "description": "reasoning step by step how to make correct diagnosis. Which information or knowledge are required to diagnose (when additional medical documents are needed)",
            "optional": True
        },
        "plan": {
            "type": "array",
            "items": {"type": "string"},
            "description": "when additional medical documents are needed, which would search terms or queries be established?",
            "optional": True
        }
    },
    "examples": [
        {
            "message": (
                "Chief complaint: I am feeling very tired all the time. My skin looks pale, and I have gained weight without changing my diet.\n"
                "Medical History: I had an upper respiratory infection about two weeks ago.\n"
                "Physical Examination: Pale skin noted. General fatigue noted.\n"
                "Medical documents: Medical Journal: Fatigue and pale skin can be symptoms of anemia. Fatigue and weight gain can be symptoms of hypothyroidism."
            ), 
            "response": {
                "requires_more_docs": True, 
                "thought":  "The patient's symptoms can be found in multiple diseases, and more testing is required to find the correct one.", 
                "plan": [
                    "Complete blood count (CBC) with differential",
                    "Thyroid function tests (TSH, T3, T4)",
                    "Iron studies (serum iron, ferritin, TIBC)"
                ]
            }
        }, 
        {
            "message": (
                "Chief complaint: I've been feeling incredibly tired lately, and I've lost some weight without trying. I also have some mild abdominal discomfort.\n"
                "Medical History: No known chronic illnesses.\n"
                "Physical Examination: General fatigue noted. Abdomen: mild tenderness upon palpation.\n"
                "Medical documents: Medical Textbook Excerpt: Unexplained weight loss, fatigue, and abdominal discomfort can be indicative of various systemic diseases, including but not limited to, gastrointestinal malignancies, endocrine disorders, and chronic infections. Further investigation is warranted."
            ), 
            "response": {
                "requires_more_docs": True, 
                "thought": "The patient's symptoms are non-specific and consistent with a range of potential conditions, as described in medical textbooks. Further testing is needed to differentiate between these possibilities.", 
                "plan": [
                    "Complete blood count (CBC)",
                    "Comprehensive metabolic panel (CMP)",
                    "Abdominal ultrasound",
                    "Review patient's medication list for potential side effects"
                ], 
            
            }
        }, 
        {
            "message": (
                "Chief complaint: I've had a persistent cough for the past week, along with a mild fever and some chest congestion. I've also been wheezing a bit.\n"
                "Medical History: I had an upper respiratory infection about two weeks ago.\n"
                "Physical Examination: Auscultation reveals wheezing in the lungs. Temperature: 100.4°F (38°C).\n"
                "Medical documents: Journal Article Snippet: Acute bronchitis often follows a viral upper respiratory infection. Common symptoms include persistent cough, wheezing, and low-grade fever."
            ), 
            "response": {
                "requires_more_docs": False, 
                "direct_response": [
                    {
                        "possible_disease": "Acute Bronchitis", 
                        "evidences": [
                            {
                                "symptoms": ["a persistent cough", "a mild fever", "chest congestion", "wheezing"],
                                "references": ["Journal Article Snippet: Acute bronchitis often follows a viral upper respiratory infection. Common symptoms include persistent cough, wheezing, and low-grade fever."]
                            }
                        ]
                    }
                ]
            
            }
        }, 

    ]
}

final_diagnosis_format = {
    "type": "json", 
    "schema": {
        "final_diagnosis": {
            "type": "array",
            'items': {
                "type": "object", 
                "properties": {
                    "possible_disease": {
                        "type": "string", 
                        "description": "name of possible disease that the patient gets"
                    }, 
                    "evidences": {
                        "type": "array", 
                        "items": {
                            "type": "object", 
                            "properties": {
                                "symptoms": {
                                    "type": "array", 
                                    "items": {"type": "string"}, 
                                    "description": "Which symptoms from given patient's chief complain, medical history and physical does the diagnosis derive from?"
                                }, 
                                "references": {
                                    "type": "array", 
                                    "items": {"type": "string"}, 
                                    "description":"Which medical documents of documents are provided to strengthen the decision of that diagnosis."
                                }
                            }
                        }
                    }
                }
            },
            "description": "response patient's possible disease",
       }
    }
}
# TODO: add examples for final_diagnosis_format