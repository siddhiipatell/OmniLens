"""
scripts/ingest_sample_data.py
─────────────────────────────
Ingests the sample files from sample_data/ into OmniLens.
Run this after `uvicorn backend.main:app` is running.

Usage:
    python scripts/ingest_sample_data.py
"""
import os
import requests

API_BASE = "http://localhost:8000"
SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "sample_data")
COLLECTION = "omnilens_demo"

SUPPORTED_EXTS = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".mp3", ".wav", ".m4a"}


def ingest_file(filepath: str):
    filename = os.path.basename(filepath)
    ext = os.path.splitext(filename)[1].lower()

    if ext not in SUPPORTED_EXTS:
        print(f"  ⚠ Skipping unsupported file: {filename}")
        return

    with open(filepath, "rb") as f:
        r = requests.post(
            f"{API_BASE}/ingest/",
            files={"file": (filename, f)},
            data={"collection": COLLECTION},
        )

    if r.ok:
        d = r.json()
        print(f"  ✓ {filename} ({d['modality']}) → {d['chunks_indexed']} chunks")
    else:
        print(f"  ✗ {filename} failed: {r.text}")


def main():
    print(f"\nOmniLens — ingesting sample data into collection '{COLLECTION}'\n")
    files = [
        os.path.join(SAMPLE_DIR, f)
        for f in os.listdir(SAMPLE_DIR)
        if os.path.isfile(os.path.join(SAMPLE_DIR, f))
    ]
    if not files:
        print("No files found in sample_data/. Add some PDFs, images, or audio files.")
        return

    for fp in sorted(files):
        ingest_file(fp)

    print(f"\nDone. Open http://localhost:8501 and start asking questions.")


if __name__ == "__main__":
    main()
