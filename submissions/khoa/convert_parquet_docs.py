from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
PARQUET_PATH = ROOT.parent.parent / "docs" / "0000.parquet"
OUT_DIR = ROOT / "data" / "parquet_docs"


def main() -> None:
    df = pd.read_parquet(PARQUET_PATH)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    subset = df[df["type"].eq("law")].head(10)
    written: list[Path] = []

    for _, row in subset.iterrows():
        filename = str(row["filename"])
        if not filename.endswith(".md"):
            filename = f"{row['id']}.md"

        path = OUT_DIR / filename
        text = (
            f"# {row['title']}\n\n"
            f"- id: {row['id']}\n"
            f"- type: {row['type']}\n"
            f"- source_file: {row['filename']}\n"
            f"- content_length: {row['content_length']}\n\n"
            "---\n\n"
            f"{row['content']}\n"
        )
        path.write_text(text, encoding="utf-8")
        written.append(path)

    print(f"Converted {len(written)} documents:")
    for path in written:
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
