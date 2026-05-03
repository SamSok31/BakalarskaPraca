import json
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage

from agents.state import AgentState
from ui_events import EVENT_QUEUE, RESPONSE_QUEUE
from llm.client import invoke_with_retries
from graphRAG.client import persist_function_to_graph, persist_function_io, persist_function_attributes
from utils.extraction import extract_json_block
from utils.building import build_method_spec_lookup, build_graph_function_payload

from prompts.acitivity_diagram import (FEEDBACK_TYPE_PROMPT)


def user_feedback(agent_state: AgentState) -> AgentState:
    set_defaults_states(agent_state)

    EVENT_QUEUE.put({
            "type": "status",
            "stage": "done" })
    
    agent_state["messagesHistory"].append(AIMessage(content=agent_state["finalProgram"]))
    agent_state["messagesHistory"].append(AIMessage(content=agent_state["activityDiagram"]))
    EVENT_QUEUE.put({
            "type": "output",
            "program": agent_state["finalProgram"],
            "diagram": agent_state["activityDiagram"] })
    
    response = RESPONSE_QUEUE.get()

    user_feedback = response.get("message", "").strip()
    agent_state["usersFeedback"] = user_feedback

    if not user_feedback or user_feedback.lower() == "ok":
        EVENT_QUEUE.put({
            "type": "persist",
            "message": "waiting response" })
        
        response = RESPONSE_QUEUE.get()

        add = response.get("message", "").strip().lower()
        agent_state["persistToGraph"] = (add == "yes")

    else:
        agent_state["persistToGraph"] = False

    agent_state["messagesHistory"].append(HumanMessage(content=user_feedback))

    return agent_state


def set_defaults_states(agent_state: AgentState) -> AgentState:
    agent_state["useCaseReview"] = {}
    agent_state["useCaseReviewRound"] = 0

    agent_state["architectureReview"] = {}
    agent_state["architectureReviewRound"] = 0

    agent_state["activityDiagramReview"] = ""

    agent_state["invalidFunctions"] = []
    agent_state["functionValidationErrors"] = {}
    agent_state["functionValidationRound"] = 0
    agent_state["classValidationRound"] = 0

    agent_state["programValidationErrors"] = []
    agent_state["programValidationRound"] = 0
    agent_state["testValidationRound"] = 0

    agent_state["activityDiagramReview"] = ""

    return agent_state


def decide_gen_again(agent_state: AgentState) -> str:
    feedback_type = classify_feedback_type(agent_state)

    if feedback_type == "NO_FEEDBACK":
        return "add_to_graph"

    elif feedback_type == "CODE_FIX":
        return "generate_functions"

    elif feedback_type == "USE_CASE_UPDATE":
        return "generate_use_case"

    return "generate_functions"


def classify_feedback_type(agent_state: AgentState) -> str:
    def validation_json(parsed) -> bool:
        if parsed.get("classification") in ("CODE_FIX", "USE_CASE_UPDATE"):
            return True
        return False


    feedback = agent_state.get("usersFeedback", "")
    
    if not feedback or feedback.lower().strip() == "ok":
        return "NO_FEEDBACK"

    system_prompt = SystemMessage(content=FEEDBACK_TYPE_PROMPT.format(
        feedback=feedback,
        useCase=agent_state.get("useCase", ""),
        architecture=json.dumps(agent_state.get("architecture", {}), indent=2) ))
    
    extracted_llm_response = invoke_with_retries([system_prompt], "mistral", extract_json_block, validation_json)
    if extracted_llm_response:
        return extracted_llm_response.get("classification", "USE_CASE_UPDATE")
    else:
        return "USE_CASE_UPDATE"
    
    
def graph_write_back(agent_state: AgentState) -> AgentState:
    if not agent_state.get("persistToGraph"):
        return agent_state

    architecture = agent_state.get("architecture", {})
    classes = architecture.get("classes", [])

    method_specs = build_method_spec_lookup(classes)

    for gen in agent_state.get("generatedFunctionsCode", []):
        class_name = gen.get("class")
        method_name = gen.get("method")
        code = gen.get("code", "")

        func_spec = method_specs.get((class_name, method_name))
        if not func_spec:
            continue

        func_payload = build_graph_function_payload(func_spec, class_name, code, classes)

        persist_function_to_graph(func_payload, code)
        persist_function_io(func_payload)
        persist_function_attributes(func_payload)

    return agent_state
    