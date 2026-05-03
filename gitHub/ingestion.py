import time
import ast

from ui_events import EVENT_QUEUE
from .client import get_latest_commit_sha, github_get, get_changed_files_from_commit, get_file_content_from_commit
from .enricher import enrich_function_with_llm, admit_function_llm
from graphRAG.client import (delete_file_from_graph, persist_function_to_graph, 
                            persist_function_io, persist_function_attributes, neo)
from utils.extraction import extract_method_attribute_usage, extract_functions_from_tree


CHECK_INTERVAL_MINUTES = 5
REPOSITORIES = [{"owner": "SamSok31",
                "name": "testBP",
                "full_name": "SamSok31/testBP",
                "type": "internal" }]


def get_repository_state(repo_name: str):
    result = neo.run("""
        MATCH (r:RepositoryState {name: $name})
        RETURN r.last_commit AS last_commit
    """, {
        "name": repo_name })

    if not result:
        return None

    return result[0].get("last_commit")

def save_repository_state(repo_name: str, commit_sha: str):
    neo.run("""
        MERGE (r:RepositoryState {name: $name})
        SET r.last_commit = $last_commit
    """, {
        "name": repo_name,
        "last_commit": commit_sha })


class GitHubExplorer:
    def __init__(self):
        self.repositories = REPOSITORIES
        self.running = False


    def start(self):
        self.running = True

        while self.running:
            self.check_repositories()
            time.sleep(CHECK_INTERVAL_MINUTES * 60)


    def check_repositories(self):
        EVENT_QUEUE.put({
            "type": "github_reset",
            "message": "Checking repositories" })
        
        for repo in self.repositories:
            self.check_repository(repo)


    def check_repository(self, repo):
        name = repo.get("name", "unknown")
        current_commit = get_latest_commit_sha(repo)

        if current_commit is None:
            return

        last_commit = get_repository_state(name)

        if last_commit is None:
            self.bootstrap_repository(repo, current_commit)

            save_repository_state(name, current_commit)
            return

        if current_commit != last_commit:
            self.handle_new_commit(repo, current_commit)
            save_repository_state(name, current_commit)


    def bootstrap_repository(self, repo, commit_hash):
        owner = repo["owner"]
        name = repo["name"]

        commit_data = github_get(f"/repos/{owner}/{name}/commits/{commit_hash}")
        tree_sha = commit_data["commit"]["tree"]["sha"]

        tree = github_get(
            f"/repos/{owner}/{name}/git/trees/{tree_sha}",
            params={"recursive": 1})

        files = tree.get("tree", [])

        python_files = [item["path"] for item in files
            if item["type"] == "blob" and item["path"].endswith(".py") ]


        for file_path in python_files:
            self.process_python_file(repo, commit_hash, file_path)


    def handle_new_commit(self, repo, commit_hash):
        changed_files = get_changed_files_from_commit(repo, commit_hash)

        repo_name = repo["name"]

        for file in changed_files:
            status = file["status"]
            filename = file["filename"]

            if status == "removed":
                if filename.endswith(".py"):
                    EVENT_QUEUE.put({
                        "type": "github",
                        "message": f"Deleting from {repo_name} file {filename}" })
                    
                    delete_file_from_graph(repo_name, filename)

            elif status == "renamed":
                old_name = file.get("previous_filename")

                if old_name and old_name.endswith(".py"):
                    EVENT_QUEUE.put({
                        "type": "github",
                        "message": f"Deleting from {repo_name} file {filename}" })
                    
                    delete_file_from_graph(repo_name, old_name)

                if filename.endswith(".py"):
                    EVENT_QUEUE.put({
                        "type": "github",
                        "message": f"Adding from {repo_name} file {filename}" })
                    
                    self.process_python_file(repo, commit_hash, filename)

            elif status in {"added", "modified"}:
                if filename.endswith(".py"):
                    EVENT_QUEUE.put({
                        "type": "github",
                        "message": f"Adding from {repo_name} file {filename}" })
                    
                    self.process_python_file(repo, commit_hash, filename)


    def persist_candidate(self, candidate):
        enriched = enrich_function_with_llm(candidate)
        admitted = admit_function_llm(enriched, enriched["code"])

        if not admitted:
            return

        persist_function_to_graph(enriched, enriched["code"])
        persist_function_io(enriched)
        persist_function_attributes(enriched)


    def process_python_file(self, repo, commit_hash, file_path):
        source_code = get_file_content_from_commit(repo, file_path, commit_hash)

        delete_file_from_graph(repo.get("name"), file_path)

        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            return

        functions = extract_functions_from_tree(tree)

        for func, class_name, attributes, attribute_metadata, responsibility in functions:
            reads, writes = extract_method_attribute_usage(func)
            
            method_code = ast.get_source_segment(source_code, func)

            if class_name:
                function_id = f"{repo['name']}::{class_name}::{func.name}"
            else:
                function_id = f"{repo['name']}::Global::{func.name}"

            candidate = {
                "id": function_id,
                "name": func.name,
                "class": class_name or "Global",
                "class_attributes": attributes or [],
                "class_attribute_metadata": attribute_metadata or {},
                "class_responsibility": responsibility,
                "summary": "",
                "description": "",
                "steps": [],
                "inputs": [
                    {"name": arg.arg,
                    "type": "unknown",
                    "description": "" }
                    for arg in func.args.args
                    if arg.arg != "self" ],
                "outputs": [],
                "reads_attributes": reads or [],
                "writes_attributes": writes or [],
                "tags": [],
                "code": method_code,
                "source": f"{repo.get('name')}:{file_path}" }

            self.persist_candidate(candidate)
