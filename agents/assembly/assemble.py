import json
from langchain_core.messages import SystemMessage

from agents.state import AgentState
from ui_events import EVENT_QUEUE
from llm.client import invoke_with_retries
from utils.extraction import extract_python_code

from prompts.assemble_program import (INITIAL_ASSEMBLE_PROMPT, REVIEW_REASSEMBLE_PROMPT, FEEDBACK_REASSEMBLE_PROMPT)


def assemble_program(agent_state: AgentState) -> AgentState:
    def validation_python_code(code):
        if code and code.strip():
            return True
        
        return False
    

    gen_funcs = agent_state.get("generatedFunctionsCode", [])
    functions_code_block = "\n\n".join(f.get("code", "") for f in gen_funcs if f.get("code"))
    architecture = agent_state.get("architecture", {})

    mode = "initial generation" if not agent_state.get("finalProgram") else (
        "regenerate invalid program" if (agent_state.get("programValidationRound", 0) > 0) 
        else "feedback revision" )

    if mode == "initial generation":
        EVENT_QUEUE.put({
            "type": "status",
            "stage": "assembly" })
        
        system_prompt = SystemMessage(content=INITIAL_ASSEMBLE_PROMPT.format(
            architecture=json.dumps(architecture, indent=2),
            functions_code_block=functions_code_block,
            useCase=agent_state['useCase'] ))
    
    elif mode == "regenerate invalid program":
        system_prompt = SystemMessage(content=REVIEW_REASSEMBLE_PROMPT.format(
            finalProgram=agent_state['finalProgram'],
            programValidationErrors=json.dumps(agent_state.get("programValidationErrors", []), indent=2),
            useCase=agent_state['useCase'] ))
    
    elif mode == "feedback revision":
        EVENT_QUEUE.put({
            "type": "status",
            "stage": "assembly" })
        
        system_prompt = SystemMessage(content=FEEDBACK_REASSEMBLE_PROMPT.format(
            finalProgram=agent_state['finalProgram'],
            usersFeedback=agent_state.get("usersFeedback", ""),
            architecture=json.dumps(agent_state["architecture"], indent=2),
            functions_code_block=functions_code_block,
            useCase=agent_state['useCase'] ))


    extracted_llm_response = invoke_with_retries([system_prompt], "codestral", extract_python_code, validation_python_code)
    if not extracted_llm_response:
        extracted_llm_response = ""

    agent_state["finalProgram"] = extracted_llm_response
    return agent_state
