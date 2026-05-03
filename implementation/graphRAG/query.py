import os
from huggingface_hub import login
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from .client import neo
from agents.state import AgentState
from utils.extraction import extract_all_methods


login(token=os.getenv("HF_TOKEN"))
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def graph_query(agent_state: AgentState) -> AgentState:
    all_methods = extract_all_methods(agent_state.get("architecture", {}))

    graphRag_results, methods_to_process = filter_methods_for_graph_query(all_methods, agent_state.get("graphRagResults", []),
                                                                          bool(agent_state.get("usersFeedback")) )

    all_functions_descriptions = neo.run("""
        MATCH (f:Function)-[:BELONGS_TO]->(c:Class)
        RETURN
            c.name AS class_name,
            c.responsibility AS class_responsibility,
            c.attributes AS class_attributes,
            f.name AS method_name,
            f.summary AS method_summary,
            f.description AS method_description,
            f.steps AS method_steps
        """)
    
    if not all_functions_descriptions:
        agent_state["graphRagResults"] = []
        return agent_state
    
    all_functions_embedding = build_graph_embeddings(all_functions_descriptions)

    for method in methods_to_process:
        if not method.get("name"):
            continue

        selected_names = select_similar_functions(method, all_functions_descriptions, all_functions_embedding)
        
        if not selected_names:
            graphRag_results.append({
                "requested": method,
                "matched_graph_functions": [] })
            continue

        matched_functions = get_matched_graph_functions(selected_names)

        graphRag_results.append({"requested": method,
                                "matched_graph_functions": matched_functions })

    agent_state["graphRagResults"] = graphRag_results

    return agent_state


def filter_methods_for_graph_query(all_methods, existing_results, has_feedback):
    if not has_feedback or not existing_results:
        return [], all_methods

    current_methods = {
        ( method.get("class"), method.get("name") )
        for method in all_methods if method.get("name") }

    graph_results = [
        item for item in existing_results
        if ( item["requested"].get("class"), item["requested"].get("name") ) in current_methods ]

    existing_names = {
        ( item["requested"].get("class"), item["requested"].get("name") )
        for item in graph_results }

    methods_to_process = [ 
        method for method in all_methods
        if ( method.get("class"), method.get("name") ) not in existing_names ]

    return graph_results, methods_to_process


def get_matched_graph_functions(selected_names: list) -> list:
    matched_functions_info = neo.run("""
        MATCH (f:Function)-[:BELONGS_TO]->(c:Class)
        WHERE any(item IN $selected
            WHERE item['name'] = f.name AND item['class'] = c.name)
        OPTIONAL MATCH (f)-[:PRODUCES]->(out:Data)
        OPTIONAL MATCH (f)-[:CONSUMES]->(inp:Data)
        OPTIONAL MATCH (f)-[:READS]->(ra:Attribute)
        OPTIONAL MATCH (f)-[:WRITES]->(wa:Attribute)
        OPTIONAL MATCH (c)-[:HAS_ATTRIBUTE]->(ca:Attribute)
        RETURN
            c.name AS class_name,
            c.responsibility AS responsibility,
            f.name AS function,
            f.summary AS summary,
            f.description AS description,
            f.code AS code,
            collect(DISTINCT {
                name: inp.name,
                type: inp.type,
                description: inp.description
            }) AS inputs,
            collect(DISTINCT {
                name: out.name,
                type: out.type,
                description: out.description
            }) AS outputs,
            collect(DISTINCT ra.name) AS reads,
            collect(DISTINCT wa.name) AS writes,
            collect(DISTINCT {
                name: ca.name,
                type: ca.type,
                description: ca.description
            }) AS class_attributes
        """, {"selected": selected_names})
    
    matched_functions = []
    for item in matched_functions_info:
        matched_functions.append({
            "class_attributes": [
                a for a in item.get("class_attributes", [])
                if a.get("name")],
            "name": item["function"],
            "summary": item.get("summary", ""),
            "description": item.get("description", ""),
            "code": item.get("code", ""),
            "inputs": [i for i in item["inputs"] if i["name"]],
            "outputs": [o for o in item["outputs"] if o["name"]] })

    return matched_functions


def build_graph_embeddings(graph_functions: list):
    def build_graph_text(f):
        return " ".join([
            f"Name: {f.get('method_name', '')}",
            f"Summary: {f.get('method_summary', '')}",
            f"Description: {f.get('method_description', '')}",
            "Steps: " + " ".join(f.get("method_steps", [])) ]).lower()
    
    if not graph_functions:
        return []

    texts = [build_graph_text(f) for f in graph_functions]
    embeddings = embedding_model.encode(texts)

    return embeddings


def select_similar_functions(target_func: dict, graph_functions: list, graph_embeddings: list) -> list:
    def build_target_text(f):
        return " ".join([
            f"Name: {f.get('name', '')}",
            f"Summary: {f.get('summary', '')}",
            f"Description: {f.get('description', '')}",
            "Steps: " + " ".join(f.get("steps", [])) ]).lower()
    
    if len(graph_embeddings) == 0:
        return []

    target_text = build_target_text(target_func)

    target_emb = embedding_model.encode([target_text])[0]

    similarities = cosine_similarity([target_emb], graph_embeddings)[0]

    scored = list(zip(graph_functions, similarities))

    THRESHOLD = 0.7
    filtered = [ (f, score) for f, score in scored if score >= THRESHOLD ]

    if not filtered:
        return []

    filtered.sort(key=lambda x: x[1], reverse=True)

    MAX_RESULTS = 2
    top = filtered[:MAX_RESULTS]

    return [ {"class": f["class_name"], "name": f["method_name"]}
                for f, score in top ]
