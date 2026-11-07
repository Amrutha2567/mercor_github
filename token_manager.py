import re

def count_tokens(text: str) -> int:
    """Use tiktoken when installed; conservative fallback otherwise."""
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        return max(1, len(re.findall(r"\w+|[^\w\s]", text)))

def chunk_text(text: str, max_tokens: int = 2500, overlap_tokens: int = 150) -> list[str]:
    """Line-aware chunking with a bounded overlap; never returns an empty chunk."""
    lines = text.splitlines()
    chunks, current = [], []
    current_tokens = 0
    for line in lines:
        line_tokens = count_tokens(line)
        if current and current_tokens + line_tokens > max_tokens:
            chunks.append("\n".join(current))
            overlap, overlap_count = [], 0
            for old in reversed(current):
                n = count_tokens(old)
                if overlap_count + n > overlap_tokens:
                    break
                overlap.insert(0, old)
                overlap_count += n
            current = overlap
            current_tokens = overlap_count
        # Split a single oversized line to keep hard bounds.
        if line_tokens > max_tokens:
            words, part = line.split(), []
            for word in words:
                if count_tokens(" ".join(part + [word])) > max_tokens and part:
                    if current:
                        chunks.append("\n".join(current))
                        current, current_tokens = [], 0
                    chunks.append(" ".join(part))
                    part = [word]
                else:
                    part.append(word)
            line = " ".join(part)
            line_tokens = count_tokens(line)
        current.append(line)
        current_tokens += line_tokens
    if current:
        chunks.append("\n".join(current))
    return [c for c in chunks if c.strip()]

def fit_token_budget(files: list[dict], budget: int) -> list[dict]:
    """Greedy priority-based budget allocation. Input should already be sorted."""
    selected, used = [], 0
    for item in files:
        cost = count_tokens(item["content"])
        if used + cost <= budget:
            selected.append(item)
            used += cost
        elif not selected and budget > 0:
            # Keep a truncated representative slice for at least one informative file.
            words = item["content"].split()
            low, high = 0, len(words)
            while low < high:
                mid = (low + high + 1) // 2
                if count_tokens(" ".join(words[:mid])) <= budget:
                    low = mid
                else:
                    high = mid - 1
            if low:
                selected.append({**item, "content": " ".join(words[:low])})
                used = count_tokens(selected[0]["content"])
    return selected
