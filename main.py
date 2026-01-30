import os
import logging
from utils.argument_parser import parse_arguments

def main():
    args = parse_arguments()

    if args.extract:
        try:
            from extractors.extractor import Extractor
        except ModuleNotFoundError as e:
            if e.name == "pptx":
                logging.error(
                    "Missing dependency 'python-pptx'. Install with: "
                    "`python3 -m pip install -r requirements.txt`"
                )
                raise SystemExit(2)
            raise
        extractor = Extractor(args.pptx_path)
        info_path = extractor.extract_info(args.output_dir)
        logging.info(f"Presentation information saved to: {info_path}")

    if args.recreate:
        try:
            from recreator.recreator import Recreator
        except ModuleNotFoundError as e:
            if e.name == "pptx":
                logging.error(
                    "Missing dependency 'python-pptx'. Install with: "
                    "`python3 -m pip install -r requirements.txt`"
                )
                raise SystemExit(2)
            raise
        info_path = args.info_path or os.path.join(
            args.output_dir, f"{os.path.basename(args.pptx_path).split('.')[0]}_info.json"
        )
        if os.path.isdir(info_path):
            raise IsADirectoryError(f"Info path must be a JSON file, got a directory: {info_path}")
        if not os.path.exists(info_path):
            raise FileNotFoundError(f"Info file not found: {info_path}")
        template_pptx_path = args.pptx_path if os.path.isfile(args.pptx_path) else None
        recreator = Recreator(info_path, template_pptx_path=template_pptx_path)

        output_path = None
        if args.output_pptx:
            candidate = os.path.expanduser(args.output_pptx)
            if os.path.isdir(candidate):
                output_path = None
            elif os.path.basename(candidate) == candidate:
                output_path = os.path.join(args.output_dir, candidate)
            else:
                output_path = candidate
            if output_path and not output_path.lower().endswith(".pptx"):
                output_path = f"{output_path}.pptx"

        output_pptx_path = recreator.recreate_pptx(args.output_dir, output_path=output_path)
        logging.info(f"New PPTX created at: {output_pptx_path}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    try:
        main()
    except Exception as e:
        logging.error(f"Error in main execution: {str(e)}")
        raise
