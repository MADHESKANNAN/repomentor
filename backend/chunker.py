"""RepoMentor - Week 1 Day 5: split files into chunks with file path + start/end line."""
import ast
from dataclasses import dataclass, asdict
from pathlib import Path

from repo_loader import clone_repo, get_code_files

MAX_LINES = 60        # size of a fallback block
OVERLAP = 10          # lines shared between neighbouring blocks
MAX_FUNC_LINES = 120  # functions longer than this get split
BIG_CLASS_LINES = 150 # classes longer than this get split into methods


@dataclass
class Chunk:
    file_path: str   # relative to repo root, e.g. "src/click/core.py"
    start_line: int  # 1-based, inclusive
    end_line: int    # 1-based, inclusive
    kind: str        # "function" | "class" | "module" | "block"
    text: str

    def to_dict(self) -> dict:
        return asdict(self)


def line_chunks(lines: list[str], rel_path: str, first_line: int = 1, kind: str = "block") -> list[Chunk]:
    """Fixed-size overlapping windows. Used for non-Python files and oversized code."""
    chunks = []
    step = MAX_LINES - OVERLAP
    i = 0
    while i < len(lines):
        part = lines[i:i + MAX_LINES]
        if any(l.strip() for l in part):  # skip all-blank windows
            chunks.append(Chunk(
                rel_path,
                first_line + i,
                first_line + i + len(part) - 1,
                kind,
                "\n".join(part),
            ))
        if i + MAX_LINES >= len(lines):
            break
        i += step
    return chunks


def _make(lines, rel_path, start, end, kind) -> list[Chunk]:
    seg = lines[start - 1:end]
    if not any(l.strip() for l in seg):
        return []
    if kind == "function" and len(seg) > MAX_FUNC_LINES:
        return line_chunks(seg, rel_path, first_line=start, kind="function")
    return [Chunk(rel_path, start, end, kind, "\n".join(seg))]


def python_chunks(source: str, rel_path: str) -> list[Chunk]:
    """One chunk per top-level function/class (big classes -> header + one per method)."""
    lines = source.splitlines()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return line_chunks(lines, rel_path)

    func_types = (ast.FunctionDef, ast.AsyncFunctionDef)
    spans = []  # (start, end, kind)

    def node_start(n):
        return min([n.lineno] + [d.lineno for d in getattr(n, "decorator_list", [])])

    for node in tree.body:
        if isinstance(node, func_types):
            spans.append((node_start(node), node.end_lineno, "function"))
        elif isinstance(node, ast.ClassDef):
            start, end = node_start(node), node.end_lineno
            methods = [n for n in node.body if isinstance(n, func_types)]
            if end - start + 1 > BIG_CLASS_LINES and methods:
                first = min(node_start(m) for m in methods)
                spans.append((start, first - 1, "class"))  # class header + docstring
                for m in methods:
                    spans.append((node_start(m), m.end_lineno, "function"))
            else:
                spans.append((start, end, "class"))

    spans.sort()
    chunks, cursor = [], 1
    for start, end, kind in spans:
        if start > cursor:  # code between definitions: imports, constants...
            chunks += _make(lines, rel_path, cursor, start - 1, "module")
        chunks += _make(lines, rel_path, start, end, kind)
        cursor = max(cursor, end + 1)
    if cursor <= len(lines):
        chunks += _make(lines, rel_path, cursor, len(lines), "module")
    return chunks


def chunk_file(path: Path, repo_root: Path) -> list[Chunk]:
    rel = path.relative_to(repo_root).as_posix()
    source = path.read_text(encoding="utf-8", errors="ignore")
    if not source.strip():
        return []
    if path.suffix == ".py":
        return python_chunks(source, rel)
    return line_chunks(source.splitlines(), rel)


def chunk_repo(repo_path: Path) -> list[Chunk]:
    chunks = []
    for f in get_code_files(repo_path):
        chunks += chunk_file(f, repo_path)
    return chunks


if __name__ == "__main__":
    repo = clone_repo("https://github.com/pallets/click")
    chunks = chunk_repo(repo)
    print(f"Total chunks: {len(chunks)}")

    kinds = {}
    for c in chunks:
        kinds[c.kind] = kinds.get(c.kind, 0) + 1
    print("By kind:", kinds)

    print("\nSample chunks:")
    for c in chunks[:8]:
        print(f"  {c.file_path}:{c.start_line}-{c.end_line}  [{c.kind}]")

    # Sanity check: show the first function chunk
    fn = next(c for c in chunks if c.kind == "function")
    print(f"\n--- {fn.file_path}:{fn.start_line}-{fn.end_line} ---")
    print(fn.text[:400])
