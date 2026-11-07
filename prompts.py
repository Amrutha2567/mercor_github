REPOSITORY_SYSTEM = """You are a senior software architect conducting evidence-based code review.
Assess technical complexity, not popularity, repository size, commit count, or dependency count.
Only make claims supported by the supplied file excerpts. If evidence is insufficient, say so.
Return valid JSON only, matching the requested schema. Scores must be integers from 1 to 10."""

def repository_prompt(repo: dict, excerpts: list[dict]) -> str:
    evidence = "\n\n".join(
        f"### FILE: {x['path']}\n{x['content']}" for x in excerpts
    )
    return f"""Evaluate this GitHub repository.

Repository metadata:
- Name: {repo['full_name']}
- Description: {repo.get('description') or 'Not provided'}
- Primary language: {repo.get('language') or 'Not reported'}
- Stars: {repo.get('stargazers_count', 0)} (context only; do not score popularity)
- Files examined: {len(excerpts)}

Score each dimension from 1-10:
1. architecture_system_design
2. algorithmic_complexity
3. backend_engineering_depth
4. data_structures_problem_solving
5. ai_ml_advanced_techniques
6. scalability_performance
7. testing_reliability_maintainability

Weights respectively: 20, 20, 15, 15, 10, 10, 10 percent.
Provide JSON with keys:
"dimension_scores": object containing the seven exact keys and integer scores;
"technical_summary": string;
"strengths": array of strings;
"limitations": array of strings;
"evidence": array of objects with "file", "observation", "dimension";
"confidence": number from 0 to 1;
"insufficient_evidence": boolean.

Do not infer implementation details from dependencies alone. Distinguish implemented features from configuration or documentation.
If an area is not evidenced, use a conservative score and explain uncertainty.

Source excerpts:
{evidence}
"""

FINAL_PROMPT = """Compare repository assessments. Select the strongest demonstrated technical complexity,
not the largest or most popular repository. Consider confidence and evidence coverage.
Return JSON: {"selected_full_name": string, "reasoning": string,
"comparison": [{"full_name": string, "weighted_score": number, "key_distinction": string}]}.
Do not invent evidence or claim exhaustive inspection."""
