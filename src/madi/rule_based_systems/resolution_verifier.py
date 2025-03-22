from typing import List, Set, Dict, Tuple, Any, Optional

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from madi.handlers import Log
from madi.utils import normalize_text

logger = Log(__name__)

class ResolutionBasedVerifier: 
    def __init__(
        self, 
        sentence_transformer_model_name: str = 'all-MiniLM-L6-v2', 
        semantic_threshold: float = 0.7
    ):
        self.model = SentenceTransformer(sentence_transformer_model_name,device="cpu")
        self.semantic_threshold = semantic_threshold

    # Function to find semantic matches
    def find_semantic_matches(self, search_term, lookup_list):
        matches = {}

        # Compute embeddings
        json_embeddings = self.model.encode(lookup_list, convert_to_tensor=False)
        extra_embeddings = self.model.encode([search_term], convert_to_tensor=False)

        # Compute cosine similarity
        similarity_matrix = cosine_similarity(extra_embeddings, json_embeddings)

        for i, score in enumerate(similarity_matrix[0]):
            if score >= self.semantic_threshold:
                matches[lookup_list[i]] = score

        return matches
    

    def enrich_patient_facts(self, disease_factors, patient_facts): 
        enriched_facts = []
        enriched_facts.extend(patient_facts)
        for factor in disease_factors: 
            matches = self.find_semantic_matches(factor, patient_facts)
            if matches: 
                enriched_facts.append(factor)
        return enriched_facts

    def validate_diagnosis_by_resolution(
        self,
        diagnosis: str,
        disease_to_factors,
        patient_facts,
        interactive=True,
        max_iterations=100,
        visited_diseases=None  # Track visited diseases to prevent infinite recursion
    ):
        """
        Validate a diagnosis using Resolution proof by contradiction,
        with recursive validation of disease-factors and cycle detection
        """
        # Initialize visited_diseases if None
        if visited_diseases is None:
            visited_diseases = set()

        # Add current diagnosis to visited set to prevent cycles
        visited_diseases.add(diagnosis)

        # Convert patient_facts to a set for faster lookups
        patient_facts_set = set(patient_facts)

        # Normalize patient facts to handle negations consistently
        positive_facts = set()
        negative_facts = set()
        for fact in patient_facts_set:
            if fact.startswith("¬"):
                negative_facts.add(fact[1:])  # Store the positive form in negative_facts
            else:
                positive_facts.add(fact)

        # Start by assuming negation of the diagnosis
        current_clauses = [f"¬{diagnosis}"]
        reasoning = [f"Starting with negation: ¬{diagnosis}"]

        # Create a copy of patient facts that we might update
        updated_patient_facts = list(patient_facts_set)

        # Track missing factors that might need to be queried
        missing_factors = set()
        missing_disease_factors = set()  # Track factors that are also diseases

        # Keep track of all derived clauses to prevent redundant work
        all_clauses = set(current_clauses)

        # Resolution loop
        iteration = 0
        clauses_to_process = current_clauses.copy()
        processed_clauses = set()

        while iteration < max_iterations and clauses_to_process:
            iteration += 1
            new_clauses = []

            # Get the next clause to process
            if not clauses_to_process:
                break
            clause = clauses_to_process.pop(0)

            # Skip if we've already processed this clause
            if clause in processed_clauses:
                continue

            processed_clauses.add(clause)

            # Case 1: Simple negated disease (e.g., "¬Peptic ulcers")
            if clause.startswith("¬") and " OR " not in clause:
                disease_name = clause[1:]
                if disease_name in disease_to_factors:
                    # Apply M1: If ¬A and (A ← B,C), then ¬B OR ¬C
                    factors = disease_to_factors[disease_name]

                    # Check if any required factor is already known to be false
                    contradiction_found = False
                    for factor in factors:
                        if factor in negative_facts:
                            reasoning.append(f"Required factor '{factor}' is known to be false, so diagnosis '{disease_name}' cannot be valid")
                            contradiction_found = True
                            break

                    if contradiction_found:
                        # We found a direct contradiction - the diagnosis is actually invalid
                        # which means our starting assumption (¬diagnosis) is actually true
                        reasoning.append(f"Found contradiction: diagnosis {diagnosis} is not valid")
                        return False, reasoning, updated_patient_facts

                    # Continue with normal resolution
                    negated_factors = [f"¬{factor}" for factor in factors]
                    new_clause = " OR ".join(negated_factors)

                    # Only add if it's a new clause
                    if new_clause not in all_clauses:
                        new_clauses.append(new_clause)
                        all_clauses.add(new_clause)
                        reasoning.append(f"Applied M1: From {clause} and rule ({disease_name} ← {', '.join(factors)}), derived {new_clause}")

                    # Check if any factors are missing from patient facts
                    for factor in factors:
                        if factor not in positive_facts and factor not in negative_facts:
                            # Check if this factor is itself a disease
                            if factor in disease_to_factors and factor not in visited_diseases:
                                missing_disease_factors.add(factor)
                                reasoning.append(f"Factor '{factor}' is also a disease - will try to prove recursively")
                            else:
                                missing_factors.add(factor)

            # Case 2: Disjunction of literals (e.g., "¬Cirrhosis OR ¬Hematemesis")
            elif " OR " in clause:
                literals = clause.split(" OR ")

                # Apply M2: Resolution with patient facts
                simplified_literals = []
                for literal in literals:
                    if literal.startswith("¬"):
                        term = literal[1:]
                        if term in positive_facts:
                            # The term is positive in our facts, so this literal is false
                            continue
                        elif term in negative_facts:
                            # The term is negative in our facts, so this literal is true
                            # The entire clause is satisfied
                            reasoning.append(f"Applied M2: Clause {clause} is satisfied because {term} is known to be false")
                            simplified_literals = []  # Clear the list as we don't need a new clause
                            break
                        else:
                            # We don't know about this term
                            simplified_literals.append(literal)
                            # Check if this is a disease
                            if term in disease_to_factors and term not in visited_diseases:
                                missing_disease_factors.add(term)
                            else:
                                missing_factors.add(term)
                    else:
                        # This is a positive literal
                        if literal in positive_facts:
                            # The literal is positive in our facts, so it's true
                            # The entire clause is satisfied
                            reasoning.append(f"Applied M2: Clause {clause} is satisfied because {literal} is known to be true")
                            simplified_literals = []  # Clear the list as we don't need a new clause
                            break
                        elif literal in negative_facts:
                            # The literal is negative in our facts, so it's false
                            # We can remove it from this clause
                            continue
                        else:
                            # We don't know about this literal
                            simplified_literals.append(literal)
                            # Check if this is a disease
                            if literal in disease_to_factors and literal not in visited_diseases:
                                missing_disease_factors.add(literal)
                            else:
                                missing_factors.add(literal)

                # If we have simplified literals, create a new clause
                if simplified_literals and len(simplified_literals) < len(literals):
                    new_simplified_clause = " OR ".join(simplified_literals)
                    if new_simplified_clause not in all_clauses:
                        new_clauses.append(new_simplified_clause)
                        all_clauses.add(new_simplified_clause)
                        reasoning.append(f"Applied M2: Simplified {clause} to {new_simplified_clause} using patient facts")

                # Check if we've derived an empty clause (contradiction)
                if len(simplified_literals) == 0 and len(literals) > 0:
                    reasoning.append("Applied M2: Derived empty clause (contradiction) - diagnosis confirmed")
                    return True, reasoning, updated_patient_facts

                # Apply M3: Unit resolution for single literals
                if len(simplified_literals) == 1:
                    unit_literal = simplified_literals[0]
                    reasoning.append(f"Applied M3: Found unit clause {unit_literal}")

                    # If we have a unit negation, potentially expand it
                    if unit_literal.startswith("¬"):
                        disease_name = unit_literal[1:]
                        if disease_name in disease_to_factors and disease_name not in visited_diseases:
                            # Handle nested disease definitions
                            factors = disease_to_factors[disease_name]
                            negated_factors = [f"¬{factor}" for factor in factors]
                            new_clause = " OR ".join(negated_factors)
                            if new_clause not in all_clauses:
                                new_clauses.append(new_clause)
                                all_clauses.add(new_clause)
                                reasoning.append(f"Applied M3: From unit clause {unit_literal}, derived {new_clause}")

            # Case 3: Unit positive clause (should be a fact)
            elif not clause.startswith("¬") and " OR " not in clause:
                if clause in negative_facts:
                    # This contradicts our known facts - we've reached a contradiction
                    reasoning.append(f"Contradiction: {clause} must be true for diagnosis, but patient fact says it's false")
                    # This means our starting assumption (¬diagnosis) leads to a contradiction
                    # So the diagnosis is valid
                    return True, reasoning, updated_patient_facts
                elif clause not in positive_facts:
                    # This is a necessary factor that's missing
                    # Check if this factor is itself a disease
                    if clause in disease_to_factors and clause not in visited_diseases:
                        missing_disease_factors.add(clause)
                        reasoning.append(f"Factor '{clause}' is also a disease - will try to prove recursively")
                    else:
                        missing_factors.add(clause)
                        reasoning.append(f"Missing information: {clause} should be true but not in patient facts")

            # Add new clauses to process queue
            for new_clause in new_clauses:
                if new_clause and new_clause not in processed_clauses:
                    clauses_to_process.append(new_clause)

        # First, try to recursively validate disease-factors
        if missing_disease_factors and len(visited_diseases) < len(disease_to_factors):
            reasoning.append(f"Attempting to recursively validate disease-factors: {', '.join(missing_disease_factors)}")

            # Track if we found any disease factors
            recursively_validated = []

            for disease_factor in missing_disease_factors:
                if disease_factor in visited_diseases:
                    continue

                reasoning.append(f"Recursively validating '{disease_factor}'")

                # Try to validate this disease-factor
                sub_valid, sub_reasoning, sub_facts = self.validate_diagnosis_by_resolution(
                    disease_factor, disease_to_factors, updated_patient_facts,
                    interactive=False, max_iterations=max_iterations//2,
                    visited_diseases=visited_diseases.copy()
                )

                # Add the reasoning from the recursive call
                for step in sub_reasoning:
                    reasoning.append(f"  Recursive: {step}")

                if sub_valid:
                    reasoning.append(f"Successfully validated '{disease_factor}' recursively")
                    recursively_validated.append(disease_factor)
                    # Add this as a known fact
                    if disease_factor not in updated_patient_facts:
                        updated_patient_facts.append(disease_factor)
                else:
                    reasoning.append(f"Could not validate '{disease_factor}' recursively")

            # If we recursively validated any diseases, retry the main validation
            if recursively_validated:
                reasoning.append(f"Restarting main validation with recursively validated diseases: {', '.join(recursively_validated)}")
                return self.validate_diagnosis_by_resolution(
                    diagnosis, disease_to_factors, updated_patient_facts,
                    interactive=interactive, max_iterations=max_iterations,
                    visited_diseases=visited_diseases
                )

        # If we have missing factors and interactive mode is on, ask the patient
        if missing_factors and interactive:
            reasoning.append(f"Missing information detected: {', '.join(missing_factors)}")

            # Query patient for missing factors, including disease-factors we couldn't validate
            all_missing = set(missing_factors)
            for disease_factor in missing_disease_factors:
                if disease_factor not in visited_diseases and disease_factor not in updated_patient_facts:
                    all_missing.add(disease_factor)

            updated_facts = self.query_patient_for_missing_factors(all_missing, updated_patient_facts)

            # If we got new information, try validation again with updated facts
            if set(updated_facts) != set(updated_patient_facts):
                reasoning.append("Restarting validation with new patient information")
                # Important - pass the complete set of updated facts to the recursive call
                new_result, new_reasoning, newest_facts = self.validate_diagnosis_by_resolution(
                    diagnosis, disease_to_factors, updated_facts,
                    interactive=False, max_iterations=max_iterations//2,
                    visited_diseases=visited_diseases
                )
                reasoning.extend(new_reasoning)
                return new_result, reasoning, newest_facts

        # If we get here without finding a contradiction, diagnosis is not validated
        reasoning.append("No contradiction found - diagnosis not confirmed")
        return False, reasoning, updated_patient_facts

    def query_patient_for_missing_factors(self, missing_factors, patient_facts):
        """
        Ask patient about missing factors needed for diagnosis

        Args:
            missing_factors: Set of factors to ask about
            patient_facts: Current patient facts

        Returns:
            Updated patient facts
        """
        updated_facts = patient_facts.copy()
        patient_facts_set = set(patient_facts)

        print("\n--- Additional Information Needed ---")
        print("Please answer yes or no to the following questions:")

        for factor in missing_factors:
            # Skip factors that are already known (positive or negative)
            if factor in patient_facts_set or f"¬{factor}" in patient_facts_set:
                continue

            response = input(f"Do you have '{factor}'? (yes/no): ").strip().lower()
            if response in ["yes", "y", "true"]:
                updated_facts.append(factor)
                print(f"Added '{factor}' to patient facts")
            elif response in ["no", "n", "false"]:
                updated_facts.append(f"¬{factor}")
                print(f"Added '¬{factor}' (absence of {factor}) to patient facts")
            else:
                print(f"Unclear response for '{factor}', skipping this factor")

        return updated_facts


    # Example usage with LLM integration:
    def validate_with_llm(self, diagnosis, disease_to_factors, patient_facts, llm_function):
        """
        Wrapper function that uses LLM to answer patient queries

        Args:
            diagnosis: The disease to validate
            disease_to_factors: Knowledge base of disease-factor relationships
            patient_facts: Known patient facts
            llm_function: Function to call LLM API

        Returns:
            Validation result, reasoning, and updated facts
        """
        # First pass - identify missing information
        is_valid, reasoning, updated_facts = validate_diagnosis_by_resolution(
            diagnosis, disease_to_factors, patient_facts, interactive=False
        )

        # Extract missing factors from reasoning
        missing_factors = set()
        for step in reasoning:
            if "Missing information:" in step:
                factor = step.split("Missing information: ")[1].split(" should be true")[0]
                missing_factors.add(factor)
            elif "Missing information detected:" in step:
                factors = step.split("Missing information detected: ")[1].split(", ")
                missing_factors.update(factors)

        # If we have missing factors, query the LLM
        if missing_factors:
            print(f"Found {len(missing_factors)} missing factors: {missing_factors}")

            # Format all questions in a single prompt
            questions = "\n".join([f"- Do you have '{factor}'? (Please answer yes or no)" for factor in missing_factors])

            prompt = f"""
            I need to confirm a few symptoms to help with your diagnosis.
            Please answer each question with a clear yes or no:

            {questions}
            """

            # Call the LLM
            print("Asking LLM for missing information...")
            llm_response = llm_function(prompt)
            print(f"LLM response: {llm_response}")

            # Process response and update patient facts
            for factor in missing_factors:
                factor_lower = factor.lower()
                response_lines = llm_response.lower().split("\n")

                for line in response_lines:
                    if factor_lower in line:
                        if "yes" in line:
                            updated_facts.append(factor)
                            print(f"Added '{factor}' to patient facts")
                            break
                        elif "no" in line:
                            updated_facts.append(f"¬{factor}")
                            print(f"Added '¬{factor}' (absence of {factor}) to patient facts")
                            break

            # Run validation again with updated facts
            print("Running validation with updated facts...")
            is_valid, reasoning, newest_facts = validate_diagnosis_by_resolution(
                diagnosis, disease_to_factors, updated_facts, interactive=False
            )

        return is_valid, reasoning, updated_facts



if __name__ == "__main__": 
    # verifier = ResolutionBasedVerifier()
    # patient_facts = ['Vomiting blood for 2 days after eating', 'Vomiting of coffee-colored gastric contents', 'Dizziness', 'Palpitations', 'Weakness', 'Chronic Hepatitis B for three years', '¬abdominal distension', '¬abdominal pain', '¬melena', '¬bloody stool', '¬confusion', 'Pale skin and mucous membranes', 'Abdominal breathing', 'Soft abdomen', 'Liver dullness', 'Normal bowel sounds', '¬visible peristaltic waves', '¬abdominal wall vein varicosity', '¬fluid wave or shifting dullness', '¬palpable masses', '¬significant tenderness or rebound tenderness', '¬Liver and spleen not palpable below the ribs', "¬Murphy's sign negative", '¬evident kidney area tenderness or percussion pain', '¬abnormal vascular pulsation in the abdomen', '¬significant tenderness at bilateral ureteral pressure points', '¬shifting dullness']
    # disease_factors = ['Gastroesophageal varices (GEV) bleeding', "Size discrepancy between the donor liver and recipient's abdominal cavity", 'Adult liver transplantation (LT)']
    # enriched = verifier.enrich_patient_facts(disease_factors, patient_facts)
    # logger.info("Enriched patient factors", enriched)

    verifier = ResolutionBasedVerifier()
    disease_to_factors = {'Peptic ulcers': ['vomiting bright red blood', 'vomit resembling coffee grounds', 'abdominal pain or discomfort', 'weakness', 'dizziness', 'peptic ulcers', 'esophageal varices'], 'Esophageal varices': ['vomiting bright red blood', 'vomit resembling coffee grounds', 'abdominal pain or discomfort', 'weakness', 'dizziness', 'peptic ulcers', 'esophageal varices'], 'Duodenal Ulcer': ['Massive hematemesis', 'Gastrointestinal tract hemorrhage', 'Penetrating duodenal ulcer', 'Ruptured pseudoaneurysm of the hepatic artery', 'Liver transplantation', 'Ischemic cholangitis'], 'Ischemic Cholangitis': ['Ischemia of the grafted liver', 'Percutaneous transhepatic cholangial drainage']}
    patient_facts = ['Vomiting blood', 'Symptoms occurred after eating', 'Vomiting of coffee-colored gastric contents', 'Dizziness', 'Palpitations', 'Weakness', 'Chronic Hepatitis B', '¬abdominal distension', '¬abdominal pain', '¬melena', '¬bloody stool', '¬confusion', 'Pale skin and mucous membranes', 'Abdominal breathing', 'Liver dullness', 'Normal bowel sounds', '¬visible peristaltic waves', '¬abdominal wall vein varicosity', '¬fluid wave or shifting dullness', '¬palpable masses', '¬significant tenderness or rebound tenderness', '¬Liver and spleen not palpable below the ribs', "¬Murphy's sign negative", '¬kidney area tenderness or percussion pain', '¬abnormal vascular pulsation in the abdomen', '¬significant tenderness at bilateral ureteral pressure points', '¬shifting dullness', 'vomiting bright red blood', 'vomit resembling coffee grounds', 'weakness', 'dizziness', 'vomiting bright red blood', 'vomit resembling coffee grounds', 'weakness', 'dizziness']
    normalized_patient_facts = []
    for fact in patient_facts:
        normalized_patient_facts.append(normalize_text(fact))
    
    normalized_disease_factors = {}
    for k, v in disease_to_factors.items():
        normalized_values = []
        for va in v:
            normalized_values.append(normalize_text(va))
        norm_k = normalize_text(k)
        normalized_disease_factors[norm_k] = normalized_values
    
    diagnosis = "peptic ulcers"
    is_valid, reasoning, updated_facts = verifier.validate_diagnosis_by_resolution(
            diagnosis, normalized_disease_factors, normalized_patient_facts, interactive=True
        )
