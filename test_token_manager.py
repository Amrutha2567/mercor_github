from app.token_manager import chunk_text, count_tokens, fit_token_budget

def test_chunking_respects_budget_approximately():
    chunks = chunk_text("\n".join(["word " * 30 for _ in range(40)]), max_tokens=100, overlap_tokens=10)
    assert chunks
    assert all(count_tokens(x) <= 110 for x in chunks)

def test_budget_selects_files():
    files = [{"path": "a.py", "content": "alpha beta"},
             {"path": "b.py", "content": "gamma delta"}]
    result = fit_token_budget(files, 100)
    assert len(result) == 2
