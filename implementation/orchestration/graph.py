from agents.state import AgentState
from langgraph.graph import END, START, StateGraph
from agents.use_case.generation import generate_use_case, decide_use_case_review_design
from agents.use_case.review import review_use_case
from agents.architecture.design import design_architecture, decide_architecture_review
from agents.architecture.review import review_architecture
from graphRAG.query import graph_query
from agents.methods.generation import generate_function_code
from agents.methods.validation import validate_function, validate_classes, decide_class_validation
from agents.assembly.assemble import assemble_program
from agents.assembly.validation import validate_program, decide_program_validation
from agents.feedback.feedback import user_feedback, graph_write_back, decide_gen_again
from agents.activity_diagram.generation import generate_activity_diagram, decide_activity_review
from agents.activity_diagram.review import review_activity_diagram


def build_graph():
    graph = StateGraph(AgentState)
    
    graph.add_node("generate_use_case", generate_use_case)
    graph.add_node("review_use_case", review_use_case)

    graph.add_node("design_architecture", design_architecture)
    graph.add_node("review_architecture", review_architecture)
    graph.add_node("graph_query", graph_query)

    graph.add_node("generate_function_code", generate_function_code)
    graph.add_node("validate_function", validate_function)
    graph.add_node("validate_classes", validate_classes)

    graph.add_node("assemble_program", assemble_program)
    graph.add_node("validate_program", validate_program)

    graph.add_node("user_feedback", user_feedback)
    graph.add_node("generate_activity_diagram", generate_activity_diagram)
    graph.add_node("review_activity_diagram", review_activity_diagram)
    graph.add_node("graph_write_back", graph_write_back)

    graph.add_node("router_review_useCase_design", lambda state: state)
    graph.add_node("router_architecture_review", lambda state: state)
    graph.add_node("router_method_validation", lambda state: state)
    graph.add_node("router_class_validation", lambda state: state)
    graph.add_node("router_program_validation", lambda state: state)
    graph.add_node("router_activity_review", lambda state: state)
    graph.add_node("router_gen_again", lambda state: state)


    graph.add_edge(START, "generate_use_case")

    graph.add_edge("generate_use_case", "router_review_useCase_design")
    graph.add_conditional_edges("router_review_useCase_design", decide_use_case_review_design, {
            "review": "review_use_case",
            "design": "design_architecture"
        })
    graph.add_edge("review_use_case", "generate_use_case")

    graph.add_edge("design_architecture", "router_architecture_review")
    graph.add_conditional_edges("router_architecture_review", decide_architecture_review, {
            "review": "review_architecture",
            "graph_rag": "graph_query"
        })
    graph.add_edge("review_architecture", "design_architecture")

    graph.add_edge("graph_query", "generate_function_code")

    graph.add_edge("generate_function_code", "validate_function")
    graph.add_edge("validate_function", "validate_classes")
    graph.add_edge("validate_classes", "router_class_validation")
    graph.add_conditional_edges("router_class_validation", decide_class_validation, {
            "regen_methods": "generate_function_code",
            "assemble": "assemble_program"
        })

    graph.add_edge("assemble_program", "validate_program")
    graph.add_edge("validate_program", "router_program_validation")
    graph.add_conditional_edges("router_program_validation", decide_program_validation, {
            "regen_program": "assemble_program",
            "gen_activity_diagram": "generate_activity_diagram"
        })

    graph.add_edge("generate_activity_diagram", "router_activity_review")
    graph.add_conditional_edges("router_activity_review", decide_activity_review, {
            "review": "review_activity_diagram",
            "get_feedback": "user_feedback"
        })
    graph.add_edge("review_activity_diagram", "generate_activity_diagram")

    graph.add_edge("user_feedback", "router_gen_again")
    graph.add_conditional_edges("router_gen_again", decide_gen_again, {
            "generate_functions": "generate_function_code",
            "add_to_graph": "graph_write_back",
            "generate_use_case": "generate_use_case"
        })
    graph.add_edge("graph_write_back", END)

    return graph.compile()
