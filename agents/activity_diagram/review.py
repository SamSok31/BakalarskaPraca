from langchain_core.messages import SystemMessage

from agents.state import AgentState
from llm.client import safe_invoke

from prompts.acitivity_diagram import (REVIEW_INITIAL_DIAGRAM_PROMPT)


def review_activity_diagram(agent_state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content=REVIEW_INITIAL_DIAGRAM_PROMPT.format(
        activityDiagram=agent_state.get('activityDiagram'),
        finalProgram=agent_state.get('finalProgram'),
        useCase=agent_state.get('useCase') ))

    llm_response = safe_invoke([system_prompt], model="mistral")
    agent_state["activityDiagramReview"] = llm_response.content

    return agent_state
