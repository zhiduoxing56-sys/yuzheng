from __future__ import annotations

import argparse
import json
import subprocess
import zipfile
from pathlib import Path, PurePosixPath


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "tmp",
    "secrets",
    ".cache",
    "huggingface",
    "snapshots",
}
FORBIDDEN_PREFIXES = {
    "data/database",
    "data/secrets",
    "data/models",
}
FORBIDDEN_SUFFIXES = {".db", ".db-wal", ".db-shm", ".pyc", ".pyo"}


def _tracked_files() -> list[PurePosixPath]:
    completed = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
    )
    return [
        PurePosixPath(value.decode("utf-8"))
        for value in completed.stdout.split(b"\0")
        if value
    ]


def _allowed(path: PurePosixPath) -> bool:
    text = path.as_posix()
    lowered_parts = {part.lower() for part in path.parts}
    if lowered_parts & FORBIDDEN_PARTS:
        return False
    if any(text == prefix or text.startswith(prefix + "/") for prefix in FORBIDDEN_PREFIXES):
        return False
    return not any(text.lower().endswith(suffix) for suffix in FORBIDDEN_SUFFIXES)


def export(output: Path) -> dict[str, object]:
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    included = [path for path in _tracked_files() if _allowed(path)]
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative in included:
            source = PROJECT_ROOT / relative.as_posix()
            if source.is_file() and source.resolve() != output:
                archive.write(source, relative.as_posix())
    with zipfile.ZipFile(output) as archive:
        unsafe = [name for name in archive.namelist() if not _allowed(PurePosixPath(name))]
        if unsafe:
            raise RuntimeError(f"打包结果包含禁止路径: {unsafe}")
        names = archive.namelist()
    return {"output": str(output), "file_count": len(names), "forbidden_entry_count": 0}


def main() -> int:
    parser = argparse.ArgumentParser(description="导出不含本地密钥、数据库和缓存的源码包")
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "dist" / "yuzheng-source.zip",
    )
    args = parser.parse_args()
    print(json.dumps(export(args.output), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
