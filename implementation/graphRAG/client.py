from graphRAG.neo4j_client import Neo4jClient

neo = Neo4jClient(uri="bolt://localhost:7687", user="neo4j", password="password")


def persist_function_to_graph(func: dict, code: str):
    if func.get("class") == "Global":
        func["class_responsibility"] = ("Contains functions that are not part of any class.")

    neo.run("""
        MERGE (c:Class {name: $class_name})
        SET
            c.responsibility = $responsibility,
            c.attributes = $attributes
    """, {
        "class_name": func.get("class", ""),
        "responsibility": func.get("class_responsibility", ""),
        "attributes": func.get("class_attributes", []) })

    neo.run("""
        MERGE (f:Function {id: $id})
        SET
            f.name = $name,
            f.class = $class_name,
            f.summary = $summary,
            f.description = $description,
            f.steps = $steps,
            f.source = $source,
            f.tags = $tags,
            f.code = $code
    """, {
        "id": func["id"],
        "name": func["name"],
        "class_name": func.get("class", ""),
        "summary": func.get("summary", ""),
        "description": func.get("description", ""),
        "steps": func.get("steps", []),
        "source": func.get("source", ""),
        "tags": func.get("tags", []),
        "code": code })

    neo.run("""
        MATCH (f:Function {id: $id}),
              (c:Class {name: $class_name})
        MERGE (f)-[:BELONGS_TO]->(c)
    """, {
        "id": func["id"],
        "class_name": func.get("class", "") })


def persist_function_io(func: dict):
    func_id = func["id"]

    for out in func.get("outputs", []):
        data_id = f"{out['name']}:{out['type']}"

        neo.run("""
            MERGE (d:Data {id: $data_id})
            SET
                d.name = $name,
                d.type = $type,
                d.description = $description
            """, {
            "data_id": data_id,
            "name": out["name"],
            "type": out["type"],
            "description": out.get("description", "") })

        neo.run("""
            MATCH (f:Function {id: $func_id}),
                  (d:Data {id: $data_id})
            MERGE (f)-[:PRODUCES]->(d)
            """, {
            "func_id": func_id,
            "data_id": data_id })

    for inp in func.get("inputs", []):
        data_id = f"{inp['name']}:{inp['type']}"

        neo.run("""
            MERGE (d:Data {id: $data_id})
            SET
                d.name = $name,
                d.type = $type,
                d.description = $description
            """, {
            "data_id": data_id,
            "name": inp["name"],
            "type": inp["type"],
            "description": inp.get("description", "") })

        neo.run("""
            MATCH (f:Function {id: $func_id}),
                  (d:Data {id: $data_id})
            MERGE (f)-[:CONSUMES]->(d)
            """, {
            "func_id": func_id,
            "data_id": data_id })


def persist_function_attributes(func: dict):
    if func.get("class") == "Global":
        return

    class_name = func.get("class")

    for attr in func.get("class_attributes", []):
        meta = func.get("class_attribute_metadata", {}).get(attr, {})

        neo.run("""
            MERGE (a:Attribute {name: $name, class: $class_name})
            SET
                a.type = $type,
                a.description = $description
        """, {
            "name": attr,
            "class_name": class_name,
            "type": meta.get("type", "unknown"),
            "description": meta.get("description", "") })

        neo.run("""
            MATCH (c:Class {name: $class_name}),
                  (a:Attribute {name: $name, class: $class_name})
            MERGE (c)-[:HAS_ATTRIBUTE]->(a)
        """, {
            "class_name": class_name,
            "name": attr })

    for attr in func.get("reads_attributes", []):

        neo.run("""
            MATCH (f:Function {id: $id}),
                  (a:Attribute {name: $name, class: $class_name})
            MERGE (f)-[:READS]->(a)
        """, {
            "id": func["id"],
            "name": attr,
            "class_name": class_name })

    for attr in func.get("writes_attributes", []):

        neo.run("""
            MATCH (f:Function {id: $id}),
                  (a:Attribute {name: $name, class: $class_name})
            MERGE (f)-[:WRITES]->(a)
        """, {
            "id": func["id"],
            "name": attr,
            "class_name": class_name })
        

def delete_file_from_graph(repo_name: str, file_path: str):
    source = f"{repo_name}:{file_path}"

    neo.run("""
        MATCH (f:Function {source: $source})
        DETACH DELETE f
    """, {
        "source": source })

    neo.run("""
        MATCH (c:Class)
        WHERE c.name <> "Global"
        AND NOT EXISTS {
            MATCH (:Function)-[:BELONGS_TO]->(c)
        }
        DETACH DELETE c
    """)

    neo.run("""
        MATCH (a:Attribute)
        WHERE NOT EXISTS {
            MATCH (:Class)-[:HAS_ATTRIBUTE]->(a)
        }
        DETACH DELETE a
    """)

    neo.run("""
        MATCH (d:Data)
        WHERE NOT EXISTS {
            MATCH (:Function)-[:CONSUMES|PRODUCES]->(d)
        }
        DETACH DELETE d
    """)
