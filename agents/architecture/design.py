import json
from copy import deepcopy
from langchain_core.messages import SystemMessage

from agents.state import AgentState
from orchestration.config import MAX_VALIDATION_ROUNDS, REVIEW_TRESHOLD
from ui_events import EVENT_QUEUE
from utils.formatting import format_list_for_prompt
from llm.client import invoke_with_retries
from utils.extraction import extract_json_block

from prompts.architecture import (INITIAL_DESIGN_PROMPT, REVIEW_DESIGN_PROMPT, FEEDBACK_DESIGN_PROMPT)


def design_architecture(agent_state: AgentState) -> AgentState:
    mode = "initial design" if not agent_state.get("architecture", "") else (
        "architecture revision" if agent_state.get("architectureReview", "") else "feedback revision" )

    if mode == "initial design":
        EVENT_QUEUE.put({
            "type": "status",
            "stage": "architecture" })
        
        agent_state["architectureReviewRound"] = 0
        userTask = agent_state["messagesHistory"][-1].content

        system_prompt = SystemMessage(content=INITIAL_DESIGN_PROMPT.format(useCase=agent_state["useCase"], userTask=userTask) )
    
    elif mode == "architecture revision":
        system_prompt = SystemMessage(content=REVIEW_DESIGN_PROMPT.format(
            architecture=json.dumps(agent_state['architecture'], indent=2, ensure_ascii=False),
            architectureReview=format_list_for_prompt(agent_state['architectureReview'].get('issues', [])),
            useCase=agent_state['useCase'] ))
    
    elif mode == "feedback revision":
        EVENT_QUEUE.put({
            "type": "status",
            "stage": "architecture" })
        
        agent_state["previousArchitecture"] = deepcopy(agent_state.get("architecture", {"classes": []}))
        system_prompt = SystemMessage(content=FEEDBACK_DESIGN_PROMPT.format(
            architecture = json.dumps(agent_state['architecture'], indent=2, ensure_ascii=False),
            usersFeedback = agent_state.get('usersFeedback', ''),
            useCase = agent_state.get('useCase', '') ))


    extracted_llm_response = invoke_with_retries([system_prompt], "mistral", extract_json_block, lambda x: True)
    if extracted_llm_response:
        if isinstance(extracted_llm_response, list):
            extracted_llm_response = {"classes": extracted_llm_response}
        
        agent_state["architecture"] = extracted_llm_response
    else:
        raise ValueError("design_architecture failed to produce valid architecture JSON")
    
    return agent_state


def decide_architecture_review(agent_state: AgentState) -> str:
    if (agent_state.get("architectureReviewRound", 0) < MAX_VALIDATION_ROUNDS and 
        agent_state.get("architectureReview", {}).get("score", 0) < REVIEW_TRESHOLD):
        return "review"
    else:
        return "graph_rag"
