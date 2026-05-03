import re
from graphRAG.client import neo


def format_list_for_prompt(list: list) -> str:
    if not list:
        return "None"
    
    return "\n".join(f"- {item}" for item in list)


def normalize_function_name(name: str) -> str:
    rows = neo.run("""
        MATCH (f:Function)
        WHERE f.name = $base
           OR f.name STARTS WITH $base + "_"
        RETURN f.name AS name
    """, {"base": name})

    existing = [r["name"] for r in rows]

    if name not in existing:
        return name

    suffixes = []
    for n in existing:
        m = re.match(rf"{re.escape(name)}_(\d+)$", n)
        if m:
            suffixes.append(int(m.group(1)))

    next_idx = max(suffixes, default=1) + 1
    return f"{name}_{next_idx}"


def validation_review_json(parsed):
    score = float(parsed.get("score", None))
    if score is None or not (0 <= score <= 1):
        return False
    
    issues = parsed.get("issues", None)
    if isinstance(issues, list):
        return True
    
    return False
