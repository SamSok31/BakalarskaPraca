import os
import requests
import base64


def github_get(path: str, params=None):
    if path.startswith("http"):
        raise ValueError(f"github_get received full URL: {path}")

    GITHUB_API_BASE = "https://api.github.com"
    url = f"{GITHUB_API_BASE}{path}"

    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    if not GITHUB_TOKEN:
        raise RuntimeError("GITHUB_TOKEN not found in environment")

    headers = {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
            "Accept": "application/vnd.github+json" }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def get_latest_commit_sha(repo: dict) -> str | None:
    owner = repo["owner"]
    name = repo["name"]

    try:
        commits = github_get(f"/repos/{owner}/{name}/commits",params={"per_page": 1})
    except requests.HTTPError as e:
        if e.response.status_code == 409:
            return None
        raise

    if not commits:
        return None

    return commits[0]["sha"]


def get_changed_files_from_commit(repo: dict, commit_sha: str) -> list[dict]:
    owner, name = repo["full_name"].split("/")

    data = github_get(f"/repos/{owner}/{name}/commits/{commit_sha}")

    return [{
            "filename": f["filename"],
            "status": f["status"],
            "previous_filename": f.get("previous_filename") }
            for f in data.get("files", []) ]


def get_file_content_from_commit(repo: dict, file_path: str, commit_sha: str) -> str:
    owner = repo["owner"]
    name = repo["name"]

    data = github_get(
        f"/repos/{owner}/{name}/contents/{file_path}",
        params={"ref": commit_sha} )

    if data.get("encoding") != "base64":
        raise ValueError("Unsupported file encoding")

    content = base64.b64decode(data["content"]).decode("utf-8")
    return content
