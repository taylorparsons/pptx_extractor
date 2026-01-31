![pptx_extractor banner](assets/readme-banner.svg)

# PPTX Utility Tool

Extract PPTX → JSON, edit safely, and recreate a styled deck (with SmartArt text support).

The PPTX Utility Tool is a Python project that allows you to extract presentation information from a PowerPoint file (PPTX) and recreate the PPTX file using the extracted information. This tool can be useful for analyzing and manipulating PowerPoint presentations programmatically.

## Why this exists (value)

If you need to update PowerPoint content but don’t want to hand-edit slides in PowerPoint (or you need to do repeatable/batch updates), this tool lets you:

- Extract a deck into a structured `*_info.json` file.
- Make edits in text form (great for “find/replace”, content ops, or having someone else update copy without touching slide layout).
- Recreate a new PPTX — optionally using the original PPTX as a template to preserve master slides, backgrounds, and SmartArt.

## Prerequisites

Before using this tool, make sure you have the following:

- Python 3.x installed on your system
- Dependencies installed in a virtualenv (use `./run.sh` or Option B below)

## Getting Started

From the project directory (repo root), choose one of the following:

### Option A (recommended): use `./run.sh`

`run.sh` creates/uses a local `.venv`, installs `requirements.txt`, then runs `main.py`.

```sh
chmod +x run.sh
./run.sh -h
```

### Option C: launch the web UI

If you prefer not to use the CLI, you can run a local Streamlit UI.  
**New users should first make the script executable with `chmod`:**

```sh
chmod +x run.sh
./run.sh ui
```

This installs UI-only dependencies from `requirements-ui.txt` (first run) **and starts the Streamlit app**. Follow the printed URL (usually `http://localhost:8501`).

#### Web UI quick guide

**Extract tab**
1. Choose a PPTX (upload or paste the path).
2. Pick an output directory.
3. Click **Run extract**.

**Validate / Filter JSON tab**
1. Upload or paste a `*_info.json` path.
2. Click **Validate JSON** (errors are shown with JSON paths).
3. Optionally filter slides/shape types and **Save filtered JSON**.

**Recreate tab**
1. (Recommended) Provide the original PPTX as a **template** so styling is preserved.
2. The JSON path is auto‑filled if you came from Extract/Validate.
3. Click **Run recreate** and use the **Open PPTX** link to open the output.

### Option B: manual virtualenv setup

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py -h
```

## Testing / Validation

This repo doesn’t currently have unit tests. Use these sanity checks instead:

### Quick sanity checks

```sh
# Syntax check all python modules in the repo
python3 -m compileall main.py extractors recreator utils

# Shellcheck equivalent (syntax only) for the wrapper script
bash -n run.sh
```

### Validate edited JSON before recreating

If you hand-edit a `*_info.json`, validate it before running `--recreate`:

```sh
./run.sh validate /path/to/some_info.json
```

### End-to-end (extract + recreate)

```sh
# Extract to a throwaway directory
./run.sh path/to/presentation.pptx /tmp/pptx_extract_out --extract

# Recreate from the extracted JSON (template-based if the PPTX exists)
./run.sh path/to/presentation.pptx /tmp/pptx_extract_out --recreate
```

If you moved/renamed the extracted JSON, recreate using `--info-path`:

```sh
./run.sh path/to/presentation.pptx /tmp/pptx_extract_out --recreate --info-path /path/to/some_info.json
```

## Usage

The PPTX Utility Tool provides two main functionalities: extracting presentation information and recreating the PPTX file.

### Extracting Presentation Information

To extract presentation information from a PPTX file, use the following command:

```sh
./run.sh <pptx_path> <output_dir> --extract
```

- `<pptx_path>`: Path to the PPTX file you want to extract information from.
- `<output_dir>`: Directory where the extracted information will be saved as a JSON file (must be writable). If it isn’t writable (common when pointing at a volume root), `run.sh` falls back to `./output`.

Example:
```sh
./run.sh presentation.pptx output --extract
```

This command will extract the presentation information from `presentation.pptx` and save it as a JSON file in the `output` directory.

### Recreating the PPTX File

To recreate the PPTX file using the extracted information, use the following command:

```sh
./run.sh <pptx_path> <output_dir> --recreate
```

- `<pptx_path>`: Path to the PPTX file you want to recreate (used to determine the JSON file name). If this file exists, it is used as a template to preserve slide masters/backgrounds.
- `<output_dir>`: Directory where the recreated PPTX file will be saved.

Example:
```sh
./run.sh presentation.pptx output --recreate
```

This command will look for the extracted information JSON file (`<pptx_basename>_info.json`) in the `output_dir` and use it to recreate the PPTX file. The output is saved as `recreated_<pptx_basename>.pptx` (or `recreated_<json_stem>.pptx` when using `--info-path`).

### Recreating from a specific JSON file

If you moved/renamed the extracted JSON file, you can pass it explicitly:

```sh
./run.sh anything.pptx output --recreate --info-path /path/to/some_info.json
```

Tip: If you want to preserve SmartArt/backgrounds, pass the original `.pptx` as `<pptx_path>` (so it can be used as a template) even when using `--info-path`.  
Also, extracted JSON now stores a template hint (`source_pptx`); if the original PPTX still exists at that path (or next to the JSON), recreate will automatically use it to keep styling.

### Recreating with a specific output filename

```sh
./run.sh anything.pptx output --recreate --info-path /path/to/some_info.json --output-pptx recreated_custom_name.pptx
```

## Limitations

 - SmartArt/diagram shapes are extracted as text blocks.
  - SmartArt is not recreated as *new editable SmartArt* from JSON alone (python-pptx limitation).
  - If you recreate **from a template PPTX** (recommended), the tool preserves the SmartArt and can update its text by editing the underlying diagram XML.
  - If you recreate **without a template PPTX**, diagram text blocks are rendered as simple textboxes so the deck isn’t “empty-looking”.

## Troubleshooting

If you encounter any issues or errors while using the PPTX Utility Tool, please check the following:

- Make sure you have installed the required dependencies (`python-pptx`).
- Ensure that you are providing the correct paths for the PPTX file and output directory.
- If you pass a path to `--info-path`, keep it on one shell line and quote it:
  - Good: `./run.sh dummy.pptx out --recreate --info-path "~/REI_Principal_PM_Flashcards_info.json"`
- Check the error messages logged in the console for any specific details about the issue.

## License

This project is licensed under the [MIT License](LICENSE).
