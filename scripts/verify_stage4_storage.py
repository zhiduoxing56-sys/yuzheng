from __future__ import annotations

import argparse
import re
import sqlite3
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--database", default="data/database/yuzheng.db", type=Path
    )
    args = parser.parse_args()
    connection = sqlite3.connect(args.database)
    try:
        values: list[str] = []
        values.extend(row[0] for row in connection.execute("SELECT record_json FROM audit_records"))
        values.extend(
            row[0] for row in connection.execute("SELECT payload_json FROM turn_workflow_events")
        )
        values.extend(
            row[0] for row in connection.execute("SELECT result_json FROM vehicle_execution_events")
        )
    finally:
        connection.close()
    raw_pattern = re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")
    print(
        {
            "serialized_rows_scanned": len(values),
            "raw_token_pattern_hits": sum(bool(raw_pattern.search(value)) for value in values),
            "non_null_authorization_token_fields": sum(
                '"authorization_token":"' in value for value in values
            ),
        }
    )


if __name__ == "__main__":
    main()
