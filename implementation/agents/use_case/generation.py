from copy import deepcopy
from langchain_core.messages import SystemMessage

from agents.state import AgentState
from orchestration.config import MAX_VALIDATION_ROUNDS, REVIEW_TRESHOLD
from ui_events import EVENT_QUEUE
from utils.formatting import format_list_for_prompt
from llm.client import safe_invoke

from prompts.use_case import (INITIAL_USECASE_GENERATION_PROMPT, REVIEW_USECASE_REVISION_PROMPT, FEEDBACK_USECASE_REVISION_PROMPT)


def generate_use_case(agent_state: AgentState) -> AgentState:
    mode = "initial generation" if not agent_state.get("useCase", "") else (
        "review revision" if agent_state.get("useCaseReview", "") else "feedback revision")

    if mode == "initial generation":
        EVENT_QUEUE.put({
            "type": "status",
            "stage": "use_case" })
        
        agent_state["useCaseReviewRound"] = 0
        userTask = agent_state["messagesHistory"][-1].content
        
        system_prompt = SystemMessage(content=INITIAL_USECASE_GENERATION_PROMPT.format(userTask=userTask))
    
    elif mode == "review revision":
        system_prompt = SystemMessage(content=REVIEW_USECASE_REVISION_PROMPT.format(
                useCase=agent_state["useCase"],
                issues=format_list_for_prompt(agent_state['useCaseReview'].get('issues', [])) ))
    
    elif mode == "feedback revision":
        EVENT_QUEUE.put({
            "type": "status",
            "stage": "use_case" })
        
        agent_state["previousUseCase"] = deepcopy(agent_state.get("useCase", ""))
        
        system_prompt = SystemMessage(content=FEEDBACK_USECASE_REVISION_PROMPT.format(
                useCase=agent_state["useCase"],
                feedback=agent_state["usersFeedback"] ))


    llm_response = safe_invoke([system_prompt], "mistral")
    agent_state["useCase"] = llm_response.content
    return agent_state


def decide_use_case_review_design(agent_state: AgentState) -> str:
    if (agent_state.get("useCaseReviewRound", 0) < MAX_VALIDATION_ROUNDS and
        agent_state.get("useCaseReview", {}).get("score", 0) < REVIEW_TRESHOLD):
        return "review"
    else:
        return "design"
