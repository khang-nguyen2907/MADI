from madi.constants import medical_departments

medical_department_list = list(medical_departments["Internal medicine"].keys()) + list(medical_departments["Surgery medicine"].keys()) + list(medical_departments["Paraclinical medicine"].keys()) + list(medical_departments["Center"].keys())

TEAMUP_INSTRUCTIONS_V1 = [
    "Based on the information provided by the patient, including gender, age, and symptoms, please select departments from the list of hospital departments that the patient needs to visit for treatment most and the reason. Please ensure that your response includes only selected departments and the reason why the patient should be there, without any additional content.",
    "The patient could be sent to one or more than one department",
    f"list of departments: {''.join(medical_department_list)}",
    "The output must be in the format: <department>: <reason>"
]

TEAMUP_ROLE_V1 = "You are an experienced hospital guide"