"""Бастапқы Excel-тізімнен (data/source_catalog.xlsx) data/books.csv жасайды.

Іске қосу: python build_catalog.py
Excel-де сипаттама жоқ, сондықтан `description` бағаны бос қалады (команда толтырады).
`genre_group` — күрделі жанр жолдарынан жасалған 5 топ (мұқаба түсі, сүзгі және кластерлеу үшін).
`read_url` — Excel-дегі «Сайт» бағаны (кітапты оқуға арналған тікелей сілтеме, үшінші тарап сайттары).
"""
import pandas as pd

SRC = "data/source_catalog.xlsx"
OUT = "data/books.csv"

# Excel-де автор аты ілік септікте жазылған (қате): түзетілді
AUTHOR_FIX = {"Асқар Сүлейменовтің": "Асқар Сүлейменов", "Зейтін Ақышевтің": "Зейтін Ақышев"}


def group(genre: str) -> str:
    g = genre.lower()
    if "балалар" in g:
        return "балалар_прозасы"
    if "детектив" in g:
        return "детектив"
    if "мемуар" in g or "әскери" in g:
        return "мемуарлық_проза"
    if any(w in g for w in ("тарихи", "эпопея", "трилогия", "дилогия")):
        return "тарихи_проза"
    return "роман_повесть_әңгіме"


def main():
    d = pd.read_excel(SRC, sheet_name=0)
    out = pd.DataFrame({
        "book_id": range(1, len(d) + 1),
        "title": d["Кітап атауы"].str.strip(),
        "author": d["Автор"].str.strip().replace(AUTHOR_FIX),
        "genre": d["Жанр"].str.strip(),
        "genre_group": d["Жанр"].map(group),
        "pages": d["Бет саны"],
        "language": d["Тілі"],
        "description": "",
        "source": d["Сайт"].str.extract(r"https?://(?:www\.)?([^/]+)")[0],
        "read_url": d["Сайт"],
    })
    out.to_csv(OUT, index=False)
    print(f"{len(out)} кітап, {out.author.nunique()} автор → {OUT}")
    print(out.genre_group.value_counts().to_string())


if __name__ == "__main__":
    main()
