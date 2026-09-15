import argparse
import json
from pathlib import Path

from classifier import process_document


def main():
    parser = argparse.ArgumentParser(
        description="Back Office Document Classification and Routing Agent"
    )
    parser.add_argument("command", choices=["classify"], help="Action to perform")
    parser.add_argument("path", help="Path to a PDF file or a folder of PDFs")
    parser.add_argument(
        "--batch", action="store_true", help="Treat path as a folder and process all PDFs in it"
    )
    args = parser.parse_args()

    if args.batch:
        folder = Path(args.path)
        pdf_files = sorted(folder.glob("*.pdf"))
        if not pdf_files:
            print(f"No PDF files found in {folder}")
            return
        results = []
        for pdf_file in pdf_files:
            print(f"Processing {pdf_file.name}...")
            results.append(process_document(str(pdf_file)))
        print(json.dumps(results, indent=2))
    else:
        result = process_document(args.path)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()