#!/usr/bin/env python3
"""
Analyze AIA State Championship PDF structure
Quick prototype to understand PDF format before building full parser
"""

import sys

try:
    import pdfplumber
except ImportError:
    print("ERROR: pdfplumber not installed")
    print("Install with: pip install pdfplumber")
    sys.exit(1)

def analyze_pdf(pdf_path):
    """Analyze PDF structure"""
    print(f"\n{'='*80}")
    print(f"Analyzing: {pdf_path}")
    print(f"{'='*80}\n")

    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total Pages: {len(pdf.pages)}")
        print("\nFirst 5 pages analysis:\n")

        for i, page in enumerate(pdf.pages[:5]):
            print(f"\n--- Page {i+1} ---")

            # Extract text
            text = page.extract_text()
            if text:
                lines = text.split('\n')[:10]  # First 10 lines
                print("First 10 lines of text:")
                for j, line in enumerate(lines, 1):
                    print(f"  {j:2d}: {line[:80]}")  # First 80 chars

            # Check for tables
            tables = page.extract_tables()
            print(f"\nTables found: {len(tables)}")
            if tables:
                print(f"First table dimensions: {len(tables[0])} rows x {len(tables[0][0]) if tables[0] else 0} cols")
                if tables[0]:
                    print("First few rows:")
                    for row in tables[0][:3]:
                        print(f"  {row}")

            print(f"\nPage dimensions: {page.width} x {page.height}")

if __name__ == "__main__":
    pdfs = [
        "aia-pdfs/2024-state-championships.pdf",
        "aia-pdfs/2020-state-championships.pdf",
        "aia-pdfs/2015-state-championships.pdf"
    ]

    for pdf_path in pdfs:
        try:
            analyze_pdf(pdf_path)
        except Exception as e:
            print(f"\nERROR analyzing {pdf_path}: {e}")

    print(f"\n{'='*80}")
    print("Analysis complete!")
    print(f"{'='*80}\n")


