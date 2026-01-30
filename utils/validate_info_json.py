from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from utils.info_json_validator import validate_info_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a PPTX extracted info JSON (v2) and print actionable errors.",
    )
    parser.add_argument(
        "json_path",
        help="Path to the extracted *_info.json file",
    )
    args = parser.parse_args(argv)

    path = Path(args.json_path).expanduser()
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 2
    if path.is_dir():
        print(f"Error: expected a JSON file, got a directory: {path}", file=sys.stderr)
        return 2

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        return 2

    errors = validate_info_json(data)
    if not errors:
        print("OK: JSON matches expected schema (v2) enough to recreate.")
        return 0

    print(f"Found {len(errors)} issue(s):", file=sys.stderr)
    for err in errors:
        print(f"- {err}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

