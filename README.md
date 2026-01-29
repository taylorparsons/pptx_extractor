# PPTX Utility Tool

The PPTX Utility Tool is a Python project that allows you to extract presentation information from a PowerPoint file (PPTX) and recreate the PPTX file using the extracted information. This tool can be useful for analyzing and manipulating PowerPoint presentations programmatically.

## Prerequisites

Before using this tool, make sure you have the following:

- Python 3.x installed on your system
- `python-pptx` library installed (`python3 -m pip install python-pptx`)

## Getting Started

From the project directory (repo root), choose one of the following:

### Option A (recommended): use `./run.sh`

`run.sh` creates/uses a local `.venv`, installs `requirements.txt`, then runs `main.py`.

```sh
chmod +x run.sh
./run.sh -h
```

### Option B: manual virtualenv setup

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py -h
```

## Usage

The PPTX Utility Tool provides two main functionalities: extracting presentation information and recreating the PPTX file.

### Extracting Presentation Information

To extract presentation information from a PPTX file, use the following command:

```sh
./run.sh <pptx_path> <output_dir> --extract
```

- `<pptx_path>`: Path to the PPTX file you want to extract information from.
- `<output_dir>`: Directory where the extracted information will be saved as a JSON file.

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

- `<pptx_path>`: Path to the PPTX file you want to recreate (used to determine the JSON file name).
- `<output_dir>`: Directory where the recreated PPTX file will be saved.

Example:
```sh
./run.sh presentation.pptx output --recreate
```

This command will look for the extracted information JSON file (`presentation_info.json`) in the `output` directory and use it to recreate the PPTX file. The recreated file will be saved as `recreated_presentation.pptx` in the `output` directory.

## Troubleshooting

If you encounter any issues or errors while using the PPTX Utility Tool, please check the following:

- Make sure you have installed the required dependencies (`python-pptx`).
- Ensure that you are providing the correct paths for the PPTX file and output directory.
- Check the error messages logged in the console for any specific details about the issue.

## License

This project is licensed under the [MIT License](LICENSE).
