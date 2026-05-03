from langchain_core.messages import SystemMessage

from agents.state import AgentState
from orchestration.config import MAX_VALIDATION_ROUNDS, REVIEW_TRESHOLD
from llm.client import invoke_with_retries
from utils.extraction import extract_json_block
from utils.formatting import validation_review_json

from prompts.use_case import (REVIEW_INITIAL_GENERATION_USECASE_PROMPT, REVIEW_GENERATION_AFTER_FEEDBACK_USECASE_PROMPT)


def review_use_case(agent_state: AgentState) -> AgentState:
    if agent_state.get("useCaseReviewRound", 0) >= MAX_VALIDATION_ROUNDS:
        return agent_state

    if agent_state.get("useCaseReview", {}).get("score", 0) >= REVIEW_TRESHOLD:
        return agent_state


    mode = "initial review" if not agent_state.get("usersFeedback", "") else "after feedback revision"

    if mode == "initial review":
        userTask = agent_state["messagesHistory"][-1].content

        system_prompt = SystemMessage(content=REVIEW_INITIAL_GENERATION_USECASE_PROMPT.format(
                useCase=agent_state["useCase"],
                userTask=userTask ))
        
    elif mode == "after feedback revision":
        system_prompt = SystemMessage(content=REVIEW_GENERATION_AFTER_FEEDBACK_USECASE_PROMPT.format(
                previousUseCase=agent_state["previousUseCase"],
                useCase=agent_state["useCase"],
                feedback=agent_state["usersFeedback"] ))


    extracted_llm_response = invoke_with_retries([system_prompt], "mistral", extract_json_block, validation_review_json)

    if extracted_llm_response:
        result = {"score": float(extracted_llm_response.get("score")),
                "issues": extracted_llm_response.get("issues")}
    else:
        result = {"score": 1.0, "issues": []}

    agent_state["useCaseReview"] = result
    agent_state["useCaseReviewRound"] += 1

    return agent_state
