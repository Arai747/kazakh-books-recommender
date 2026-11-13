"""Meaningful backend, migration, reader isolation and Streamlit integration checks."""
import importlib
import sqlite3
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "integrated-site"
sys.path.insert(0, str(SITE))
import database as db
from recommender import BookRecommender
from service import RecommendationService


@pytest.fixture
def storage(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "bookrec.db")
    monkeypatch.setattr(db, "get_database_url", lambda: "")
    db.init_db()
    return db


@pytest.fixture(scope="module")
def service():
    books = pd.read_csv(SITE / "data" / "books.csv").fillna("")
    return RecommendationService(books, BookRecommender(books))


def test_migrates_existing_favorites_without_losing_data(tmp_path, monkeypatch):
    path = tmp_path / "legacy.db"
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE reading_list (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT NOT NULL, book_id INTEGER NOT NULL, added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, UNIQUE(user_id, book_id))")
        conn.execute("INSERT INTO reading_list(user_id, book_id) VALUES ('reader',17)")
    monkeypatch.setattr(db, "DB_PATH", path)
    monkeypatch.setattr(db, "get_database_url", lambda: "")
    db.init_db()
    db.init_db()
    assert db.get_reading_entries("reader")[0]["status"] == "planned"
    assert db.get_reading_list("reader") == [17]


def test_reading_list_is_persistent_and_isolated(storage):
    storage.add_to_reading_list("alice", 17)
    storage.add_to_reading_list("alice", 17)
    storage.add_to_reading_list("bob", 17)
    storage.set_reading_status("alice", 17, "reading")
    assert storage.get_reading_entries("alice")[0]["status"] == "reading"
    assert storage.get_reading_entries("bob")[0]["status"] == "planned"
    storage.remove_from_reading_list("bob", 17)
    assert storage.get_reading_list("alice") == [17]
    assert storage.get_reading_list("bob") == []
    with pytest.raises(ValueError):
        storage.set_reading_status("alice", 17, "invalid")
    with sqlite3.connect(storage.DB_PATH) as connection:
        assert connection.execute("SELECT status FROM reading_list WHERE user_id='alice'").fetchone()[0] == "reading"


def test_preferences_are_saved_and_can_be_cleared(storage, service):
    storage.add_to_reading_list("reader", 17)
    assert service.saved_likes("reader") == [17]
    service.save_likes("reader", [1, 104, 1])
    assert storage.get_preferences("reader") == [1, 104]
    service.save_likes("reader", [])
    assert service.saved_likes("reader") == []
    assert service.recommend_for_user("reader").empty
    assert storage.get_reading_list("reader") == [17]


def test_recommendations_exclude_saved_and_liked_books(storage, service):
    service.save_likes("alice", [17])
    storage.add_to_reading_list("alice", 18)
    result = service.recommend_for_user("alice", k=12)
    assert len(result) == 12
    assert not set(result.book_id) & {17, 18}
    assert result.similarity.between(0, 1).all()
    assert result.similarity.is_monotonic_decreasing
    assert service.recommend_for_user("bob").empty
    with pytest.raises(ValueError):
        service.save_likes("alice", [999999])
    assert storage.get_preferences("alice") == [17]
    with pytest.raises(ValueError):
        service.recommend_for_user("alice", 0)


def test_access_code_recovers_choices(storage, service):
    from access_code import generate_access_code, normalize_access_code
    code = generate_access_code()
    storage.register_access_code(code)
    storage.add_to_reading_list(code, 104)
    service.save_likes(code, [1, 17])
    restored = normalize_access_code('  '+code.upper()+'  ')
    assert storage.access_code_exists(restored)
    assert storage.get_reading_list(restored) == [104]
    assert service.saved_likes(restored) == [1, 17]


def test_all_270_illustrated_covers_exist():
    from PIL import Image
    books = pd.read_csv(SITE / "data" / "books.csv")
    assert len(books) == 270
    for bid in books.book_id:
        with Image.open(SITE / "covers" / f"{bid}.webp") as image:
            assert image.format == "WEBP"
            assert image.width >= 256 and image.height >= 384


def test_streamlit_end_to_end(storage):
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=40).run()
    assert not app.exception
    user_id = app.session_state["user_id"]
    app.button(key="heart_hf_1").click().run()
    assert storage.get_reading_list(user_id) == [1]
    app.button(key="nav_favs").click().run()
    assert not app.exception
    app.selectbox(key=f"reading_status_{user_id}_1").set_value("finished").run()
    assert storage.get_reading_entries(user_id)[0]["status"] == "finished"
    app.button(key="nav_recs").click().run()
    assert storage.get_preferences(user_id) == [1]
    app.multiselect(key=f"liked_books_{user_id}").set_value([17]).run()
    assert not app.exception
    assert storage.get_preferences(user_id) == [17]
    assert len([button for button in app.button if str(button.key).startswith("more_rc_")]) == 5
    app.multiselect(key=f"liked_books_{user_id}").set_value([]).run()
    assert not app.exception
    assert storage.get_preferences(user_id) == []
