import json
from langchain_core.messages import SystemMessage

from agents.state import AgentState
from orchestration.config import MAX_VALIDATION_ROUNDS, REVIEW_TRESHOLD
from llm.client import invoke_with_retries
from utils.extraction import extract_json_block
from utils.formatting import validation_review_json

from prompts.architecture import (REVIEW_INITIAL_DESIGN_PROMPT, REVIEW_DESIGN_AFTER_FEEDBACK_PROMPT)


def review_architecture(agent_state: AgentState) -> AgentState:
    if agent_state.get("architectureReviewRound", 0) >= MAX_VALIDATION_ROUNDS:
        return agent_state

    if agent_state.get("architectureReview", {}).get("score", 0) >= REVIEW_TRESHOLD:
        return agent_state

    mode = "feedback revision" if agent_state.get("usersFeedback", "") else "initial review"

    if mode == "initial review":
        userTask = agent_state["messagesHistory"][-1].content
        system_prompt = SystemMessage(content=REVIEW_INITIAL_DESIGN_PROMPT.format(
            architecture = json.dumps(agent_state['architecture'], indent=2, ensure_ascii=False),
            useCase = agent_state['useCase'],
            userTask = userTask ))
    
    elif mode == "feedback revision":
        system_prompt = SystemMessage(content=REVIEW_DESIGN_AFTER_FEEDBACK_PROMPT.format(
            previousArchitecture = json.dumps(agent_state['previousArchitecture'], indent=2, ensure_ascii=False),
            architecture = json.dumps(agent_state['architecture'], indent=2, ensure_ascii=False),
            useCase = agent_state['useCase'],
            usersFeedback = agent_state['usersFeedback'] ))

    extracted_llm_response = invoke_with_retries([system_prompt], "mistral", extract_json_block, validation_review_json)
    if extracted_llm_response:
        result = {"score": float(extracted_llm_response.get("score")),
                "issues": extracted_llm_response.get("issues")}
    else:
        result = {"score": 1.0, "issues": []}

    agent_state["architectureReview"] = result
    agent_state["architectureReviewRound"] += 1
    return agent_state
