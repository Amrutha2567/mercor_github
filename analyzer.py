from app.github_client import GitHubClient
from app.preprocessing import is_candidate, priority, prepare_file
from app.token_manager import fit_token_budget
from app.llm_evaluator import Evaluator

def analyze_profile(profile_url: str, settings) -> dict:
    client = GitHubClient(settings.github_token, settings.request_timeout)
    from app.github_client import username_from_url
    username = username_from_url(profile_url)
    repos = client.repositories(username, settings.max_repos)
    if not repos:
        raise ValueError("No eligible non-fork, non-archived repositories were found.")
    evaluator = Evaluator(settings.openai_api_key, settings.openai_model)
    assessments = []
    for repo in repos:
        branch = repo.get("default_branch") or "main"
        tree = client.tree(repo["full_name"], branch)
        candidates = [x for x in tree if x.get("type") == "blob" and is_candidate(x["path"])]
        candidates.sort(key=lambda x: (priority(x["path"]), x.get("size", 0)), reverse=True)
        files = []
        for node in candidates[:settings.max_files_per_repo]:
            if node.get("size", 0) > 1_000_000:
                continue
            try:
                raw = client.file_content(node["url"])
                content = prepare_file(node["path"], raw)
                if content.strip():
                    files.append({"path": node["path"], "content": content})
            except Exception:
                # Individual inaccessible or malformed files should not abort the repository.
                continue
        files = fit_token_budget(files, settings.repo_token_budget)
        if not files:
            continue
        analysis = evaluator.evaluate_repository(repo, files)
        assessments.append({"repository": {
            "full_name": repo["full_name"], "html_url": repo["html_url"],
            "description": repo.get("description"), "language": repo.get("language"),
            "stars": repo.get("stargazers_count", 0)
        }, "analysis": analysis})
    if not assessments:
        raise ValueError("No repositories contained analyzable text files.")
    comparison = evaluator.compare(assessments)
    selected = next(x for x in assessments
                    if x["repository"]["full_name"] == comparison["selected_full_name"])
    return {"username": username, "repositories_analyzed": len(assessments),
            "assessments": assessments, "winner": selected, "comparison": comparison}
