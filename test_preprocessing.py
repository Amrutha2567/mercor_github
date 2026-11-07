from app.preprocessing import is_candidate, process_notebook

def test_filters_generated_and_binary_paths():
    assert not is_candidate("node_modules/pkg/index.js")
    assert not is_candidate("assets/logo.png")
    assert is_candidate("src/main.py")

def test_notebook_drops_outputs():
    raw = b'{"cells":[{"cell_type":"code","source":["print(1)"],"outputs":[{"data":"large"}]}]}'
    assert "print(1)" in process_notebook(raw)
    assert "large" not in process_notebook(raw)
