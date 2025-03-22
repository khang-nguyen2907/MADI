from phi.agent import Agent
from madi.utils import extract_json_from_text
from madi.handlers import Log
from madi.prompt_engineering import (
    MEDOC_FIRST_SUMMARY_PROMPT, 
    MEDDOC_REFINE_PROMPT, 
    MEDOC_SUMMARY_ROLE
)
import json
from ollama import chat
from ollama import ChatResponse

logger = Log(__name__)

def gen_text(
    agent: Agent, 
    message: str, 
    max_retries: int = 3, 
    parse_json: bool = False
): 
    response = ''
    for i in range(max_retries + 1): 
        try: 
            response = agent.run(message, stream=False).content
            if not response: 
                raise ValueError("Response is empty")
            break

        except Exception as e: 
            logger.error("Error", e)
            logger.title(f"Retry {i+1}")

    if parse_json: 
        parsed_result = ''
        for i in range(max_retries+1): 
            try: 
                parsed_result = extract_json_from_text(response) 
                logger.title("JSON response is parsed successfully")
                return parsed_result
            except Exception as e: 
                logger.error("Error", e)
                logger.info("Input to be parsed unsuccessfully", response)
                logger.title(f"Retry {i+1}")
        return parsed_result
    return response

def generate_response(
    client, 
    messages, 
    service,
    model,
    temperature,
    max_completion_tokens,
    top_p,
    stop,
    stream,
    max_retries: int =3, 
    parse_json: bool=False
):
    response = ''
    for i in range(max_retries + 1): 
        try: 
            if service == "groq": 
                response = client.chat.completions.create(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_completion_tokens=max_completion_tokens,
                    top_p=top_p,
                    stop=stop,
                    stream=stream,
                ).choices[0].message.content
            elif service == "ollama": 
                response: ChatResponse = chat(model=model, messages=messages).message.content
            else: 
                raise ValueError(f"service {service} is not supported.")
            if not response: 
                raise ValueError("Response is empty")
            break

        except Exception as e: 
            logger.error("Error", e)
            logger.title(f"Retry {i+1}")

    if parse_json: 
        if not isinstance(response, dict):
            parsed_result = ''
            for i in range(max_retries+1): 
                try: 
                    # Always try the extract_json_from_text function first
                    parsed_result = extract_json_from_text(response)
                    if parsed_result is not None:
                        logger.title("JSON response extracted successfully")
                        return parsed_result
                    
                    # If extraction didn't work, try direct parsing as fallback
                    parsed_result = json.loads(response)
                    logger.title("JSON response parsed successfully via direct loading")
                    return parsed_result
                except Exception as e: 
                    logger.error("Error", e)
                    logger.info("Input to be parsed unsuccessfully", response)
                    logger.title(f"Retry {i+1}")
        else: 
            parsed_result = response
        return parsed_result
    return response

def refine_medoc(
    client, 
    medoc: list, 
    service,
    model,
    temperature,
    max_completion_tokens,
    top_p,
    stop,
    stream,
    max_retries: int =3
): 
    first_summary_message = [
        {
            "role": "system", 
            "content": MEDOC_SUMMARY_ROLE
        }, 
        {
            "role": "user", 
            "content": MEDOC_FIRST_SUMMARY_PROMPT.format(text=medoc[0])
        }
    ]   
    first_summary = generate_response(
        client,
        messages=first_summary_message,
        service=service,
        model=model,
        temperature=temperature,
        max_completion_tokens=max_completion_tokens,
        top_p=top_p,
        stop=stop,
        stream=stream,
        max_retries=max_retries,
        parse_json=False
    )
    logger.info(f"FIST_SUMMARY response: \n***\n{first_summary}\n***\n")
            
    for md in medoc[1:]: 
        refined_summary_message = [
            {
                "role": "system", 
                "content": MEDOC_SUMMARY_ROLE
            }, 
            {
                "role": "user", 
                "content": MEDDOC_REFINE_PROMPT.format(
                    existing_answer=first_summary, 
                    text=md
                )
            }
        ]

        refined_summary = generate_response(
            client,
            messages=refined_summary_message,
            service=service,
            model=model,
            temperature=temperature,
            max_completion_tokens=max_completion_tokens,
            top_p=top_p,
            stop=stop,
            stream=stream,
            max_retries=max_retries,
            parse_json=False
        )
        logger.info(f"REFINED_SUMMARY response: \n***\n{refined_summary}\n***\n")

                
    return refined_summary
        

def summarize_medoc(
    client, 
    medoc: list, 
    service,
    model,
    temperature,
    max_completion_tokens,
    top_p,
    stop,
    stream,
    max_retries: int =3
): 
    summaries = []
    
    for doc in medoc: 
        message = [
            {
                "role": "system", 
                "content": MEDOC_SUMMARY_ROLE
            }, 
            {
                "role": "user", 
                "content": MEDOC_FIRST_SUMMARY_PROMPT.format(text=doc)
            }
        ]

        summary = generate_response(
            client,
            messages=message,
            service=service,
            model=model,
            temperature=temperature,
            max_completion_tokens=max_completion_tokens,
            top_p=top_p,
            stop=stop,
            stream=stream,
            max_retries=max_retries,
            parse_json=False
        )
        logger.info("SUMMARIZE", f"{doc[:100]}...: \n\n{summary}")

        summaries.append(summary)
    return summaries
