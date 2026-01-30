#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

PYTHON=""
if command -v python3.11 >/dev/null 2>&1; then
  PYTHON="python3.11"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
else
  echo "Error: No suitable Python found (need python3.11 or python3)." >&2
  exit 1
fi

if [[ ! -f "requirements.txt" ]]; then
  echo "Error: requirements.txt not found." >&2
  exit 1
fi

if [[ ! -d ".venv" ]]; then
  "$PYTHON" -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

export PIP_NO_CACHE_DIR=1
export PIP_DISABLE_PIP_VERSION_CHECK=1

python -m pip install -r requirements.txt

if [[ $# -eq 0 ]]; then
  python main.py -h
elif [[ "${1:-}" == "validate" || "${1:-}" == "validate-json" ]]; then
  shift
  python -m utils.validate_info_json "$@"
else
  # Validate --info-path if provided (common footgun: accidental line breaks).
  info_path=""
  output_pptx=""
  skip_next=0
  for arg in "$@"; do
    if [[ $skip_next -eq 1 ]]; then
      info_path="$arg"
      skip_next=0
      continue
    fi
    if [[ "$arg" == "--info-path" ]]; then
      skip_next=1
    fi
  done

  skip_next=0
  for arg in "$@"; do
    if [[ $skip_next -eq 1 ]]; then
      output_pptx="$arg"
      skip_next=0
      continue
    fi
    if [[ "$arg" == "--output-pptx" ]]; then
      skip_next=1
    fi
  done

  if [[ -n "$info_path" ]]; then
    if [[ -d "$info_path" ]]; then
      echo "Error: --info-path must be a JSON file, got a directory: $info_path" >&2
      echo "Example:" >&2
      echo "  ./run.sh dummy.pptx \"$REPO_ROOT/output\" --recreate --info-path \"/absolute/path/to/some_info.json\"" >&2
      exit 2
    fi
    if [[ ! -f "$info_path" ]]; then
      echo "Error: --info-path does not exist or is not a file: $info_path" >&2
      exit 2
    fi
  fi

  if [[ -n "$output_pptx" ]]; then
    if [[ -d "$output_pptx" ]]; then
      echo "Error: --output-pptx must be a file path (or filename), got a directory: $output_pptx" >&2
      exit 2
    fi
  fi

  # If this looks like a normal invocation, validate the output directory is writable
  # to avoid confusing Python stack traces (common when pointing at a volume root).
  if [[ "$*" != *" -h"* && "$*" != *" --help"* ]]; then
    positional=()
    skip_next=0
    for arg in "$@"; do
      if [[ $skip_next -eq 1 ]]; then
        skip_next=0
        continue
      fi
      case "$arg" in
        -h|--help|--extract|--recreate) ;;
        --info-path) skip_next=1 ;;
        --output-pptx) skip_next=1 ;;
        *) positional+=("$arg") ;;
      esac
    done

    if [[ ${#positional[@]} -ge 2 ]]; then
      output_dir="${positional[1]}"
      if [[ -e "$output_dir" && ! -d "$output_dir" ]]; then
        echo "Error: output_dir is not a directory: $output_dir" >&2
        exit 2
      fi

      if [[ ! -d "$output_dir" ]]; then
        mkdir -p "$output_dir" 2>/dev/null || true
      fi

      if [[ ! -d "$output_dir" || ! -w "$output_dir" ]]; then
        fallback_dir=""
        if [[ -d "$output_dir/_temp" && -w "$output_dir/_temp" ]]; then
          fallback_dir="$output_dir/_temp"
        else
          fallback_dir="$REPO_ROOT/output"
        fi

        mkdir -p "$fallback_dir"
        echo "Warning: output_dir is not writable: $output_dir" >&2
        echo "Using fallback output_dir: $fallback_dir" >&2

        new_args=()
        non_option_seen=0
        skip_next=0
        for arg in "$@"; do
          if [[ $skip_next -eq 1 ]]; then
            new_args+=("$arg")
            skip_next=0
            continue
          fi
          case "$arg" in
            -h|--help|--extract|--recreate)
              new_args+=("$arg")
              ;;
            --info-path)
              new_args+=("$arg")
              skip_next=1
              ;;
            --output-pptx)
              new_args+=("$arg")
              skip_next=1
              ;;
            *)
              non_option_seen=$((non_option_seen + 1))
              if [[ $non_option_seen -eq 2 ]]; then
                new_args+=("$fallback_dir")
              else
                new_args+=("$arg")
              fi
              ;;
          esac
        done

        python main.py "${new_args[@]}"
        exit 0
      fi
    fi
  fi
  python main.py "$@"
fi
