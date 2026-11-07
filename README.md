# GitHub Repository Complexity Analyzer

A Python/FastAPI + LangChain application that evaluates public repositories from a GitHub profile and selects the repository with the strongest demonstrated technical complexity.

## Important honesty note

This is a starter implementation, not a verified production deployment. Run the tests, configure API keys, and validate output quality before submitting. It does not claim exhaustive inspection: GitHub trees can be truncated, files are capped, and token budgets intentionally limit source coverage.

## Architecture

1. Parse a GitHub profile URL and fetch non-fork, non-archived repositories.
2. Retrieve repository trees and prioritize source, tests, configuration, and documentation.
3. Exclude generated folders, binaries, dependency lockfiles, and oversized files.
4. Extract notebook code/Markdown while discarding cell outputs; add Python AST structure.
5. Apply per-repository token budgets and line-aware overlapping chunks.
6. Use LangChain/OpenAI to summarize chunks and assess repository dimensions.
7. Calculate weighted scores in Python and ask GPT for an evidence-based comparison.
8. Validate that the selected repository belongs to the evaluated set.

## Scoring rubric

| Dimension | Weight |
|---|---:|
| Architecture and system design | 20% |
| Algorithmic complexity | 20% |
| Backend engineering depth | 15% |
| Data structures and problem solving | 15% |
| AI/ML advanced techniques | 10% |
| Scalability and performance | 10% |
| Testing, reliability and maintainability | 10% |

Popularity, stars, file count, and dependency count are context only and are not scoring dimensions.

## Run locally

Python 3.11 recommended.

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Set OPENAI_API_KEY and optionally GITHUB_TOKEN
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

In another terminal:

```bash
streamlit run frontend/streamlit_app.py
```

Set the backend URL in the Streamlit page if it is not `http://localhost:8000`.

## Test

```bash
pytest -q
```

Tests are starter coverage and should be expanded with mocked GitHub API responses, rate-limit cases, truncated trees, large files, malformed notebooks, and LLM JSON failures.

## Deploy

### Backend on Render
1. Push this project to a GitHub repository.
2. Create a Render Web Service from the repository; choose Docker.
3. Add `OPENAI_API_KEY`, `GITHUB_TOKEN`, and optionally `OPENAI_MODEL` as environment variables.
4. Deploy and verify `/health` and `/docs`.

### Frontend on Streamlit Community Cloud
1. Push the project to GitHub.
2. Create a Streamlit app with entrypoint `frontend/streamlit_app.py`.
3. Set `API_URL` to the deployed Render backend URL in app secrets/environment.
4. Deploy and test a profile URL end-to-end.

## YouTube demo outline (3–5 minutes)

1. Introduce the problem and show the deployed interface.
2. Submit a public GitHub profile URL.
3. Explain repository discovery and file exclusions.
4. Show notebook cleanup, token budgets, chunking, and hierarchical summaries in code.
5. Show dimension scores, cited file evidence, and final comparison.
6. Mention limitations honestly: public repositories only, sampled files, API limits, model variability, and no claim of exhaustive analysis.

## Engineering limitations and next improvements

- Add async/concurrent repository fetching with bounded concurrency and retry/backoff.
- Cache immutable GitHub tree/content responses to reduce API calls.
- Use a stronger relevance-ranking stage before token-budget allocation.
- Replace per-chunk raw summaries with structured symbol-aware summaries and a map-reduce synthesis stage.
- Add robust JSON schema validation/retry for LLM responses.
- Add secret scanning and sensitive-file exclusions before sending code to an external model.
- Use a persistent job queue for long profile analyses; current synchronous API may time out on large profiles.
- Record analyzed file paths and skipped-file reasons in output for auditability.
- Add rate limiting, request authentication, and cost controls before public deployment.

## Security

Never commit `.env` or expose API keys in browser code. Only analyze repositories you are authorized to inspect. Review applicable privacy and data-handling requirements before sending repository code to an external LLM.
