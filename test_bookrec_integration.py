"""BookRec: integrated-site recommender және SQLite backend smoke tests.
Run: python -m unittest -v test_bookrec_integration.py
Uses temporary SQLite database; does not modify production data.
"""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "integrated-site"
sys.path.insert(0, str(SITE))


def load_database():
    spec = importlib.util.spec_from_file_location("bookrec_database_test", SITE / "database.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BookRecIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from recommender import BookRecommender
        cls.books = pd.read_csv(SITE / "data" / "books.csv").fillna("")
        cls.model = BookRecommender(cls.books, kind="char")
        cls.ids = set(cls.books.book_id.astype(int))

    def test_three_real_catalog_examples(self):
        for title in ("Абай жолы: 1-том", "Ақбілек", "Менің атым Қожа"):
            with self.subTest(title=title):
                matching = self.books[self.books.title == title]
                self.assertFalse(matching.empty, f"Каталогта жоқ: {title}")
                bid = int(matching.iloc[0].book_id)
                result = self.model.recommend([bid], k=5)
                self.assertEqual(len(result), 5)
                self.assertNotIn(bid, result.book_id.tolist())
                self.assertTrue(set(result.book_id.astype(int)).issubset(self.ids))
                self.assertTrue(result.similarity.between(0, 1).all())

    def test_unknown_book_id_is_handled(self):
        with self.assertRaises(ValueError):
            self.model.recommend([-999999], k=5)

    def test_access_code_and_sqlite_persistence(self):
        import access_code
        db = load_database()
        with tempfile.TemporaryDirectory() as temp:
            db.DB_PATH = Path(temp) / "test_bookrec.db"
            db.get_database_url = lambda: ""
            db.init_db()
            code = access_code.generate_access_code()
            self.assertTrue(access_code.validate_access_code(code))
            self.assertFalse(db.access_code_exists(code))
            db.register_access_code(code)
            self.assertTrue(db.access_code_exists(code))
            bid = int(self.books.iloc[0].book_id)
            db.add_to_reading_list(code, bid)
            db.add_to_reading_list(code, bid)
            self.assertEqual(db.get_reading_list(code), [bid])
            db.remove_from_reading_list(code, bid)
            self.assertEqual(db.get_reading_list(code), [])


if __name__ == "__main__":
    unittest.main()
