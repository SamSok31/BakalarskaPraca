import json
from copy import deepcopy
from langchain_core.messages import SystemMessage

from agents.state import AgentState
from .common import generate_single_method, invoke_llm_for_code
from llm.client import safe_invoke
from utils.building import build_method_context, build_previous_methods_map
from utils.extraction import extract_json_block

from prompts.code_generation import (SELECT_FEEDBACK_INFLUENCED_METHODS_PROMPT, FEEDBACK_METHOD_GENERATION_PROMPT)


def apply_feedback_revision(agent_state: AgentState) -> list:
    current_arch = agent_state.get("architecture", {})
    previous_arch = agent_state.get("previousArchitecture", agent_state.get("architecture", {}))

    current_classes = current_arch.get("classes", [])
    previous_classes = previous_arch.get("classes", [])

    previous_methods = build_previous_methods_map(previous_classes)
    current_methods = {}

    current_method_keys = set(current_methods.keys())
    previous_method_keys = set(previous_methods.keys())

    removed_methods = previous_method_keys - current_method_keys

    previous_code_map = {(item["class"], item["method"]): item
                     for item in agent_state.get("generatedFunctionsCode", []) }


    methods_to_regen = filter_methods_to_regen(agent_state)
    generated, modified = [], []

    for cls in current_classes:
        class_name = cls["name"]

        for method in cls.get("methods", []):
            method_name = method["name"]

            key = (class_name, method_name)

            old_code_entry = previous_code_map.get(key)

            if key not in methods_to_regen:
                if old_code_entry:
                    generated.append(deepcopy(old_code_entry))
                continue

            modified.append(key)

            context = build_method_context(agent_state, class_name, method_name)
            generated.append(generate_or_update_method(context))

    generated = [item for item in generated
                if (item["class"], item["method"]) not in removed_methods ]

    agent_state["modifiedFunctions"] = modified
    return generated


def filter_methods_to_regen(agent_state):
    current_arch = agent_state.get("architecture", {})
    previous_arch = agent_state.get("previousArchitecture", agent_state.get("architecture", {}))

    current_classes = current_arch.get("classes", [])
    previous_classes = previous_arch.get("classes", [])

    previous_methods = build_previous_methods_map(previous_classes)
    current_methods = {}

    for cls in current_classes:
        for m in cls.get("methods", []):
            current_methods[(cls["name"], m["name"])] = m

    current_method_keys = set(current_methods.keys())
    previous_method_keys = set(previous_methods.keys())

    new_methods = current_method_keys - previous_method_keys
    existing_methods = current_method_keys & previous_method_keys


    previous_code_map = {(item["class"], item["method"]): item
                        for item in agent_state.get("generatedFunctionsCode", []) }

    llm_selected = set()
    feedback = agent_state.get("usersFeedback", "")

    for cls in current_classes:
        class_name = cls["name"]
        methods = cls.get("methods", [])

        selected = llm_select_methods_for_class(class_name, methods, previous_code_map, feedback )

        for m in selected:
            llm_selected.add((class_name, m))

    spec_changed = { key for key in existing_methods
                if method_spec_changed(previous_methods[key], current_methods[key]) }

    methods_to_regen = new_methods | spec_changed | llm_selected
    return methods_to_regen


def method_spec_changed(old_spec, new_spec) -> bool:
    keys = ["summary", "description", "steps", "inputs", "outputs", "special requirements"]

    return any(old_spec.get(k) != new_spec.get(k) for k in keys)


def llm_select_methods_for_class(class_name, methods, previous_code_map, feedback):
    methods_with_code = []

    for method in methods:
        method_name = method["name"]
        old_code_entry = previous_code_map.get((class_name, method_name))

        methods_with_code.append({
            "name": method_name,
            "summary": method.get("summary"),
            "description": method.get("description"),
            "steps": method.get("steps"),
            "code": old_code_entry["code"] if old_code_entry else "" })

    system_prompt = SystemMessage(content=SELECT_FEEDBACK_INFLUENCED_METHODS_PROMPT.format(
        feedback=feedback,
        class_name=class_name,
        methods_with_code=json.dumps(methods_with_code, indent=2, ensure_ascii=False) ))
    
    response = safe_invoke([system_prompt], "mistral")
    clean = extract_json_block(response.content)

    try:
        data = json.loads(clean)
        return set(data.get("methods_to_regenerate", []))
    except:
        return set()


def generate_or_update_method(context: dict):
    method = context["method"]
    class_name = context["class_name"]
    class_attributes = context["class_attributes"]
    other_methods = context["other_methods"]
    old_spec = context["old_spec"]
    old_code = context["previous_impl"]
    feedback = context["feedback"]

    mode = "revision" if old_spec else "initial"

    if mode == "initial":
        return generate_single_method(context)
    
    system_prompt = SystemMessage(content=FEEDBACK_METHOD_GENERATION_PROMPT.format(
        class_name=class_name,
        class_attributes=json.dumps(class_attributes, indent=2, ensure_ascii=False),
        other_methods=json.dumps(other_methods, indent=2, ensure_ascii=False),
        old_code=old_code,
        method=json.dumps(method, indent=2, ensure_ascii=False),
        feedback=feedback ))

    code_text = invoke_llm_for_code(system_prompt, fallback=old_code)

    return {"class": class_name,
            "method": method.get("name"),
            "code": code_text }
