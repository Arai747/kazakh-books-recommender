"""Streamlit Community Cloud entry point. Run: streamlit run app.py"""
import runpy
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent / "integrated-site"
if str(SITE) not in sys.path:
    sys.path.insert(0, str(SITE))
runpy.run_path(str(SITE / "app.py"), run_name="__main__")
