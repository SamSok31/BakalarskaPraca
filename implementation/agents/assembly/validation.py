import re
import json
import ast
from langchain_core.messages import SystemMessage
from sklearn.metrics.pairwise import cosine_similarity

from agents.state import AgentState
from orchestration.config import MAX_VALIDATION_ROUNDS, REVIEW_TRESHOLD
from .tests import run_unit_test_phase, run_integration_test_phase
from llm.client import invoke_with_retries, safe_invoke
from utils.extraction import extract_json_block
from utils.formatting import validation_review_json
from graphRAG.query import embedding_model

from prompts.assemble_program import (REVIEW_INITIAL_PROGRAM_PROMPT, REVIEW_AFTER_FEEDBACK_PROGRAM_PROMPT, PROGRAM_TO_USECASE_PROMPT)


def validate_program(agent_state: AgentState) -> AgentState:
    if (agent_state.get("programValidationRound", 0) >= MAX_VALIDATION_ROUNDS and 
        agent_state.get("testValidationRound", 0) >= MAX_VALIDATION_ROUNDS):
        agent_state["programValidationRound"] = agent_state.get("programValidationRound", 0) + 1
        agent_state["testValidationRound"] = agent_state.get("testValidationRound", 0) + 1
        return agent_state

    program = agent_state.get("finalProgram", "")
    errors = []

    if (agent_state.get("programValidationRound", 0) < MAX_VALIDATION_ROUNDS):
        errors.extend(check_program_syntax_and_compile(program))
        errors.extend(semantic_program_review(agent_state))

        if errors:
            agent_state["programValidationRound"] = agent_state.get("programValidationRound", 0) + 1
        else:
            agent_state["programValidationRound"] = MAX_VALIDATION_ROUNDS
    else:
        errors.extend(run_unit_test_phase(agent_state))
        errors.extend(run_integration_test_phase(agent_state))

        if errors:
            agent_state["testValidationRound"] = agent_state.get("testValidationRound", 0) + 1
        else:
            agent_state["testValidationRound"] = MAX_VALIDATION_ROUNDS

    agent_state["programValidationErrors"] = errors

    return agent_state


def decide_program_validation(agent_state: AgentState) -> str:
    if (agent_state.get("programValidationErrors") and 
        agent_state.get("programValidationRound", 0) <= MAX_VALIDATION_ROUNDS):
        return "regen_program"
    elif (agent_state.get("programValidationErrors") and 
          agent_state.get("testValidationRound", 0) <= MAX_VALIDATION_ROUNDS):
        return "regen_program"
    else:
        return "gen_activity_diagram"


def check_program_syntax_and_compile(program: str) -> list:
    errors = []

    if not program.strip():
        errors.append({"type": "syntax",
                    "message": "Program is empty."})
        return errors

    try:
        ast.parse(program)
    except SyntaxError as e:
        errors.append({"type": "syntax",
                    "message": f"{e.msg} (line {e.lineno}, col {e.offset})" })
        
    try:
        compile(program, "<string>", "exec")
    except Exception as e:
        errors.append({"type": "compile",
                    "message": str(e)})

    return errors


def semantic_program_review(agent_state: AgentState) -> list:
    errors = []
    errors.append(semantic_similarity(agent_state))
    errors.append(llm_semantic_review(agent_state))

    return errors


def llm_semantic_review(agent_state):
    errors = []

    has_feedback = bool(agent_state.get("usersFeedback", "").strip()
                and agent_state["usersFeedback"].lower() != "ok" )

    if not has_feedback:
        system_prompt = SystemMessage(content=REVIEW_INITIAL_PROGRAM_PROMPT.format(
            architecture=json.dumps(agent_state.get("architecture", {}), indent=2),
            useCase=agent_state['useCase'],
            finalProgram=agent_state['finalProgram'] ))
    else:
        system_prompt = SystemMessage(content=REVIEW_AFTER_FEEDBACK_PROGRAM_PROMPT.format(
            architecture=json.dumps(agent_state.get("architecture", {}), indent=2),
            useCase=agent_state['useCase'],
            usersFeedback=agent_state['usersFeedback'],
            finalProgram=agent_state['finalProgram'] ))


    extracted_llm_response = invoke_with_retries([system_prompt], "mistral", extract_json_block, validation_review_json)
    if extracted_llm_response:
        score = float(extracted_llm_response.get("score"))
        issues = extracted_llm_response.get("issues", [])
    else:
        score = 1.0
        issues = []

    if score < REVIEW_TRESHOLD:
        for issue in issues:
            errors.append({"type": "llm_semantic",
                        "message": issue })
    

    return errors


def semantic_similarity(agent_state):
    errors = []

    final_code = agent_state.get("finalProgram", "")
    original_use_case = agent_state.get("useCase", "")

    program_use_case = generate_use_case_from_program(final_code)

    uc_user = extract_use_case_sections(original_use_case)
    uc_program = extract_use_case_sections(program_use_case)

    if uc_program["goal"] and uc_program["main_flow"]:
        similarity = compute_use_case_similarity(uc_user, uc_program)

        SIM_THRESHOLD = 0.75
        if similarity < SIM_THRESHOLD:
            errors.append({
                "type": "semantic_similarity",
                "message": f"Low semantic similarity ({similarity:.2f}) between use case and program" })
            
    return errors


def extract_use_case_sections(use_case_text: str) -> dict:
    sections = {
        "goal": "",
        "responsibilities": [],
        "main_flow": [] }

    lines = use_case_text.splitlines()
    current_section = None

    for raw_line in lines:
        line = raw_line.strip()

        line = line.replace("**", "")

        if line.lower().startswith("goal:"):
            sections["goal"] = line.split(":", 1)[1].strip()
            current_section = None
            continue

        if "system responsibilities" in line.lower():
            current_section = "responsibilities"
            continue

        if "main success scenario" in line.lower():
            current_section = "main_flow"
            continue

        if current_section == "responsibilities":
            match = re.match(r"^(\d+\.|-)\s*(.*)", line)
            if match:
                sections["responsibilities"].append(match.group(2).strip())

        elif current_section == "main_flow":
            match = re.match(r"^\d+\.\s*(.*)", line)
            if match:
                sections["main_flow"].append(match.group(1).strip())

    return sections


def generate_use_case_from_program(code: str) -> str:
    prompt = PROGRAM_TO_USECASE_PROMPT.format(program=code)

    response = safe_invoke([SystemMessage(content=prompt)], "mistral")

    return response.content.strip()


def compute_use_case_similarity(uc1: dict, uc2: dict) -> float:
    def embed(text: str):
        return embedding_model.encode([text])[0]
    
    def cosine_sim(a, b):
        return cosine_similarity([a], [b])[0][0]

    weights = {
        "goal": 0.3,
        "responsibilities": 0.3,
        "main_flow": 0.4 }

    score = 0

    if uc1["goal"] and uc2["goal"]:
        score += weights["goal"] * cosine_sim(
            embed(uc1["goal"]),
            embed(uc2["goal"]) )

    if uc1["responsibilities"] and uc2["responsibilities"]:
        score += weights["responsibilities"] * cosine_sim(
            embed(" ".join(uc1["responsibilities"])),
            embed(" ".join(uc2["responsibilities"])) )

    if uc1["main_flow"] and uc2["main_flow"]:
        score += weights["main_flow"] * cosine_sim(
            embed(" ".join(uc1["main_flow"])),
            embed(" ".join(uc2["main_flow"])) )

    return score
