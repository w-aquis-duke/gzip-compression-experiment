import csv
import gzip
from pathlib import Path

data_folder = Path(__file__).resolve().parents[1] / "data"
level_1_folder = data_folder / "compressed" / "level_1"
level_9_folder = data_folder / "compressed" / "level_9"
results_folder = data_folder / "processed"

level_1_folder.mkdir(parents=True, exist_ok=True)
level_9_folder.mkdir(parents=True, exist_ok=True)
results_folder.mkdir(parents=True, exist_ok=True)

# Use the book list created by the download script.
with (data_folder / "sources.csv").open(encoding="utf-8", newline="") as file:
    books = list(csv.DictReader(file))

results = []

for book in books:
    filename = book["filename"]
    original = (data_folder / "raw" / filename).read_bytes()

    # Compress the same original bytes at both levels.
    # mtime=0 keeps a changing timestamp out of the compressed files.
    level_1 = gzip.compress(original, compresslevel=1, mtime=0)
    level_9 = gzip.compress(original, compresslevel=9, mtime=0)

    # Check that both compressed versions restore the original exactly.
    assert gzip.decompress(level_1) == original
    assert gzip.decompress(level_9) == original

    (level_1_folder / f"{filename}.gz").write_bytes(level_1)
    (level_9_folder / f"{filename}.gz").write_bytes(level_9)

    level_1_pct = 100 * len(level_1) / len(original)
    level_9_pct = 100 * len(level_9) / len(original)

    results.append([
        book["book_id"], len(original), len(level_1), len(level_9),
        level_1_pct, level_9_pct, level_1_pct - level_9_pct,
    ])
    print(f"Compressed {filename} at both levels")

# One row per book (A positive difference means level 9 saved more space.)
results_file = results_folder / "compression_results.csv"
with results_file.open("w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow([
        "book_id", "original_bytes", "level_1_bytes", "level_9_bytes",
        "level_1_pct", "level_9_pct", "difference_pp",
    ])
    writer.writerows(results)

print(f"Saved results for {len(results)} books to {results_file}")
