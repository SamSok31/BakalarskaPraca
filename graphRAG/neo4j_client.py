from neo4j import GraphDatabase
from typing import Any, Dict, List


class Neo4jClient:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password) )

    def close(self):
        self.driver.close()

    def run(self, query: str, params: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]
