import os
import json
import time

from langchain_mistralai import ChatMistralAI

llm_mistral = ChatMistralAI(model="mistral-large-latest", api_key=os.getenv("MISTRAL_API_KEY"), temperature=0)
llm_codestral = ChatMistralAI(model="codestral-latest", api_key=os.getenv("MISTRAL_API_KEY"), temperature=0)


def safe_invoke(prompt, model):
    RETRIES = 5
    DELAY = 10

    for attempt in range(RETRIES):
        try:
            if model == "codestral":
                return llm_codestral.invoke(prompt)
            
            return llm_mistral.invoke(prompt)

        except Exception as e:
            time.sleep(DELAY)
            DELAY *= 2

    raise Exception("[DEBUG] Invoke failed after retries")


def invoke_with_retries(prompt, model, extract_function, validation_function):
    MAX_ATTEMPTS = 2
    extracted_result = None

    for attempt in range(MAX_ATTEMPTS):
        llm_response = safe_invoke(prompt, model)

        clean = extract_function(llm_response.content)
        
        try:
            extracted_result = json.loads(clean) if extract_function.__name__ == "extract_json_block" else clean

            if validation_function(extracted_result):
                return extracted_result
        
        except Exception:
            continue

    return None
