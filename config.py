import os
from dataclasses import dataclass

@dataclass
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    max_repos: int = int(os.getenv("MAX_REPOS", "30"))
    max_files_per_repo: int = int(os.getenv("MAX_FILES_PER_REPO", "80"))
    repo_token_budget: int = int(os.getenv("REPO_TOKEN_BUDGET", "18000"))
    chunk_tokens: int = int(os.getenv("CHUNK_TOKENS", "2500"))
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "30"))

settings = Settings()
