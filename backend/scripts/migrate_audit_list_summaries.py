from __future__ import annotations

import argparse
import hashlib
import shutil
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_ROOT.parent
sys.path.insert(0, str(BACKEND_ROOT))

from app.models.schemas import AuditDatabaseRole  # noqa: E402
from app.services.audit.repository import AuditRepository  # noqa: E402


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def command_count(path: Path) -> int:
    with sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True) as connection:
        return int(
            connection.execute(
                "SELECT COUNT(*) FROM audit_records WHERE record_type = 'COMMAND'"
            ).fetchone()[0]
        )


def make_backup(database: Path, backup_dir: Path) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    backup = backup_dir / f"{database.stem}-pre-audit-summary-{stamp}{database.suffix}"
    shutil.copy2(database, backup)
    if file_digest(database) != file_digest(backup):
        backup.unlink(missing_ok=True)
        raise RuntimeError("database backup digest mismatch")
    return backup


def restore_database(database: Path, backup: Path) -> None:
    if not backup.is_file():
        raise FileNotFoundError(f"backup not found: {backup}")
    replacement = database.with_suffix(database.suffix + ".restore")
    shutil.copy2(backup, replacement)
    if file_digest(backup) != file_digest(replacement):
        replacement.unlink(missing_ok=True)
        raise RuntimeError("restore copy digest mismatch")
    replacement.replace(database)


def migrate(database: Path, backup_dir: Path) -> dict[str, object]:
    if not database.is_file():
        raise FileNotFoundError(f"database not found: {database}")
    before_count = command_count(database)
    backup = make_backup(database, backup_dir)
    try:
        repository = AuditRepository(
            database, database_role=AuditDatabaseRole.PRODUCTION
        )
        result = repository.backfill_audit_list_summaries()
        after_count = command_count(database)
        if before_count != after_count:
            raise RuntimeError(
                f"audit count changed: before={before_count}, after={after_count}"
            )
    except Exception:
        restore_database(database, backup)
        raise
    return {
        "database": str(database),
        "backup": str(backup),
        "before_count": before_count,
        "after_count": after_count,
        **result,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Back up and idempotently backfill compact audit-list summaries."
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=PROJECT_ROOT / "data" / "database" / "yuzheng.db",
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "database" / "backups",
    )
    parser.add_argument(
        "--restore-from",
        type=Path,
        help="Restore a previously created backup instead of migrating.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    database = args.database.resolve()
    if args.restore_from is not None:
        restore_database(database, args.restore_from.resolve())
        print(f"restored_database={database}")
        return 0
    result = migrate(database, args.backup_dir.resolve())
    for key, value in result.items():
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
