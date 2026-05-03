from .extraction import extract_all_methods, extract_class_metadata, extract_method_attribute_usage_from_code
from utils.formatting import normalize_function_name


def build_method_context(agent_state, class_name, method_name):
    architecture = agent_state.get("architecture", {})
    previous_arch = agent_state.get("previousArchitecture", {})

    classes = architecture.get("classes", [])
    class_map = {cls["name"]: cls for cls in classes}
    class_data = class_map.get(class_name, {})

    class_attributes = class_data.get("attributes", [])
    all_methods = extract_all_methods(architecture)

    method = next((m for m in all_methods if m["name"] == method_name and m["class"] == class_name), None)

    other_methods = build_other_methods(all_methods, class_name, method_name)

    graphRag_map = build_graphrag_map(agent_state.get("graphRagResults", []))
    graph_matches = graphRag_map.get((class_name, method_name), {}).get("matched_graph_functions", [])

    previous_methods = build_previous_methods_map(previous_arch.get("classes", []))
    previous_code_map = {
        (item["class"], item["method"]): item
        for item in agent_state.get("generatedFunctionsCode", []) }

    key = (class_name, method_name)

    return {
        "agent_state": agent_state,
        "method": method,
        "class_name": class_name,
        "method_name": method_name,
        "class_attributes": class_attributes,
        "other_methods": other_methods,
        "old_spec": previous_methods.get(key),
        "previous_impl": previous_code_map.get(key, {}).get("code", ""),
        "error_reason": agent_state.get("functionValidationErrors", {}).get((class_name, method_name), []),
        "graph_matches": graph_matches,
        "feedback": agent_state.get("usersFeedback", "") }


def build_other_methods(all_methods: list, current_class: str, current_method_name: str) -> list:
    return [ {"name": m["name"],
            "summary": m.get("summary", ""),
            "description": m.get("description", ""),
            "inputs": [ {"name": i["name"], "type": i["type"]}
                        for i in m.get("inputs", []) ],
            "outputs": [ {"name": o["name"], "type": o["type"]}
                        for o in m.get("outputs", []) ] }
            for m in all_methods
            if m["class"] == current_class and m["name"] != current_method_name ]


def build_graphrag_map(graph_rag_results: list) -> dict:
    return { (item["requested"]["class"], item["requested"]["name"]): item
            for item in graph_rag_results if item.get("requested") }


def build_previous_methods_map(previous_classes: list) -> dict:
    previous_methods = {}

    for cls in previous_classes:
        for m in cls.get("methods", []):
            previous_methods[(cls["name"], m["name"])] = m

    return previous_methods


def build_method_spec_lookup(classes: list) -> dict:
    lookup = {}

    for cls in classes:
        class_name = cls.get("name")

        for method in cls.get("methods", []):
            lookup[(class_name, method["name"])] = method

    return lookup


def build_graph_function_payload(func_spec: dict, class_name: str, code: str, classes: list) -> dict:
    new_name = normalize_function_name(func_spec["name"])

    func_copy = dict(func_spec)

    func_copy.update({
        "class": class_name,
        "name": new_name,
        "id": new_name,
        "source": "generated",
        "tags": func_spec.get("tags", []) })

    func_copy.update(extract_class_metadata(classes, class_name))

    reads, writes = extract_method_attribute_usage_from_code(code)

    func_copy["reads_attributes"] = reads
    func_copy["writes_attributes"] = writes

    return func_copy
