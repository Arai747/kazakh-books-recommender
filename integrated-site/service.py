"""Backend boundary between Streamlit, stored reader choices and the ML model."""
from __future__ import annotations

import database
from recommender import BookRecommender


class RecommendationService:
    def __init__(self, books, model=None):
        self.books = books
        self.known_ids = set(books.book_id.astype(int))
        self.model = model or BookRecommender(books, kind="char")

    def save_likes(self, user_id, book_ids):
        ids = list(dict.fromkeys(int(bid) for bid in book_ids))
        if not set(ids).issubset(self.known_ids):
            raise ValueError("Каталогта жоқ кітап таңдалған")
        database.save_preferences(user_id, ids)

    def saved_likes(self, user_id):
        saved = database.get_preferences(user_id)
        ids = database.get_reading_list(user_id) if saved is None else saved
        return [bid for bid in ids if bid in self.known_ids]

    def recommend_for_user(self, user_id, k=5):
        if not 1 <= int(k) <= 20:
            raise ValueError("Ұсыныс саны 1–20 аралығында болуы керек")
        liked_ids = self.saved_likes(user_id)
        if not liked_ids:
            return self.books.head(0).assign(similarity=0.0)
        return self.model.recommend(
            liked_ids,
            k=int(k),
            exclude_ids=database.get_reading_list(user_id),
        )
