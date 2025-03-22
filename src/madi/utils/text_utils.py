import re
import json

def extract_json_from_text(text):
    """
    Extract JSON from text where JSON might be formatted in various ways:
    1. Inside ```json ... ``` code blocks
    2. Inside plain ``` ... ``` code blocks
    3. Directly as JSON object within text: { ... }
    4. Multiple JSON objects where we need to find complete valid ones
    
    Returns the parsed JSON object or None if no valid JSON is found.
    """
    # Try to find JSON in ```json ... ``` format
    json_block_match = re.search(r"```json\s*([\s\S]*?)\s*```", text, re.DOTALL)
    if json_block_match:
        json_str = json_block_match.group(1).strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            print("Found ```json``` block but couldn't parse JSON")
    
    # Try to find JSON in plain ``` ... ``` format
    code_block_match = re.search(r"```\s*([\s\S]*?)\s*```", text, re.DOTALL)
    if code_block_match:
        json_str = code_block_match.group(1).strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            print("Found ``` ``` block but couldn't parse JSON")
    
    # More aggressive approach: find all possible JSON objects
    # Look for balanced pairs of curly braces
    results = []
    stack = []
    potential_start = -1
    
    for i, char in enumerate(text):
        if char == '{':
            if not stack:  # If this is the first opening brace
                potential_start = i
            stack.append('{')
        elif char == '}':
            if stack and stack[-1] == '{':
                stack.pop()
                if not stack:  # If we've closed all open braces
                    json_candidate = text[potential_start:i+1].strip()
                    try:
                        parsed = json.loads(json_candidate)
                        results.append((parsed, json_candidate))
                    except json.JSONDecodeError:
                        pass  # Not valid JSON
    
    # No valid JSON found
    if not results:
        print("No valid JSON found in text")
        return None
    
    # If there are multiple valid JSONs, prefer the one that has key data structures
    # Or just return the largest one
    if len(results) > 1:
        # First check if any has the key "final_diagnosis" or similar important fields
        for parsed, _ in results:
            if isinstance(parsed, dict) and "final_diagnosis" in parsed:
                return parsed
        
        # Otherwise, return the largest one by string length
        results.sort(key=lambda x: len(x[1]), reverse=True)
    
    return results[0][0]  # Return the parsed JSON

def get_all_medical_knowledge_findings(knowledge_dict):
    diseases = {}
    for disease in knowledge_dict["diseases"]: 
        all_findings = []
        name = ""
        for k in disease.keys(): 
            if k == "disease_name": 
                name = disease[k]
            else: 
                for pos_factor in disease[k]["positive_factors"]: 
                    all_findings.append(pos_factor)
                for neg_factor in disease[k]["negative_factors"]: 
                    all_findings.append("¬" + neg_factor)
        diseases[name] = all_findings 
    return diseases

def get_all_patient_findings(patient_data_dict): 
    patient_all_findings = []
    for k in patient_data_dict.keys(): 
        for pos_factor in patient_data_dict[k]["positive_factors"]: 
            patient_all_findings.append(pos_factor)
        for neg_factor in patient_data_dict[k]["negative_factors"]: 
            if "No" in neg_factor: 
                new_neg_factor = neg_factor.split("No ")[1]
            else: 
                new_neg_factor = neg_factor
            patient_all_findings.append("¬"+new_neg_factor)
    return patient_all_findings

def get_all_possible_diseases(final_diagnosis): 
    all_possible_diseases = []
    for disease in final_diagnosis["final_diagnosis"]: 
        all_possible_diseases.append(disease["possible_disease"])
    return all_possible_diseases

def normalize_text(text: str): 
  return text.strip().lower()

if __name__ == "__main__": 
    text = """Here is the revised final diagnosis:

```
{
  "final_diagnosis": [
    {
      "possible_disease": "Upper Gastrointestinal Bleeding (UGIB) due to Peptic Ulcer Disease",
      "evidences": [
        {
          "symptoms": [
            "Vomiting blood for 2 days after eating",
            "Vomiting of coffee-colored gastric contents"
          ],
          "references": [
            "Internet document 0: Hematemesis is a sign of internal bleeding from the upper portion of your digestive tract — the esophagus, stomach and first portion of your small intestine called the duodenum.",
            "PubMed: Peptic ulcer disease is a common cause of upper gastrointestinal bleeding, with a mortality rate of 5-10% (Source: 'Peptic Ulcer Disease' by the American Gastroenterological Association)"
          ]
        }
      ]
    },
    {
      "possible_disease": "Cirrhosis with Portal Hypertension",
      "evidences": [
        {
          "symptoms": [
            "Chronic Hepatitis B for three years",
            "Pale skin and mucous membranes"
          ],
          "references": [
            "Internet document 1: Chronic hepatitis B raises the risk of liver failure, liver cancer and serious scarring of the liver called cirrhosis.",
            "PubMed: Patients with cirrhosis are at risk of developing portal hypertension, which can lead to varices and bleeding (Source: 'Cirrhosis and Portal Hypertension' by the American Association for the Study of Liver Diseases)"
          ]
        }
      ]
    },
    {
      "possible_disease": "Variceal Bleeding",
      "evidences": [
        {
          "symptoms": [
            "Chronic Hepatitis B for three years",
            "Vomiting blood for 2 days after eating"
          ],
          "references": [
            "Internet document 1: Chronic hepatitis B raises the risk of liver failure, liver cancer and serious scarring of the liver called cirrhosis.",
            "PubMed: Variceal bleeding is a common complication of cirrhosis, with a mortality rate of 30-50% (Source: 'Variceal Bleeding' by the American Gastroenterological Association)"
          ]
        }
      ]
    }
  ]
}
```

I made the following changes:

* Added "Variceal Bleeding" as a possible diagnosis, given the patient's history of chronic Hepatitis B.
* Prioritized symptoms based on their severity and immediacy, focusing first on "Vomiting blood" and "Vomiting of coffee-colored gastric contents" when evaluating "Upper Gastrointestinal Bleeding (UGIB) due to Peptic Ulcer Disease".
* Conducted a more in-depth search of medical literature to find specific studies or guidelines that link the patient's symptoms to the proposed diagnoses.
* Ensured that all references used are from reputable sources such as PubMed or peer-reviewed journals to strengthen the reliability of the diagnosis.
* Explicitly supported the connection between "Pale skin and mucous membranes" and "Cirrhosis with Portal Hypertension" with medical literature."""

    final_diagnosis2 = '''{"type": "json", "schema": {"final_diagnosis": {"type": "array", "items": {"type": "object", "properties": {"possible_disease": {"type": "string", "description": "name of possible disease that the patient gets"}, "evidences": {"type": "array", "items": {"type": "object", "properties": {"symptoms": {"type": "array", "items": {"type": "string"}, "description": "Which symptoms from given patient's chief complain, medical history and physical does the diagnosis derive from?"}, "references": {"type": "array", "items": {"type": "string"}, "description": "Which medical documents of documents are provided to strengthen the decision of that diagnosis."}}}}}}, "description": "response patient's possible disease"}}}

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
    final_diagnosis3 = '''{"type": "json", "schema": {"final_diagnosis": {"type": "array", "items": {"type": "object", "properties": {"possible_disease": {"type": "string", "description": "name of possible disease that the patient gets"}, "evidences": {"type": "array", "items": {"type": "object", "properties": {"symptoms": {"type": "array", "items": {"type": "string"}, "description": "Which symptoms from given patient's chief complain, medical history and physical does the diagnosis derive from?"}, "references": {"type": "array", "items": {"type": "string"}, "description": "Which medical documents of documents are provided to strengthen the decision of that diagnosis."}}}}}}, "description": "response patient's possible disease"}}}
{
  "final_diagnosis": [
    {
      "possible_disease": "Portal Hypertensive Gastropathy",
      "evidences": [
        {
          "symptoms": [
            "Vomiting blood for 2 days after eating",
            "Vomiting of coffee-colored gastric contents",
            "Dizziness, palpitations, and weakness"
          ],
          "references": [
            "Liver Disease Summary",
            "PubMed: Portal Hypertensive Gastropathy in Patients with Liver Cirrhosis"
          ]
        }
      ]
    },
    {
      "possible_disease": "Decompensated Cirrhosis",
      "evidences": [
        {
          "symptoms": [
            "Pale skin and mucous membranes",
            "Flat abdomen with no visible peristaltic waves",
            "Abdominal breathing",
            "Liver dullness"
          ],
          "references": [
            "Liver Disease Summary",
            "Concise Summary: Decompensated cirrhosis secondary to chronic HBV infection"
          ]
        }
      ]
    },
    {
      "possible_disease": "Gastrointestinal Bleeding due to Portal Hypertension",
      "evidences": [
        {
          "symptoms": [
            "Vomiting blood for 2 days after eating",
            "Vomiting of coffee-colored gastric contents"
          ],
          "references": [
            "Concise Summary: Portal hypertensive colopathy (PHC), a complication of cirrhosis",
            "PubMed: Gastrointestinal Bleeding in Patients with Portal Hypertension"
          ]
        }
      ]
    }
  ]
}
    '''
    result = extract_json_from_text(final_diagnosis3)
    print(result)