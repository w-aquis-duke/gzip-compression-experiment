import csv
import gzip
import random
import time
from pathlib import Path
from urllib.request import urlretrieve

NUM_BOOKS = 50

data_folder = Path(__file__).resolve().parents[1] / "data"
books_folder = data_folder / "raw"
books_folder.mkdir(parents=True, exist_ok=True)
mirror = "https://gutenberg.pglaf.org"

# Download the catalog if we do not already have it.
catalog = data_folder / "catalog.csv.gz"
if not catalog.exists():
    urlretrieve(f"{mirror}/cache/epub/feeds/pg_catalog.csv.gz", catalog)

# Read the catalog and keep English-language books with a named author.
books = []
with gzip.open(catalog, "rt", encoding="utf-8-sig") as file:
    for book in csv.DictReader(file):
        if book["Type"] == "Text" and book["Language"] == "en":
            if book["Authors"] not in ["", "Various"]:
                books.append(book)

# The seed makes the shuffled order repeatable.
random.seed(511)
random.shuffle(books)

selected_books = []
used_authors = []
used_titles = []

for book in books:
    author = book["Authors"].split(";")[0].strip()
    title = book["Title"].strip().lower()
    if author in used_authors or title in used_titles:
        continue

    book_id = book["Text#"]
    filename = f"{book_id}.txt"
    url = f"{mirror}/cache/epub/{book_id}/pg{book_id}.txt"

    # Reuse existing files when running the script again.
    if not (books_folder / filename).exists():
        time.sleep(2)
        urlretrieve(url, books_folder / filename)

    selected_books.append([book_id, book["Title"], author, url, filename])
    used_authors.append(author)
    used_titles.append(title)
    print(f"Downloaded {len(selected_books)} of {NUM_BOOKS}")

    if len(selected_books) == NUM_BOOKS:
        break

# Save a list of the books used in the experiment.
with (data_folder / "sources.csv").open("w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["book_id", "title", "author", "source_url", "filename"])
    writer.writerows(selected_books)

print("Finished. The book list is in data/sources.csv.")
