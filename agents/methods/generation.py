import json
from copy import deepcopy
from langchain_core.messages import SystemMessage

from agents.state import AgentState
from ui_events import EVENT_QUEUE
from .common import generate_single_method, invoke_llm_for_code
from .feedback_generation import apply_feedback_revision
from utils.extraction import extract_all_methods
from utils.building import build_method_context

from prompts.code_generation import (VALIDATION_METHOD_GENERATION_PROMPT)


def generate_function_code(agent_state: AgentState) -> AgentState:
    mode = "initial generation" if not agent_state.get("generatedFunctionsCode") else (
        "regenerate invalid functions" if (agent_state.get("functionValidationRound", 0) > 0) or (agent_state.get("classValidationRound", 0) > 0) 
        else "feedback revision" )
            
    if mode == "initial generation":
        EVENT_QUEUE.put({
            "type": "status",
            "stage": "methods" })
        
        generated = initial_generation(agent_state)

    elif mode == "regenerate invalid functions":
        generated = regenerate_invalid_functions(agent_state)
    
    elif mode == "feedback revision":
        EVENT_QUEUE.put({
            "type": "status",
            "stage": "methods" })
        
        generated = apply_feedback_revision(agent_state)


    agent_state["generatedFunctionsCode"] = generated
    return agent_state


def initial_generation(agent_state: AgentState) -> list:
    generated = []
    architecture = agent_state.get("architecture", {})
    all_methods = extract_all_methods(architecture)

    for method in all_methods:
        method_name = method.get("name")
        class_name = method.get("class")

        context = build_method_context(agent_state, class_name, method_name)
        generated.append(generate_single_method(context))

    return generated


def build_reference_context(graphRag_map: dict, class_name: str, method_name: str) -> list:
    rag_item = graphRag_map.get((class_name, method_name), {})
    matched = rag_item.get("matched_graph_functions", [])

    return matched


def regenerate_invalid_functions(agent_state: AgentState) -> list:
    invalid_only = agent_state.get("invalidFunctions", [])

    architecture = agent_state.get("architecture", {})

    all_methods = extract_all_methods(architecture)

    existing_generated = { (f["class"], f["method"]): f
                            for f in agent_state.get("generatedFunctionsCode", []) }

    methods_to_generate = [ m for m in all_methods
                            if (m["class"], m["name"]) in invalid_only ]

    generated = []

    for key, method_data in existing_generated.items():
        if (method_data["class"], method_data["method"]) not in invalid_only:
            generated.append(deepcopy(method_data))

    for method in methods_to_generate:
        class_name = method.get("class")
        method_name = method.get("name")

        context = build_method_context(agent_state, class_name, method_name)
        generated.append(regenerate_single_method(context))
    
    return generated


def regenerate_single_method(context: dict) -> dict:
    method = context["method"]
    class_name = context["class_name"]
    class_attributes = context["class_attributes"]
    other_methods = context["other_methods"]
    previous_impl = context.get("previous_impl", "")
    error_reason = context.get("error_reason", [])

    system_prompt = SystemMessage(content=VALIDATION_METHOD_GENERATION_PROMPT.format(
        class_name=class_name,
        class_attributes=json.dumps(class_attributes, indent=2, ensure_ascii=False),
        other_methods=json.dumps(other_methods, indent=2, ensure_ascii=False),
        method=json.dumps(method, indent=2, ensure_ascii=False),
        previous_impl=previous_impl,
        errors = json.dumps(error_reason, indent=2, ensure_ascii=False) ))

    code_text = invoke_llm_for_code(system_prompt, fallback=previous_impl)

    return {"class": method.get("class"),
            "method": method.get("name"),
            "code": code_text}
