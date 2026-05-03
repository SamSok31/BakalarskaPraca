import re
import json
from langchain_core.messages import SystemMessage

from llm.client import safe_invoke
from prompts.github import (ENRICH_FUNCTION_PROMPT, ADMIT_FUNCTION_PROMPT, ENRICH_CLASS_PROMPT, ENRICH_ATTRIBUTE_PROMPT)


def extract_json_gh(text: str) -> dict | None:
    if not text:
        return None

    cleaned = text.strip()

    fence_match = re.search(
        r"```(?:json)?\s*(.*?)```",
        cleaned,
        re.DOTALL | re.IGNORECASE )

    if fence_match:
        cleaned = fence_match.group(1).strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end != -1:
        cleaned = cleaned[start:end + 1]

    try:
        parsed = json.loads(cleaned)

        if isinstance(parsed, dict):
            return parsed

        return None

    except Exception:
        return None
    

def enrich_function_with_llm(function_candidate: dict) -> dict:
    system_prompt = SystemMessage(content=ENRICH_FUNCTION_PROMPT.format(
        function_name=function_candidate['name'],
        function_inputs=function_candidate['inputs'],
        function_code=function_candidate['code'] ))

    response = safe_invoke([system_prompt], model="mistral")

    enriched = extract_json_gh(response.content)

    if not enriched:
        print(response.content)
        return function_candidate

    function_candidate["summary"] = enriched.get("summary", "")
    function_candidate["description"] = enriched.get("description", "")
    function_candidate["steps"] = enriched.get("steps", [])
    function_candidate["outputs"] = enriched.get("outputs", [])

    return function_candidate


def admit_function_llm(func_desc: dict, code: str) -> bool:
    system_prompt = SystemMessage(content=ADMIT_FUNCTION_PROMPT.format(
        func_desc=json.dumps(func_desc, indent=2, ensure_ascii=False),
        code=code ))

    response = safe_invoke([system_prompt], model="mistral")
    content = response.content.strip().lower()
    return ("accept" in content) and ("reject" not in content)


def enrich_class_metadata_with_llm(class_name, attributes, methods):
    system_prompt = SystemMessage(content=ENRICH_CLASS_PROMPT.format(
        class_name=class_name,
        attributes=attributes,
        methods=methods ))

    response = safe_invoke([system_prompt], model="mistral")

    parsed = extract_json_gh(response.content)

    if not parsed:
        return ""

    return parsed.get("responsibility", "")


def enrich_attribute_descriptions_with_llm(class_name, attributes, methods):
    system_prompt = SystemMessage(content=ENRICH_ATTRIBUTE_PROMPT.format(
        class_name=class_name,
        attributes=attributes,
        methods=methods ))

    response = safe_invoke([system_prompt], model="mistral")

    parsed = extract_json_gh(response.content)

    if not parsed:
        return {}

    return parsed
