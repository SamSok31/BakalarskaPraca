import re
import ast

from gitHub.enricher import enrich_class_metadata_with_llm, enrich_attribute_descriptions_with_llm


def extract_json_block(text: str) -> str:
    if not text:
        return ""

    text = text.strip()

    fence_match = re.search(
        r"```(?:json)?\s*(.*?)```",
        text,
        re.DOTALL | re.IGNORECASE )

    if fence_match:
        text = fence_match.group(1).strip()

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        return text[start:end + 1]

    return text


def extract_python_code(text: str) -> str:
    if not text:
        return ""

    text = text.strip()

    python_blocks = re.findall(r"```python\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if python_blocks:
        return python_blocks[0].strip()

    generic_blocks = re.findall(r"```\s*(.*?)```", text, re.DOTALL)
    if generic_blocks:
        return generic_blocks[0].strip()

    if any(keyword in text for keyword in ["def ", "class ", "import ", "if __name__"]):
        return text.strip()

    return ""


def extract_all_methods(architecture: dict) -> list:
    all_methods = []

    for cls in architecture.get("classes", []):
        for method in cls.get("methods", []):
            method_copy = method.copy()
            method_copy["class"] = cls.get("name")
            all_methods.append(method_copy)

    return all_methods


def extract_class_metadata(classes: list, class_name: str) -> dict:
    for cls in classes:
        if cls.get("name") == class_name:
            raw_attrs = cls.get("attributes", [])

            return {
                "class_responsibility": cls.get("responsibility", ""),
                "class_attributes": [attr["name"] for attr in raw_attrs],
                "class_attribute_metadata": {
                    attr["name"]: {
                        "type": attr.get("type", "unknown"),
                        "description": attr.get("description", "") }
                    for attr in raw_attrs } }

    return {}


def extract_method_attribute_usage(func_node):
    reads = set()
    writes = set()

    mutating_methods = {"append", "extend", "insert", "remove",
                        "pop", "clear", "update", "add"}

    for stmt in ast.walk(func_node):

        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:

                if (isinstance(target, ast.Attribute)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "self"):
                        writes.add(target.attr)

                elif (isinstance(target, ast.Subscript)
                    and isinstance(target.value, ast.Attribute)
                    and isinstance(target.value.value, ast.Name)
                    and target.value.value.id == "self"):
                        writes.add(target.value.attr)

        elif isinstance(stmt, ast.AugAssign):
            target = stmt.target

            if (isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == "self"):
                    writes.add(target.attr)
                    reads.add(target.attr)

        elif isinstance(stmt, ast.Call):
            if isinstance(stmt.func, ast.Attribute):

                if (isinstance(stmt.func.value, ast.Attribute)
                    and isinstance(stmt.func.value.value, ast.Name)
                    and stmt.func.value.value.id == "self"):
                        attr_name = stmt.func.value.attr
                        method_name = stmt.func.attr

                        if method_name in mutating_methods:
                            writes.add(attr_name)
                        else:
                            reads.add(attr_name)

        elif isinstance(stmt, ast.Attribute):
            if (isinstance(stmt.value, ast.Name)
                and stmt.value.id == "self"):
                    reads.add(stmt.attr)

    reads = reads - writes
    return list(reads), list(writes)


def extract_method_attribute_usage_from_code(code: str):
    try:
        tree = ast.parse(code)
    except Exception:
        return [], []

    func_node = next((node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)), None)

    if not func_node:
        return [], []

    return extract_method_attribute_usage(func_node)


def extract_functions_from_tree(tree):
    functions = []

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            functions.append((node, None, [], {}, "Contains functions that are not part of any class."))

        elif isinstance(node, ast.ClassDef):
            functions.extend(extract_class_functions(node))

    return functions


def extract_class_functions(class_node):
    attribute_metadata = extract_class_attribute_metadata(class_node)
    attributes = list(attribute_metadata.keys())

    method_names = [item.name for item in class_node.body
        if isinstance(item, ast.FunctionDef) and item.name != "__init__" ]

    responsibility = ""

    responsibility = enrich_class_metadata_with_llm(class_node.name, attributes, method_names)

    attribute_descriptions = {}

    attribute_descriptions = enrich_attribute_descriptions_with_llm(class_node.name, attributes, method_names)

    for attr in attribute_metadata:
        attribute_metadata[attr]["description"] = attribute_descriptions.get(attr, "")

    return [(item, class_node.name, attributes, attribute_metadata, responsibility)
        for item in class_node.body if isinstance(item, ast.FunctionDef) ]


def extract_method_attribute_usage(func_node):
    reads = set()
    writes = set()

    mutating_methods = {"append", "extend", "insert", "remove",
                        "pop", "clear", "update", "add"}

    for stmt in ast.walk(func_node):

        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if (isinstance(target, ast.Attribute)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "self"):

                    writes.add(target.attr)

                elif (isinstance(target, ast.Subscript)
                    and isinstance(target.value, ast.Attribute)
                    and isinstance(target.value.value, ast.Name)
                    and target.value.value.id == "self"):

                    writes.add(target.value.attr)

        elif isinstance(stmt, ast.AugAssign):
            target = stmt.target

            if (isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == "self"):

                writes.add(target.attr)
                reads.add(target.attr)

        elif isinstance(stmt, ast.Call):
            if isinstance(stmt.func, ast.Attribute):

                if (isinstance(stmt.func.value, ast.Attribute)
                    and isinstance(stmt.func.value.value, ast.Name)
                    and stmt.func.value.value.id == "self"):

                    attr_name = stmt.func.value.attr
                    method_name = stmt.func.attr

                    if method_name in mutating_methods:
                        writes.add(attr_name)
                    else:
                        reads.add(attr_name)

        elif isinstance(stmt, ast.Attribute):
            if (isinstance(stmt.value, ast.Name)
                and stmt.value.id == "self"):

                reads.add(stmt.attr)

    reads = reads - writes

    return list(reads), list(writes)

def extract_class_attribute_metadata(class_node):
    metadata = {}

    for item in class_node.body:
        if isinstance(item, ast.FunctionDef) and item.name == "__init__":

            for stmt in item.body:

                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:

                        if (isinstance(target, ast.Attribute)
                            and isinstance(target.value, ast.Name)
                            and target.value.id == "self"):

                            attr_name = target.attr
                            value = stmt.value

                            attr_type = "unknown"

                            if isinstance(value, ast.List):
                                attr_type = "list"

                            elif isinstance(value, ast.Dict):
                                attr_type = "dict"

                            elif isinstance(value, ast.Tuple):
                                attr_type = "tuple"

                            elif isinstance(value, ast.Set):
                                attr_type = "set"

                            elif isinstance(value, ast.Constant):
                                if value.value is None:
                                    attr_type = "None"
                                else:
                                    attr_type = type(value.value).__name__

                            elif isinstance(value, ast.Call):
                                if isinstance(value.func, ast.Name):
                                    attr_type = value.func.id

                                elif isinstance(value.func, ast.Attribute):
                                    attr_type = value.func.attr

                            metadata[attr_name] = {"type": attr_type,
                                                "description": ""}

    return metadata


def extract_plantuml(text):
    match = re.search(r"@startuml.*?@enduml", text, re.DOTALL)
    if match:
        return match.group(0).strip()

    match = re.search(r"```(.*?)```", text, re.DOTALL)
    if match:
        code = match.group(1).strip()

        if code.startswith("plantuml"):
            code = code[len("plantuml"):].strip()

        return code

    return None
