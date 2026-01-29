import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="PPTX Utility Tool")
    parser.add_argument("pptx_path", help="Path to the PPTX file to be processed.")
    parser.add_argument("output_dir", help="Directory to save the output files.")
    parser.add_argument("--extract", action="store_true", help="Extract presentation information.")
    parser.add_argument("--recreate", action="store_true", help="Recreate PPTX from extracted information.")
    return parser.parse_args()