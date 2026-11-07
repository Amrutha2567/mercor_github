import ast
import json
import re
from pathlib import PurePosixPath
from typing import Iterable

SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", "dist",
             "build", "coverage", ".next", ".idea", ".pytest_cache"}
SKIP_NAMES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock",
              "Pipfile.lock", "Cargo.lock", "composer.lock"}
TEXT_EXTS = {".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".cpp", ".c", ".h",
             ".hpp", ".go", ".rs", ".rb", ".php", ".cs", ".swift", ".kt",
             ".scala", ".sql", ".sh", ".yaml", ".yml", ".toml", ".ini",
             ".md", ".rst", ".txt", ".json", ".xml", ".html", ".css",
             ".scss", ".dockerfile", ".tf", ".proto"}
PRIORITY = {"README.md": 10, "pyproject.toml": 9, "requirements.txt": 8,
            "Dockerfile": 8, "docker-compose.yml": 8, "package.json": 8,
            "main.py": 7, "app.py": 7}

def is_candidate(path: str) -> bool:
    p = PurePosixPath(path)
    if any(part in SKIP_DIRS for part in p.parts) or p.name in SKIP_NAMES:
        return False
    if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip",
                            ".whl", ".so", ".dll", ".exe", ".mp4", ".mp3",
                            ".parquet", ".db", ".sqlite"}:
        return False
    return p.name == "Dockerfile" or p.suffix.lower() in TEXT_EXTS or p.suffix.lower() == ".ipynb"

def priority(path: str) -> int:
    name = PurePosixPath(path).name
    score = PRIORITY.get(name, 1)
    if name.lower().startswith(("test_", "spec")) or "/tests/" in f"/{path}/":
        score += 2
    if any(x in path.lower() for x in ("src/", "app/", "lib/", "core/")):
        score += 2
    return score

def decode_text(raw: bytes) -> str:
    return raw.decode("utf-8", errors="replace")

def process_notebook(raw: bytes) -> str:
    try:
        nb = json.loads(decode_text(raw))
        cells = []
        for cell in nb.get("cells", []):
            if cell.get("cell_type") == "code":
                source = "".join(cell.get("source", []))
                if source.strip():
                    cells.append(source)
            elif cell.get("cell_type") == "markdown":
                source = "".join(cell.get("source", []))
                if source.strip():
                    cells.append("# Notebook notes\n" + source[:2500])
        return "\n\n".join(cells)
    except Exception:
        return "# Notebook could not be parsed"

def python_structure(source: str) -> str:
    """Add a compact structural index while retaining the source for semantic review."""
    try:
        tree = ast.parse(source)
        entries = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                entries.append(f"{type(node).__name__} {node.name} (line {node.lineno})")
        return "# Python structure\n" + "\n".join(entries[:250]) + "\n\n" + source
    except SyntaxError:
        return source

def prepare_file(path: str, raw: bytes) -> str:
    text = process_notebook(raw) if path.endswith(".ipynb") else decode_text(raw)
    if path.endswith(".py"):
        text = python_structure(text)
    # Strip excessive blank lines and trailing whitespace.
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text[:120_000]
