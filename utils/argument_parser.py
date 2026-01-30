import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="PPTX Utility Tool")
    parser.add_argument("pptx_path", help="Path to the PPTX file to be processed.")
    parser.add_argument("output_dir", help="Directory to save the output files.")
    parser.add_argument("--extract", action="store_true", help="Extract presentation information.")
    parser.add_argument("--recreate", action="store_true", help="Recreate PPTX from extracted information.")
    parser.add_argument(
        "--info-path",
        dest="info_path",
        help="Path to a specific extracted JSON file to use for --recreate (overrides the default <output_dir>/<pptx_basename>_info.json).",
    )
    parser.add_argument(
        "--output-pptx",
        dest="output_pptx",
        help="Output .pptx path (or filename) for --recreate. If a filename is provided, it is written under output_dir.",
    )
    return parser.parse_args()
