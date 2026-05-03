import os
import sys
import re
import json
import subprocess
import tempfile
from langchain_core.messages import SystemMessage

from agents.state import AgentState
from llm.client import invoke_with_retries
from agents.methods.generation import invoke_llm_for_code
from utils.extraction import extract_json_block

from prompts.assemble_program import (GENERATE_UNIT_TESTS_PROMPT, UNIT_TESTABILITY_PROMPT, GENERATE_INTEGRATION_TESTS_PROMPT)


def run_unit_test_phase(agent_state: AgentState) -> list:
    if agent_state.get("testValidationRound", 0) == 0:
        classify_testable_methods(agent_state)
        generate_unit_tests(agent_state)


    return run_unit_tests(agent_state)


def classify_testable_methods(agent_state: AgentState) -> AgentState:
    modified = set(agent_state.get("modifiedFunctions", []))
    classes = agent_state.get("architecture", {}).get("classes", [])

    mode =  "initial classification" if not agent_state.get("usersFeedback", "") else "feedback classification"
    if mode == "initial classification":
        methods_to_check = [ (cls.get("name"), m)
                            for cls in classes
                            for m in cls.get("methods", []) ]
    elif mode == "feedback classification":
        methods_to_check = [ (cls.get("name"), m)
                            for cls in classes
                            for m in cls.get("methods", [])
                            if (cls.get("name"), m.get("name")) in modified ]
        
    testable = []
    generated_map = { (item["class"], item["method"]): item["code"]
                    for item in agent_state.get("generatedFunctionsCode", []) }

    for class_name, method in methods_to_check:
        method_name = method.get("name")
        if method_name in ["__init__", "main", "run", "start", "setup_ui"]:
            continue

        code = generated_map.get((class_name, method_name), "")

        if not code:
            continue

        if not is_method_testable(code):
            continue

        if llm_unit_testability_check(method, code):
            testable.append((class_name, method_name))

    if agent_state.get("usersFeedback", ""):
        current_methods = get_current_methods(classes)

        existing = set(agent_state.get("testableMethods", []))
        existing = filter_existing_methods(existing, current_methods, modified)

        final = existing.union(testable)
    else:
        final = set(testable)

    agent_state["testableMethods"] = list(final)

    return agent_state


def generate_unit_tests(agent_state: AgentState) -> AgentState:
    classes = agent_state.get("architecture", {}).get("classes", [])
    current_methods = get_current_methods(classes)

    existing_tests = agent_state.get("generatedUnitTests", [])
    existing_map = { (t["class"], t["method"]): t
                    for t in existing_tests }
    existing_map = { k: v for k, v in existing_map.items()
                    if k in current_methods }

    is_feedback = bool(agent_state.get("usersFeedback"))
    modified = set(agent_state.get("modifiedFunctions", [])) if is_feedback else set()

    if is_feedback:
        existing_map = { k: v for k, v in existing_map.items()
                        if k not in modified }

    testable = set(agent_state.get("testableMethods", []))
    methods_to_generate = (testable if not is_feedback else testable.intersection(modified))

    generated_tests = []
    generated_code_map = { (item["class"], item["method"]): item["code"]
                        for item in agent_state.get("generatedFunctionsCode", []) }

    for cls in classes:
        class_name = cls.get("name")

        for method in cls.get("methods", []):
            key = (class_name, method.get("name"))

            if key not in methods_to_generate:
                continue

            code = generated_code_map.get(key, "")
            if not code:
                continue

            system_prompt = SystemMessage(content=GENERATE_UNIT_TESTS_PROMPT.format(
                cls=json.dumps(cls, indent=2, ensure_ascii=False),
                method=json.dumps(method, indent=2, ensure_ascii=False),
                code=code,
                class_name=class_name ))
            
            test_code = invoke_llm_for_code(system_prompt)

            tests = split_test_functions(test_code)

            generated_tests.append({
                "class": class_name,
                "method": key[1],
                "test_codes": tests })

    final_map = existing_map.copy()

    for t in generated_tests:
        final_map[(t["class"], t["method"])] = t

    agent_state["generatedUnitTests"] = list(final_map.values())

    return agent_state


def run_unit_tests(agent_state: AgentState) -> list:
    errors = []
    final_program = agent_state.get("finalProgram", "")
    tests = agent_state.get("generatedUnitTests", [])

    for test in tests:
        test_codes = test.get("test_codes", [])
        if not test_codes:
            continue

        for test_code in test_codes:
            result = run_test_in_subprocess(final_program, test_code)

            if result["returncode"] != 0:
                errors.append({
                    "type": "unit_test_failure",
                    "class": test.get("class"),
                    "method": test.get("method"),
                    "error_type": "SubprocessError",
                    "message": result["stderr"],
                    "stdout": result["stdout"],
                    "test_code": test_code })


    return errors


def run_test_in_subprocess(program_code, test_code):
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(program_code)
            f.write("\n\n")
            f.write(test_code)
            temp_file = f.name

        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=10)

        return {"returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr }

    except subprocess.TimeoutExpired:
        return {"returncode": -1,
                "stdout": "",
                "stderr": "Test timeout" }

    finally:
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)


def is_method_testable(code: str) -> bool:
    code = code.lower()

    non_testable_keywords = ["button", "canvas", "window", "click", "event", "render",
                             "draw", "mainloop", "bind", "pack","grid", "label", "tkinter", 
                             "create_oval", "create_rectangle", ".config(", ".pack(", ".grid("]

    if any(keyword in code for keyword in non_testable_keywords):
        return False

    return True


def llm_unit_testability_check(method: dict, code: str) -> bool:
    def validation_json(data):
        if not isinstance(data, dict):
            return False
        
        verdict = data.get("verdict", None)\
        
        if not verdict:
            return False
        
        if verdict not in ["TESTABLE", "NOT_TESTABLE"]:
            return False
        
        return True
    
    system_prompt = SystemMessage(content=UNIT_TESTABILITY_PROMPT.format(
        method=json.dumps(method, indent=2, ensure_ascii=False),
        code=code ))


    extracted_llm_response = invoke_with_retries([system_prompt], "mistral", extract_json_block, validation_json)
    if extracted_llm_response:
        return extracted_llm_response.get("verdict") == "TESTABLE"
    else:
        return False


def split_test_functions(code: str) -> list:
        pattern = r"(def test_.*?)(?=\ndef test_|\Z)"
        matches = re.findall(pattern, code, re.DOTALL)

        return [m.strip() for m in matches]


def get_current_methods(classes):
    return {(cls.get("name"), m.get("name"))
            for cls in classes
            for m in cls.get("methods", [])
            if m.get("name")}


def filter_existing_methods(existing_set, current_methods, modified=None):
    existing = {m for m in existing_set if m in current_methods}

    if modified:
        existing = {m for m in existing if m not in modified}

    return existing



def run_integration_test_phase(agent_state: AgentState) -> list:
    if agent_state.get("testValidationRound", 0) == 0:
        generate_integration_test(agent_state)

    return run_integration_test(agent_state)


def generate_integration_test(agent_state: AgentState) -> AgentState:
    architecture = agent_state.get("architecture", {})
    useCase = agent_state.get("useCase", "")

    system_prompt = SystemMessage(content=GENERATE_INTEGRATION_TESTS_PROMPT.format(
        useCase = useCase,
        architecture=json.dumps(architecture, indent=2, ensure_ascii=False) ))

    test_code = invoke_llm_for_code(system_prompt)
    agent_state["generatedIntegrationTests"] = split_test_functions(test_code)

    return agent_state


def run_integration_test(agent_state: AgentState) -> list:
    errors = []
    final_program = agent_state.get("finalProgram", "")
    tests = agent_state.get("generatedIntegrationTests", [])

    if not tests:
        return errors

    for test_code in tests:
        result = run_test_in_subprocess(final_program, test_code)

        if result["returncode"] != 0:
            errors.append({
                "type": "integration_test_failure",
                "error_type": "SubprocessError",
                "message": result["stderr"],
                "stdout": result["stdout"],
                "test_code": test_code })

    return errors
