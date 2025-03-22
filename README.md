# AI-Powered Clinical Diagnosis with Resolution-Based Verification

## 1. Overview

This project leverages an AI agent to assist in clinical diagnosis. The AI agent utilizes a Large Language Model (LLM) accessed via the Groq API to provide potential diagnoses based on patient information. To ensure the reliability and logical consistency of the AI's output, a Resolution-Based Inference Engine is employed to verify the generated diagnosis against a knowledge base or set of medical rules.

This project is built using Python and managed with Poetry, aiming to provide an open and extensible platform for exploring AI in healthcare.


## 2. Table of Contents

1.  [Overview](#1-overview)
2.  [Table of Contents](#2-table-of-contents)
3.  [Getting Started](#3-getting-started)
    * [3.1. Prerequisites](#31-prerequisites)
    * [3.2. Installation](#32-installation)
    * [3.3. Configuration](#33-configuration)
4.  [Usage](#4-usage)
    * [4.1. Running the Main Application](#41-running-the-main-application)
    * [4.2. Input Format](#42-input-format)
    * [4.3. Output Interpretation](#43-output-interpretation)
5.  [Technical Details](#5-technical-details)
    * [5.1. AI Agent for Diagnosis](#51-ai-agent-for-diagnosis)
    * [5.2. Resolution-Based Inference Engine](#52-resolution-based-inference-engine)
    * [5.3. PubMed Integration](#53-pubmed-integration)
    * [5.4. Self-reflection and tool use Agent ](#534self-reflection-and-tool-use-agent)
    * [5.5. Structure patient's data and medical knowledge ](#53-structure-patient's-data-and-medical-knowledge)
    * [5.6. Project Paper](#53-project-paper)
6.  [Support](#6-support)
7.  [Future Work](#7-future-work)

## 3. Getting Started

This section outlines the steps required to set up and run the project on your local machine.

### 3.1. Prerequisites

Before you begin, ensure you have the following installed:

* **Python:** Version 3.8 or higher is recommended. You can download it from [https://www.python.org/downloads/](https://www.python.org/downloads/).
* **Poetry:** A tool for dependency management and packaging in Python. Install it by following the instructions on the official website: [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation).
* **Git:** For version control and cloning the project repository (if it's hosted on a platform like GitHub). You can download it from [https://git-scm.com/downloads](https://git-scm.com/downloads).

### 3.2. Installation

1.  **Clone the Repository (Optional):** If the project code is hosted on a Git repository (e.g., GitHub, GitLab), clone it to your local machine using the following command:

    ```bash
    git clone <repository_url>
    cd <project_directory>
    ```

2.  **Install Dependencies using Poetry:** Navigate to the project directory in your terminal and run the following command to install all the necessary dependencies specified in the `pyproject.toml` file:

    ```bash
    poetry install
    ```

    This command will create a virtual environment and install all the required libraries, including those for interacting with the Groq API, handling environment variables, and potentially for the inference engine and PubMed search.

### 3.3. Configuration

This project requires you to set up environment variables to securely store sensitive information like API keys.

1.  **Obtain Groq API Key:**
    * Go to [https://groq.com/](https://groq.com/) and sign up for an account.
    * Follow the instructions on the Groq website to obtain your API key. This key will be used to authenticate your requests to the Groq LLM.

2.  **Create `.env` File:**
    * In the root directory of your project, create a new file named `.env`.

3.  **Add Environment Variables:**
    * Open the `.env` file with a text editor and add the following lines, replacing the placeholders with your actual API key and email address:

        ```dotenv
        GROQ_API_KEY=YOUR_GROQ_API_KEY
        EMAIL=YOUR_EMAIL_ADDRESS
        ```

    * **Important:** Do not commit the `.env` file to your version control system (e.g., Git) as it contains sensitive information. Ensure that your `.gitignore` file includes `.env` to prevent accidental commits.

## 4. Usage

This section describes how to run the main application and interact with it.

### 4.1. Running the Main Application

1.  **Activate the Poetry Shell:** Before running the application, activate the virtual environment managed by Poetry:

    ```bash
    poetry shell
    ```

2.  **Run the Main File:** Assuming your main application file is named `main.py`, you can run it using the following command:

    ```bash
    python src/madi/main.py
    ```

    Replace `main.py` with the actual name of your main application file if it's different.

### 4.2. Input Format

The application will likely require some form of input to represent patient information. The specific format will depend on how you've designed the application. Examples could include:

* **Command-line arguments:** The user provides information directly when running the script.
* **Text input:** The application prompts the user to enter symptoms, medical history, etc.
* **File input:** The application reads patient data from a file (e.g., CSV, JSON).

The documentation should clearly specify the expected input format and any constraints or required information. For example:

>   To provide patient information, please enter the symptoms separated by commas when prompted. For example: `fever, cough, fatigue`.

### 4.3. Output Interpretation

The application will produce an output containing the AI agent's diagnosis and the verification result from the inference engine. The documentation should explain how to interpret this output. For example:

>   The output will be displayed in the following format:
>
>   ```
>   AI Diagnosis: [Diagnosis suggested by the AI agent]
>   Verification Result: [Result of the inference engine (e.g., Verified, Not Verified, Inconclusive)]
>   Verification Details: [Optional: Further details from the inference engine, such as rules that were violated or satisfied]
>   ```
>
>   If the verification result is "Not Verified", it indicates that the inference engine found inconsistencies or contradictions in the AI's diagnosis based on the defined rules or knowledge base.

## 5. Technical Details

This section provides more in-depth information about the core components of the project.


### 5.1. AI Agent for Diagnosis

* **LLM Integration:** The project utilizes the Groq API to interact with a Large Language Model. This LLM is responsible for generating potential clinical diagnoses based on the input patient information.
* **Prompt Engineering:** The effectiveness of the AI agent heavily relies on the prompts used to query the LLM. The project likely includes specific prompt templates designed to elicit accurate and relevant diagnostic suggestions.
* **Error Handling:** The implementation should include robust error handling to manage potential issues with the Groq API, such as network errors or invalid API keys.

### 5.2. Resolution-Based Inference Engine

With negation support, our Resolution models now function more completely:

1. Model 1 (M1) with Negation:

- Original: If b and c imply a, and we have negative a, then we have negative b or negative c
- Applied: If a disease requires positive factors b,c and negative factors d,e, then:

- Disease is confirmed if (b AND c are present) AND (d AND e are absent)
- Disease is ruled out if any required factor is missing OR any excluded factor is present

2. Model 2 (M2) with Negation:

- Original: If not (b or c) and b is true, then not c
- Applied: If a disease requires either symptom b OR symptom c is absent, and b is present, then c must be absent to confirm the disease

3. Model 3 (M3) with Explicit Contradiction Detection:

- Beyond simple contradictions, we can now detect rule-based contradictions:
    - If a factor is listed as both required and excluded for the same disease
    - If a factor is required for one disease but excluded for another, yet both diseases appear likely

Resolution as a proof system, not just as a pattern matching system. This is much closer to the formal logical Resolution method. Here's how I now understand your approach:

1. An LLM suggests a possible disease diagnosis
2. You start by assuming the negation of this diagnosis (¬Disease)
3. You apply Resolution inference rules (M1, M2) to see if this leads to a contradiction
4. If you reach a contradiction (M3), then the negation is invalid, which means the original diagnosis (Disease) is valid

Applying This to Your Workflow
To apply this to your original workflow:

1. Extract patient data (symptoms, history, examination)
2. Have an LLM suggest possible diagnoses
3. For each suggested diagnosis:

    - Apply Resolution proof by contradiction
    - If a contradiction is found, the diagnosis is validated
    - Return the validated diagnoses with confidence scores



This approach properly uses Resolution as a proof system, using:

- Model 1 (M1) to derive negated factors from negated diseases
- Model 2 (M2) to resolve clauses when some literals are known to be false
- Model 3 (M3) to detect contradictions that validate the original diagnosis

Let's take a specific example to illustrate:

1. LLM Suggests: "Variceal bleeding"
2. Start with Negation: ¬(Variceal bleeding)
3. Rules for Variceal bleeding:

    - Variceal bleeding ← Cirrhosis, Hematemesis
    - Cirrhosis ← Chronic hepatitis B, Liver damage

4. Patient Data (Facts):

    - Chronic hepatitis B
    - Hematemesis
    - Vomiting blood
    - Liver damage

5. Resolution Process:

- Apply M1: From ¬(Variceal bleeding) and (Variceal bleeding ← Cirrhosis, Hematemesis), we get ¬Cirrhosis OR ¬Hematemesis
- Patient data shows Hematemesis is true, so by M2, we derive ¬Cirrhosis
- Apply M1 again: From ¬Cirrhosis and (Cirrhosis ← Chronic hepatitis B, Liver damage), we get ¬(Chronic hepatitis B) OR ¬(Liver damage)
- Patient data shows both Chronic hepatitis B and Liver damage are true
- This creates a contradiction (M3): Patient has both factors, but our resolution chain requires at least one to be false


Conclusion: Since we reached a contradiction, the initial assumption ¬(Variceal bleeding) must be false, therefore "Variceal bleeding" is validated as a correct diagnosis.
### 5.3. PubMed Integration

* **Literature Search:** The project may include functionality to search PubMed ([https://pubmed.ncbi.nlm.nih.gov/](https://pubmed.ncbi.nlm.nih.gov/)) for relevant medical literature based on the AI's diagnosis or the patient's symptoms.
* **API Usage:** This feature would likely involve using the NCBI Entrez API to programmatically query PubMed. The `EMAIL` environment variable is required by the NCBI API for identification purposes.
* **Information Retrieval:** The retrieved information from PubMed could potentially be used to further validate the AI's diagnosis or provide additional context.

### 5.4. Self-reflection and tool use Agent 
- The search agent serves as the initial information retrieval module, tasked with gathering relevant medical knowledge based on the patient's provided clinical data, which includes their chief complaint, medical history, and physical examination findings. To achieve this, the agent utilizes two external tools: PubMed search and DuckDuckGo search. PubMed is employed to retrieve scholarly medical articles and journals using specific medical terminology derived from the patient's data. DuckDuckGo search is used to access broader online information that may be necessary for a comprehensive understanding of the patient's condition.

- The search agent operates by first analyzing the patient's clinical data to identify key sub-problems and formulate appropriate search queries and terms. It then develops an initial plan outlining the efficient utilization of the available tools to retrieve the most relevant medical documents for diagnosis. To ensure the efficacy of this plan, the agent performs a self-reflection step, critically evaluating the planned tool usage and potentially regenerating the plan to optimize information retrieval. Following this reflective phase, the agent executes the search plan, accessing the PubMed API for medical literature and using the DuckDuckGo web browser for other relevant information. The retrieved medical documents are then passed on to the subsequent module.

- There are many frameworks that provide pre-built Agent architecture and we just need to import and use. However, in order to strongly control and enable customization, we built Agent from scratch. 

### 5.5. Structure patient's data and medical knowledge 
There is an LLM within the clinical diagnosis workflow plays a critical role in structuring both the original, unsynthesized medical documents retrieved by the Search Agent and the patient's clinical data in a format suitable for the Resolution-based Verifier. This involves extracting key entities from the text and categorizing them into "present" and "absent" sets.

For the patient's data (chief complaint, medical history, and physical examination), each set is further divided into "present" and "absent" subsets. If a symptom or event is explicitly mentioned by the patient as being present, it is categorized into the "present" subset. Conversely, if the patient explicitly states the absence of a symptom or condition, and this is clearly stated in the text, it is classified into the "absent" subset. These categorized entities serve as factual assertions or negations, forming the basis for logical inference within the verifier. They can be viewed as the initial hypotheses regarding the patient's condition.

Similarly, for the medical documents, the LLM extracts entities and categorizes them into "present" and "absent" sets. However, in this case, the categorization is performed for each disease, symptom, or medical subject mentioned in the document. For instance, if a medical document describes a disease, it will also list associated symptoms, conditions, and causes that are explicitly stated in the textual medical documents. These explicitly mentioned factors will then be categorized as either present or absent in relation to that specific disease, depending on how they are described in the text. For example, a document might state that a disease is characterized by fever and cough (present entities) but typically does not involve rash (absent entity). These structured representations of medical knowledge from the documents function as the rules within the verification process. This can be conceptualized as an "if...then..." rule, where a `<set_of_symptoms>` (present entities) implies a `<disease>`.

Structuring textual medical documents is seemed as building a graph, condense the key concepts and identify relationships between entity. This work supports not only Resolution-based inference verifier (Rule-based system) but also save limit rate token. 

### 5.6. Project Paper

For a more detailed explanation of the project's methodology, implementation, and results, please refer to the following technical report:

[MADI: Multi-Agent Diagnostic Intelligence technical report](https://drive.google.com/file/d/1uEniYqiiTCsaThXKsGPotnNN_vTcz772/view?usp=sharing)

## 6. Support

If you encounter any issues or have questions about the project, please:

* **Check the Issues Tracker:** Look for existing issues or create a new one on the project's repository.
* **Send an email to:** [khangnhg.ai@gmail.com](mailto:khangnhg.ai@gmail.com)


## 7. Future Work

* **Multi-agents:** Due to resource limitations and the Groq API free plan's rate limits, the development of a complex multi-agent system is currently on hold while we explore alternative solutions. Our ongoing efforts are focused on the following:

* **Medical Knowledge Acquisition:** We are actively leveraging accessible APIs like PubMed and utilizing web scraping via DuckDuckGo to gather necessary medical information. We are in the process of building a medical knowledge graph, utilizing the Unified Medical Language System (UMLS) to structure and organize medical concepts and their relationships.
* **Interactive Web Interface:** A key area of future development is a web interface to enhance user interaction. This interface will allow users to input patient information such as chief complaints, medical history, and physical examination findings. Furthermore, during the diagnosis verification process using the resolution-based inference engine, the system will be able to ask clarifying yes/no questions to the user based on required medical knowledge to confirm potential diseases. This interactive approach aims to improve the user experience and ensure more comprehensive data collection for accurate diagnosis.
