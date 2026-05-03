import json
from langchain_core.messages import SystemMessage

from agents.state import AgentState
from ui_events import EVENT_QUEUE
from llm.client import safe_invoke

from prompts.acitivity_diagram import (INITIAL_GENERATION_DIAGRAM_PROMPT, REVIEW_GENERATION_DIAGRAM_PROMPT)


def generate_activity_diagram(agent_state: AgentState) -> AgentState:
    mode = ("initial generation" if not agent_state.get("activityDiagramReview", "") 
            else "revision")

    if mode == "initial generation":
        EVENT_QUEUE.put({
            "type": "status",
            "stage": "diagram" })
        
        system_prompt = SystemMessage(content=INITIAL_GENERATION_DIAGRAM_PROMPT.format(
            architecture=json.dumps(agent_state.get('architecture', {}), indent=2),
            useCase=agent_state['useCase'],
            finalProgram=agent_state['finalProgram'] ))
    
    elif mode == "revision":
        system_prompt = SystemMessage(content=REVIEW_GENERATION_DIAGRAM_PROMPT.format(
            activityDiagramReview=agent_state.get('activityDiagramReview'),
            activityDiagram=agent_state.get('activityDiagram') ))

    response = safe_invoke([system_prompt], model="mistral")
    agent_state["activityDiagram"] = response.content
    return agent_state


def decide_activity_review(agent_state: AgentState) -> str:
    if not agent_state.get("activityDiagramReview", ""):
        return "review"
    else:
        return "get_feedback"
