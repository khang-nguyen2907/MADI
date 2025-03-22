from typing import (
    Callable,
    Any,
    Dict,
    get_type_hints,
    Optional,
    List
)
from datetime import datetime

from dataclasses import dataclass
import inspect
from typing import _GenericAlias
import urllib.request
import json
from groq import Groq
import os
from madi.prompt_engineering import (
    DEFAULT_SYSTEM_ROLE, 
    DEFAULT_SYSTEM_INSTRUCTIONS, 
    DEFAULT_SYSTEM_CAPABILITIES, 
    SEARCH_ENGINE_AGENT_ROLE, 
    SEARCH_ENGINE_AGENT_INSTRUCTIONS, 
    SEARCH_ENGINE_AGENT_CAPABILITIES
)
from madi.schema import (
    Tool, 
    Interaction, 
    search_agent_json_format
)
from madi.schema import (
    PubmedSearchResult, 
    DDuckGoSearchResult
)
from madi.tools import duckgo_search, search_pubmed
from madi.constants import ENV_VAR
from madi.llm import generate_response
from madi.utils import load_default_config
from madi.handlers import Log

logger = Log(__name__)
configs = load_default_config()

class SearchAgent:
    def __init__(
        self,
        llm: Groq,
        role: str = DEFAULT_SYSTEM_ROLE,
        instructions: List[str] = DEFAULT_SYSTEM_INSTRUCTIONS,
        capabilities: List[str] = DEFAULT_SYSTEM_CAPABILITIES, 
        max_retries: int = 3
    ):
        self.client = llm
        self.tools: Dict[str, Tool] = {}
        self.interactions: List[Interaction] = [] #working memory
        self.role = role
        self.instructions = instructions
        self.capabilities = capabilities
        self.max_retries = max_retries

    def add_tool(self, tool: Tool) -> None:
        """Register a new tool with the agent"""
        self.tools[tool.name] = tool
        logger.title(f"{tool.name} tool added succesfully")

    def get_available_tools(self) -> List[str]:
        """Get list of available tool descriptions"""
        return [
            f"{tool.name}: {tool.description}" for tool in self.tools.values()
        ]

    def use_tool(self, tool_name: str, **kwargs: Any) -> str:
        """Execute a specific tool with given arguments."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}")
        tool = self.tools[tool_name]
        return tool.func(**kwargs)

    def create_system_prompt(self) -> str:
        """Create the system prompt for the LLM with available tools"""
        tools_json = {
            "role": self.role,
            "capabilities": self.capabilities,
            "instructions": self.instructions,
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        name: {
                            "type": info["type"],
                            "description": info["description"]
                        }
                        for name, info in tool.parameters.items()
                    }
                }
                for tool in self.tools.values()
            ],
            "response_format": search_agent_json_format
        }

        return f"""You are an AI assistant that helps users by providing direct answers or using tools when necessary.
Configuration, instructions, and available tools are provided in JSON format below:

{json.dumps(tools_json, indent=2)}

Always respond with a JSON object following the response_format schema above.
Remember to use tools only when they are actually needed for the task."""
    def init_plan(self, user_query: str) -> Dict:
        logger.title("Initial plan is created")
        """Use LLM to create a plan for tool usage"""
        messages = [
            {"role": "system", "content": self.create_system_prompt()},
            {"role": "user", "content": user_query}
        ]
        
        plan = generate_response(
            client=self.client, 
            messages=messages, 
            model=configs["madi_configs"]["llm"]["default_model_name"], 
            service=configs["madi_configs"]['llm_service'],
            temperature=configs["madi_configs"]["gen_config"]["temperature"], 
            max_completion_tokens=configs["madi_configs"]["gen_config"]["max_completion_tokens"], 
            top_p=configs["madi_configs"]["gen_config"]["top_p"], 
            stop=configs["madi_configs"]["gen_config"]["stop"],
            stream=configs["madi_configs"]["gen_config"]["stream"],
            max_retries=self.max_retries,
            parse_json=True
        )
        logger.info("INITIAL PLAN", plan)
        try:
            interaction = Interaction(
                timestamp=datetime.now(),
                query=user_query,
                plan=plan
            )
            logger.title("Plan is saved to short memory")
            self.interactions.append(interaction)
        except Exception as e: 
            logger.error("Failed save to short memory", e)
        
        return plan
       

    def reflect_on_plan(self) -> Dict[str, Any]:
        """Reflect on the most recent plan using interaction history"""
        logger.title("Start to reflect the plan")
        if not self.interactions:
            return {
                "reflection": "No plan to reflect on",
                "requires_changes": False
            }

        latest_interaction = self.interactions[-1]
        reflection_prompt = {
            "task": "reflection",
            "context": {
                "user_query": latest_interaction.query,
                "generated_plan": latest_interaction.plan
            },
            "instructions": [
                "Review the generated plan for potential improvements",
                "Consider if the chosen tools are appropriate",
                "Verify tool parameters are correct",
                "Check if the plan is efficient",
                "Determine if tools are actually needed"
            ],
            "response_format": {
                "type": "json",
                "schema": {
                    "requires_changes": {
                        "type": "boolean",
                        "description": "whether the plan needs modifications"
                    },
                    "reflection": {
                        "type": "string",
                        "description": "explanation of what changes are needed or why no changes are needed"
                    },
                    "suggestions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "specific suggestions for improvements",
                        "optional": True
                    }
                }
            }
        }

        messages = [
            {
                "role": "system",
                "content": self.create_system_prompt()
            },
            {
                "role": "user",
                "content": json.dumps(reflection_prompt, indent=2)
            }
        ]

        reflection = generate_response(
            client=self.client, 
            messages=messages, 
            model=configs["madi_configs"]["llm"]["default_model_name"], 
            service=configs["madi_configs"]['llm_service'],
            temperature=configs["madi_configs"]["gen_config"]["temperature"], 
            max_completion_tokens=configs["madi_configs"]["gen_config"]["max_completion_tokens"], 
            top_p=configs["madi_configs"]["gen_config"]["top_p"], 
            stop=configs["madi_configs"]["gen_config"]["stop"],
            stream=configs["madi_configs"]["gen_config"]["stream"],
            max_retries=self.max_retries,
            parse_json=True
        )
        logger.info("REFLECTION", reflection)
        return reflection

    def plan(self, user_query: str) -> str:
        """Execute the full pipeline: plan, reflect and potential replan"""
        try:
            logger.title("Start to plan")
            # Create initial plan (this also stores it in memory)
            initial_plan = self.init_plan(user_query)

            # Reflect on the plan using memory
            reflection = self.reflect_on_plan()

            # checl if reflection suggests changes
            if reflection.get("requires_changes", False):
                logger.title("Changing plan is required")
                # Generate new plan based on reflection
                messages = [
                    {"role": "system", "content": self.create_system_prompt()},
                    {"role": "user", "content": user_query},
                    {"role": "system", "content": json.dumps(initial_plan)},
                    {"role": "user", "content": f"Please revise the plan based on this feedback: {reflection}"}
                ]
                final_plan = generate_response(
                    client=self.client, 
                    messages=messages, 
                    model=configs["madi_configs"]["llm"]["default_model_name"], 
                    service=configs["madi_configs"]['llm_service'],
                    temperature=configs["madi_configs"]["gen_config"]["temperature"], 
                    max_completion_tokens=configs["madi_configs"]["gen_config"]["max_completion_tokens"], 
                    top_p=configs["madi_configs"]["gen_config"]["top_p"], 
                    stop=configs["madi_configs"]["gen_config"]["stop"],
                    stream=configs["madi_configs"]["gen_config"]["stream"],
                    max_retries=self.max_retries,
                    parse_json=True
                )
            else:
                final_plan = initial_plan

            self.interactions[-1].plan = {
                "initial_plan": initial_plan,
                "reflection": reflection,
                "final_plan": final_plan
            }
            logger.info("Final plan", final_plan)
            return final_plan
        except Exception as e:
            logger.error(r)
            return f"RefError: {e}"
    
    # def observe(self, utterance_history, tool_calling_result): 
    #     # TODO: do loop
    #     utterance_history.append(
    #         {
    #             "role": "user", 
    #             "content": f"This is results of tool calling. Leverage these and do diagnoses: {tool_calling_result}"
    #         }
    #     )
        
    #     response = self.client.chat.completions.create(
    #         messages=messages,
    #         model=configs["madi_configs"]["groq_llm"]["default_model_name"],
    #         temperature=configs["madi_configs"]["groq_llm"]["temperature"],
    #         max_completion_tokens=configs["madi_configs"]["groq_llm"]["max_completion_tokens"],
    #         top_p=configs["madi_configs"]["groq_llm"]["top_p"],
    #         stop=configs["madi_configs"]["groq_llm"]["stop"],
    #         stream=configs["madi_configs"]["groq_llm"]["stream"],
    #     )
    #     return response

    def execute(self, user_query: str) -> str:
        """Execute the full pipeline: plan and execute tools"""
        try:
            plan = self.plan(user_query)

            if not plan.get("requires_tools", True):
                logger.title("The plan does not require tool usage")
                return plan["direct_response"]

            # Execute each tool in sequence
            logger.title("Start to call tools")
            results = []
            for tool_call in plan["tool_calls"]:
                tool_name = tool_call["tool"]
                tool_args = tool_call["args"]
                result = self.use_tool(tool_name, **tool_args)
                # if isinstance(result, list): 
                #     for data in result: 
                #         if isinstance(data, PubmedSearchResult):
                #             text = f"""Pubmed id: {data.pubmed_id} 
                #             # Content: 
                #             1. Abstract: {data.abstract}
                #             2. Methods: {data.methods}
                #             3. Results: {data.results}
                #             4. Conclusion: {data.conclusion}
                #             """
                #         elif isinstance(data, DDuckGoSearchResult): 
                #             text = f"""url: {data.url}
                #             Content: {data.content}
                #             """
                #         results.append(text)
                results.extend(result)
            # combine results
            return results

        except Exception as e:
            return f"Error executing plan: {str(e)}"

if __name__ == "__main__": 
    llm=Groq(
        api_key=ENV_VAR["GROQ_API_KEY"]
    )
    search_agent = SearchAgent(
        llm, 
        role=SEARCH_ENGINE_AGENT_ROLE,
        instructions=SEARCH_ENGINE_AGENT_INSTRUCTIONS,
        capabilities=SEARCH_ENGINE_AGENT_CAPABILITIES, 
        max_retries=3
    )
    search_agent.add_tool(duckgo_search)
    search_agent.add_tool(search_pubmed)
    chief_complaint = "Vomiting blood for 2 days after eating."
    medical_history = "The patient experienced vomiting of coffee-colored gastric contents (approximately 100ml) accompanied by dizziness, palpitations, and weakness after consuming hard food 2 days ago. There was no abdominal distension, pain, melena, or bloody stool, nor any confusion. The patient was treated conservatively with acid-suppressing and hemostatic medications, after which symptoms of vomiting blood improved. The patient has a history of chronic Hepatitis B for three years, which has not been treated."
    physical_examination = "Pale skin and mucous membranes, flat abdomen with no visible peristaltic waves and presence of abdominal breathing. No abdominal wall vein varicosity was observed. The abdomen was soft without fluid wave or shifting dullness, and no palpable masses. There was no significant tenderness or rebound tenderness, and the liver and spleen were not palpable below the ribs. Murphy's sign was negative. No evident kidney area tenderness or percussion pain, and no abnormal vascular pulsation in the abdomen. No significant tenderness at bilateral ureteral pressure points. Liver dullness was present, with the upper boundary at the right mid-clavicular line at the fifth intercostal space, with no shifting dullness. Bowel sounds were normal."

    message = f"""Chief complain: {chief_complaint}
    Medical history: {medical_history}
    Physical examination: {physical_examination}
    """

    result = search_agent.execute(message)
    print("\nSEARCH AGENT RESULT:\n")
    print(result)

