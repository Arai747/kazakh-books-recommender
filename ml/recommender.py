
import re

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class BookRecommender:
    def __init__(self, books, n_clusters=8):
        self.books = books.copy().reset_index(drop=True)

        required = {"book_id", "title", "author", "genre"}
        missing = required - set(self.books.columns)
        if missing:
            raise ValueError(f"Жетіспейтін бағандар: {missing}")

        if self.books["book_id"].duplicated().any():
            raise ValueError("book_id мәндері қайталанбауы керек")

        for column in ["title", "author", "genre"]:
            self.books[column] = self.books[column].fillna("").astype(str)

        if "description" not in self.books.columns:
            self.books["description"] = ""

        self.books["description"] = (
            self.books["description"].astype("string").fillna("")
        )

        def normalize(text):
            return re.sub(r"\s+", " ", text.lower().strip())

        self.books["genre_normalized"] = (
            self.books["genre"].map(normalize)
        )

        # Автордың әсерін азайтамыз.
        # Сипаттама бос болса, атауы мен жанры пайдаланылады.
        texts = (
            self.books["title"].map(normalize)
            + " "
            + self.books["genre_normalized"]
            + " "
            + self.books["description"].map(normalize)
        )

        self.vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(2, 5),
            sublinear_tf=True
        )

        self.X = self.vectorizer.fit_transform(texts)

        self.id_to_idx = {
            book_id: index
            for index, book_id in enumerate(self.books["book_id"])
        }

        cluster_count = min(n_clusters, len(self.books))

        self.kmeans = KMeans(
            n_clusters=cluster_count,
            random_state=42,
            n_init=10
        )

        self.books["cluster"] = self.kmeans.fit_predict(self.X)

    def scores(self, liked_ids):
        indices = [
            self.id_to_idx[book_id]
            for book_id in liked_ids
            if book_id in self.id_to_idx
        ]

        if not indices:
            raise ValueError("Кемінде бір кітап таңдау қажет")

        profile = np.asarray(self.X[indices].mean(axis=0))

        return cosine_similarity(profile, self.X).ravel()

    def recommend(self, liked_ids, k=5, exclude_ids=()):
        scores = self.scores(liked_ids)

        excluded = set(liked_ids) | set(exclude_ids)

        candidates = [
            index
            for index in np.argsort(-scores)
            if self.books.iloc[index]["book_id"] not in excluded
        ]

        selected = candidates[:k]

        result = self.books.iloc[selected].copy()
        result["similarity"] = scores[selected]

        return result

    def get_clusters(self):
        return self.books[
            ["book_id", "title", "genre", "cluster"]
        ].copy()


if __name__ == "__main__":
    books = pd.read_csv("ml/books.csv")

    model = BookRecommender(books)

    print("Кітап саны:", len(model.books))
    print("Кластер саны:", model.books["cluster"].nunique())

    print("\nҰсынылған 5 кітап:")
    print(
        model.recommend([1], k=5)[
            ["title", "author", "similarity", "cluster"]
        ].to_string(index=False)
    )
