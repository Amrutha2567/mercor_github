import re
import requests
from typing import Any

API = "https://api.github.com"

class GitHubError(RuntimeError):
    pass

def username_from_url(url: str) -> str:
    match = re.match(r"^https?://(?:www\.)?github\.com/([A-Za-z0-9-]+)/?(?:\?.*)?$", url.strip())
    if not match:
        raise ValueError("Enter a GitHub profile URL such as https://github.com/octocat")
    return match.group(1)

class GitHubClient:
    def __init__(self, token: str = "", timeout: int = 30):
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/vnd.github+json",
                                     "X-GitHub-Api-Version": "2022-11-28"})
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
        self.timeout = timeout

    def _get(self, url: str, params: dict | None = None) -> Any:
        response = self.session.get(url, params=params, timeout=self.timeout)
        if response.status_code == 404:
            raise GitHubError("GitHub user or repository not found.")
        if response.status_code == 403:
            raise GitHubError("GitHub API rate limit or access restriction. Add a GITHUB_TOKEN and retry.")
        response.raise_for_status()
        return response.json()

    def repositories(self, username: str, limit: int = 30) -> list[dict]:
        repos, page = [], 1
        while len(repos) < limit:
            batch = self._get(f"{API}/users/{username}/repos",
                              {"per_page": min(100, limit), "page": page, "sort": "updated"})
            if not batch:
                break
            repos.extend(batch)
            page += 1
        return [r for r in repos[:limit] if not r.get("fork") and not r.get("archived")]

    def tree(self, full_name: str, branch: str) -> list[dict]:
        data = self._get(f"{API}/repos/{full_name}/git/trees/{branch}", {"recursive": "1"})
        if data.get("truncated"):
            # GitHub truncates very large trees; caller still receives the available entries.
            pass
        return data.get("tree", [])

    def file_content(self, url: str) -> bytes:
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.content
