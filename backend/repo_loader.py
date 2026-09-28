"""RepoMentor - Week 1 Day 4: clone a GitHub repo and list the useful files."""
import os
import shutil
import stat
from pathlib import Path
from urllib.parse import urlparse

from git import GitCommandError, Repo

CLONE_DIR = Path("cloned_repos")

# Folders we never want to read
SKIP_DIRS = {
    ".git", "node_modules", "venv", ".venv", "env", "__pycache__",
    "dist", "build", "out", "target", ".next", ".idea", ".vscode", "coverage",
    ".github", ".devcontainer",
}
# Extensions we skip (images, binaries, archives, lock/minified files)
SKIP_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp", ".bmp",
    ".pdf", ".zip", ".tar", ".gz", ".rar", ".7z",
    ".exe", ".dll", ".so", ".bin", ".class", ".jar", ".pyc",
    ".mp3", ".mp4", ".mov", ".woff", ".woff2", ".ttf", ".eot",
    ".lock", ".map", ".min.js", ".min.css",
}
SKIP_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "poetry.lock", "Pipfile.lock", "composer.lock",
    "LICENSE", "LICENSE.txt", ".editorconfig",
}
MAX_FILE_SIZE = 200 * 1024  # 200 KB - bigger files are usually generated/data


def parse_repo_url(url: str) -> tuple[str, str]:
    """'https://github.com/owner/repo(.git)' -> ('owner', 'repo'). Raises ValueError if invalid."""
    parsed = urlparse(url.strip())
    if parsed.netloc not in ("github.com", "www.github.com"):
        raise ValueError("Only github.com links are supported")
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        raise ValueError("Link should look like https://github.com/owner/repo")
    owner, repo = parts[0], parts[1].removesuffix(".git")
    return owner, repo


def _force_remove(func, path, _exc):
    """Windows keeps .git files read-only; this lets rmtree delete them."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def clone_repo(url: str, fresh: bool = False) -> Path:
    """Shallow-clone the repo into cloned_repos/owner__repo and return its path."""
    owner, repo = parse_repo_url(url)
    dest = CLONE_DIR / f"{owner}__{repo}"

    if dest.exists():
        if not fresh:
            return dest  # already cloned
        shutil.rmtree(dest, onerror=_force_remove)

    CLONE_DIR.mkdir(exist_ok=True)
    try:
        Repo.clone_from(f"https://github.com/{owner}/{repo}.git", dest, depth=1)
    except GitCommandError as e:
        raise RuntimeError("Clone failed. Repo private-a irukkalaam or link thappa irukkalaam.") from e
    return dest


def _is_binary(path: Path) -> bool:
    """A file with a null byte in the first 1KB is treated as binary."""
    try:
        with open(path, "rb") as f:
            return b"\0" in f.read(1024)
    except OSError:
        return True


def get_code_files(repo_path: Path) -> list[Path]:
    """Walk the repo and return only files worth indexing."""
    files = []
    for root, dirs, filenames in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]  # prune skipped folders
        for name in filenames:
            p = Path(root) / name
            if name in SKIP_FILES:
                continue
            if any(name.lower().endswith(ext) for ext in SKIP_EXTS):
                continue
            if p.stat().st_size > MAX_FILE_SIZE or _is_binary(p):
                continue
            files.append(p)
    return files


if __name__ == "__main__":
    path = clone_repo("https://github.com/pallets/click")
    files = get_code_files(path)
    print(f"Cloned to: {path}")
    print(f"{len(files)} files kept")
    for f in files[:15]:
        print(" ", f.relative_to(path))