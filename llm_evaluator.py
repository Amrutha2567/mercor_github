import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.prompts import REPOSITORY_SYSTEM, repository_prompt, FINAL_PROMPT
from app.token_manager import chunk_text

WEIGHTS = {
    "architecture_system_design": 20,
    "algorithmic_complexity": 20,
    "backend_engineering_depth": 15,
    "data_structures_problem_solving": 15,
    "ai_ml_advanced_techniques": 10,
    "scalability_performance": 10,
    "testing_reliability_maintainability": 10,
}

class LLMUnavailable(RuntimeError):
    pass

class Evaluator:
    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise LLMUnavailable("OPENAI_API_KEY is not configured.")
        self.llm = ChatOpenAI(model=model, temperature=0, api_key=api_key)

    def _json(self, system: str, prompt: str) -> dict:
        response = self.llm.invoke([SystemMessage(content=system), HumanMessage(content=prompt)])
        content = response.content
        if isinstance(content, list):
            content = "".join(x.get("text", "") for x in content if isinstance(x, dict))
        text = str(content).strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
        return json.loads(text)

    def evaluate_repository(self, repo: dict, files: list[dict]) -> dict:
        # Each file is chunked independently; chunk-level notes are bounded before synthesis.
        chunk_notes = []
        for item in files:
            for index, chunk in enumerate(chunk_text(item["content"])):
                prompt = (f"Summarize only technically meaningful implementation evidence in this chunk. "
                          f"Return concise notes, preserve exact file path and symbols. "
                          f"File: {item['path']} | Chunk: {index + 1}\n\n{chunk}")
                msg = self.llm.invoke([
                    SystemMessage(content="You are a precise code-analysis assistant. Do not speculate."),
                    HumanMessage(content=prompt)
                ])
                chunk_notes.append({"path": item["path"], "content": str(msg.content)[:5000]})
        # Keep strongest/most relevant summaries under a second-stage budget.
        notes = chunk_notes[:100]
        result = self._json(REPOSITORY_SYSTEM, repository_prompt(repo, notes))
        scores = result.get("dimension_scores", {})
        normalized = {k: max(1, min(10, int(scores.get(k, 1)))) for k in WEIGHTS}
        weighted = sum(normalized[k] * w for k, w in WEIGHTS.items()) / 100
        result["dimension_scores"] = normalized
        result["weighted_score"] = round(weighted, 2)
        result["files_examined"] = len(files)
        result["chunks_summarized"] = len(chunk_notes)
        return result

    def compare(self, assessments: list[dict]) -> dict:
        compact = [{
            "full_name": a["repository"]["full_name"],
            "weighted_score": a["analysis"]["weighted_score"],
            "analysis": a["analysis"]
        } for a in assessments]
        result = self._json("You are an impartial senior engineering reviewer.", FINAL_PROMPT +
                            "\n\nAssessments:\n" + json.dumps(compact, ensure_ascii=False))
        # Guard against a hallucinated repository name.
        valid = {x["repository"]["full_name"] for x in assessments}
        if result.get("selected_full_name") not in valid:
            raise ValueError("Final comparison selected a repository outside the evaluated set.")
        return result
