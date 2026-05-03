import ast
import json
from langchain_core.messages import SystemMessage

from agents.state import AgentState
from orchestration.config import MAX_VALIDATION_ROUNDS
from utils.extraction import extract_all_methods, extract_json_block
from llm.client import invoke_with_retries

from prompts.code_generation import (REVIEW_METHOD_PROMPT, REVIEW_CLASS_PROMPT)


def validate_function(agent_state: AgentState) -> AgentState:
    if agent_state.get("functionValidationRound", 0) >= MAX_VALIDATION_ROUNDS:
        agent_state["functionValidationRound"] = agent_state.get("functionValidationRound", 0) + 1
        return agent_state

    to_check = select_functions_to_validate(agent_state)

    architecture = agent_state.get("architecture", {})
    classes = architecture.get("classes", [])
    class_map = {cls["name"]: cls for cls in classes}
    all_methods = extract_all_methods(architecture)

    invalid = []
    errors = {}

    for entry in to_check:
        class_name = entry.get("class")
        method_name = entry.get("method")

        is_valid, reason = validate_single_function(entry, all_methods, class_map)

        if not is_valid:
            invalid.append((class_name, method_name))
            errors[(class_name, method_name)] = reason

    agent_state["invalidFunctions"] = invalid
    agent_state["functionValidationErrors"] = errors

    if invalid:
        agent_state["functionValidationRound"] = agent_state.get("functionValidationRound", 0) + 1
    else:
        agent_state["functionValidationRound"] = MAX_VALIDATION_ROUNDS + 1

    return agent_state


def select_functions_to_validate(agent_state: AgentState) -> list:
    mode = "initial first validation" if (agent_state.get("functionValidationRound", 0) == 0) and not agent_state.get("usersFeedback", "") else (
        "feedback first validation" if (agent_state.get("functionValidationRound", 0) == 0) 
        else "validation")

    if mode == "initial first validation":
        return agent_state.get("generatedFunctionsCode", [])
    
    if mode == "feedback first validation":
        modified = set(agent_state.get("modifiedFunctions", []))
        return [ f for f in agent_state.get("generatedFunctionsCode", [])
                if (f.get("class"), f.get("method")) in modified ]

    invalid_names = set(agent_state.get("invalidFunctions", []))

    return [ f for f in agent_state.get("generatedFunctionsCode", [])
        if (f.get("class"), f.get("method")) in invalid_names ]


def validate_single_function(entry, all_methods, class_map):
    class_name = entry.get("class")
    method_name = entry.get("method")
    code = entry.get("code", "")

    ok, msg = check_syntax(code, class_name, method_name)
    if not ok:
        return False, msg

    func_spec = next(
        (m for m in all_methods
         if m["name"] == method_name and m["class"] == class_name),
        None )

    if not func_spec:
        return True, ""

    class_attributes = class_map.get(class_name, {}).get("attributes", [])

    other_methods = [
        {"class": m["class"],
        "name": m["name"],
        "summary": m.get("summary", ""),
        "inputs": m.get("inputs", []),
        "outputs": m.get("outputs", []) }
        for m in all_methods
        if not (m["class"] == class_name and m["name"] == method_name) ]

    return semantic_validation_llm(func_spec, code, class_attributes, other_methods)


def check_syntax(code: str, class_name: str, method_name: str):
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        msg = f"SyntaxError: {str(e)}"

        return False, msg

  
def semantic_validation_llm(func_spec: dict, code: str, class_attributes: list, other_methods: list) -> bool:
    def validation_json(data):
        if not isinstance(data, dict):
            return False

        if "verdict" not in data:
            return False
        
        return True

    system_prompt = SystemMessage(content=REVIEW_METHOD_PROMPT.format(
        class_attributes=json.dumps(class_attributes, indent=2, ensure_ascii=False),
        other_methods=json.dumps(other_methods, indent=2, ensure_ascii=False),
        func_spec=json.dumps(func_spec, indent=2, ensure_ascii=False),
        code=code ))
    

    extracted_llm_response = invoke_with_retries([system_prompt], "mistral", extract_json_block, validation_json)
    if extracted_llm_response:
        if extracted_llm_response.get("verdict") == "VALID":
            return True, ""
        else:
            return False, extracted_llm_response.get("reason", "Failing semantic validation with method description")
    else:
        return True, ""

def validate_classes(agent_state: AgentState) -> AgentState:
    if agent_state.get("functionValidationRound", 0) <= MAX_VALIDATION_ROUNDS:
        return agent_state
    
    if agent_state.get("classValidationRound", 0) >= MAX_VALIDATION_ROUNDS:
        agent_state["classValidationRound"] = agent_state.get("classValidationRound", 0) + 1
        return agent_state
    

    architecture = agent_state.get("architecture", {})
    generated = agent_state.get("generatedFunctionsCode", [])
    classes = architecture.get("classes", [])

    invalid_methods = []
    class_errors = {}

    for cls in classes:
        class_name = cls.get("name")

        class_methods_code = [f for f in generated if f.get("class") == class_name]

        if not class_methods_code:
            continue

        system_prompt = SystemMessage(content=REVIEW_CLASS_PROMPT.format(
            class_spec=json.dumps(cls, indent=2, ensure_ascii=False),
            methods_code=json.dumps(class_methods_code, indent=2, ensure_ascii=False) ))

        result = invoke_with_retries([system_prompt], "mistral", extract_json_block,
            lambda x: isinstance(x, dict) and "verdict" in x )

        if not result:
            continue

        if result.get("verdict") == "INVALID":
            issues = result.get("issues", [])

            for issue in issues:
                method_name = issue.get("method")
                description = issue.get("description", "Class-level validation issue")

                if method_name:
                    invalid_methods.append((class_name, method_name))
                    class_errors.setdefault((class_name, method_name), []).append(description)

    agent_state["invalidFunctions"] = list(set(invalid_methods))
    agent_state["functionValidationErrors"] = class_errors

    if agent_state["invalidFunctions"]:
        agent_state["classValidationRound"] = agent_state.get("classValidationRound", 0) + 1
    else:
        agent_state["classValidationRound"] = MAX_VALIDATION_ROUNDS

    return agent_state


def decide_class_validation(agent_state: AgentState) -> str:
    if (agent_state.get("invalidFunctions") and 
        agent_state.get("classValidationRound", 0) <= MAX_VALIDATION_ROUNDS):
        return "regen_methods"
    else:
        return "assemble"
