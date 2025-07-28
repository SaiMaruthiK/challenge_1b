import os
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import List
from src.parser import parse_document
from src.engine import rank_and_refine_sections

def print_intro():
    print("🚀 ADOBE INDIA HACKATHON - DOCUMENT INTELLIGENCE")
    print("="*60)

def main():
    print_intro()
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--persona", required=True)
    parser.add_argument("--job", required=True)
    parser.add_argument("--top_k", type=int, default=5)
    args = parser.parse_args()

    input_dir = Path(args.input_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    pdfs: List[str] = sorted([f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")])
    print(f"\n📄 Found {len(pdfs)} PDFs.")

    all_sections = []
    for pdf in pdfs:
        path = input_dir / pdf
        try:
            sections = parse_document(path)
            for sec in sections:
                sec["document"] = pdf
            all_sections.extend(sections)
        except Exception as e:
            print(f"❌ Failed to parse {pdf}: {e}")

    if not all_sections:
        print("❌ No sections parsed.")
        return

    print(f"📊 Total sections: {len(all_sections)}")

    extracted, refined = rank_and_refine_sections(
        all_sections, args.persona, args.job, top_k=args.top_k
    )

    output = {
        "metadata": {
            "input_documents": pdfs,
            "persona": args.persona,
            "job_to_be_done": args.job,
            "processing_timestamp": datetime.utcnow().isoformat(),
        },
        "extracted_sections": extracted,
        "subsection_analysis": refined,
    }

    out_path = output_dir / "output.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Output saved to {out_path}")

if __name__ == "__main__":
    main()
