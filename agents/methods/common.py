import json
from langchain_core.messages import SystemMessage
from llm.client import invoke_with_retries
from utils.extraction import extract_python_code

from prompts.code_generation import (INITIAL_METHOD_GENERATION_PROMPT)


def generate_single_method(context: dict) -> dict:
    method = context["method"]
    class_name = context["class_name"]
    class_attributes = context["class_attributes"]
    other_methods = context["other_methods"]
    reference_context = context["graph_matches"]

    system_prompt = SystemMessage(content=INITIAL_METHOD_GENERATION_PROMPT.format(
        class_name=class_name,
        class_attributes=json.dumps(class_attributes, indent=2, ensure_ascii=False),
        other_methods=json.dumps(other_methods, indent=2, ensure_ascii=False),
        method=json.dumps(method, indent=2, ensure_ascii=False),
        reference_context=json.dumps(reference_context, indent=2, ensure_ascii=False) ))
  
    code_text = invoke_llm_for_code(system_prompt)

    return {"class": method.get("class"),
            "method": method.get("name"),
            "code": code_text}


def invoke_llm_for_code(prompt: SystemMessage, fallback: str = "") -> str:
    def validation_python_code(code):
        if code and code.strip():
            return True
        
        return False
    
    extract_llm_response = invoke_with_retries([prompt], "codestral", extract_python_code, validation_python_code)
    if extract_llm_response:
        return extract_llm_response
    else:
        return fallback
