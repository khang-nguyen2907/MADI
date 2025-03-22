json_text = '''{"type": "json", "schema": {"final_diagnosis": {"type": "array", "items": {"type": "object", "properties": {"possible_disease": {"type": "string", "description": "name of possible disease that the patient gets"}, "evidences": {"type": "array", "items": {"type": "object", "properties": {"symptoms": {"type": "array", "items": {"type": "string"}, "description": "Which symptoms from given patient's chief complain, medical history and physical does the diagnosis derive from?"}, "references": {"type": "array", "items": {"type": "string"}, "description": "Which medical documents of documents are provided to strengthen the decision of that diagnosis."}}}}}}, "description": "response patient's possible disease"}}}

{
  "final_diagnosis": [
    {
      "possible_disease": "Esophageal Variceal Bleeding",
      "evidences": [
        {
          "symptoms": [
            "Vomiting blood for 2 days after eating",
            "Vomiting of coffee-colored gastric contents",
            "Dizziness, palpitations, and weakness"
          ],
          "references": [
            "**Summary of Bleeding Sources in ACLF Cases**",
            "**Summary of Gastrointestinal Involvement in Hepatocellular Carcinoma (HCC)**"
          ]
        }
      ]
    },
    {
      "possible_disease": "Gastrointestinal Bleeding due to Hepatocellular Carcinoma (HCC)",
      "evidences": [
        {
          "symptoms": [
            "Vomiting blood for 2 days after eating",
            "Vomiting of coffee-colored gastric contents",
            "History of chronic Hepatitis B"
          ],
          "references": [
            "**Summary of Gastrointestinal Involvement in Hepatocellular Carcinoma (HCC)**",
            "**Summary of Bleeding Sources in ACLF Cases**"
          ]
        }
      ]
    }
  ]
}
'''