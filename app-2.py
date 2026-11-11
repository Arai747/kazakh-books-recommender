"""BookRec: қазақ әдебиеті сайты (Python + Streamlit).

Іске қосу: streamlit run app.py
Беттер: Басты бет · Кітаптар · Ұсыныстар · Таңдаулылар
Дизайн theme.py ішінде, ұсыныстар recommender.py (TF-IDF) арқылы есептеледі.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from recommender import BookRecommender
from theme import (CSS, FOOTER_HTML, GENRE_NAMES, HERO_HTML, YEARS, cover_html, esc,
                   logo_html)

st.set_page_config(page_title="BookRec · Қазақ әдебиеті", page_icon="📚", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------- деректер
@st.cache_data
def load_books() -> pd.DataFrame:
    return pd.read_csv("data/books.csv")


@st.cache_resource
def load_model(_books: pd.DataFrame) -> BookRecommender:
    return BookRecommender(_books, "char")


books = load_books()
rec = load_model(books)
by_id = books.set_index("book_id")
# бірдей атаулы кітаптар бар (әртүрлі авторлар), сондықтан белгі = «Атауы — Автор»
LABELS = (books.title + " — " + books.author).tolist()
LABEL_TO_ID = dict(zip(LABELS, books.book_id))
ID_TO_LABEL = {v: k for k, v in LABEL_TO_ID.items()}
PER_PAGE = 12

st.session_state.setdefault("page", "home")
st.session_state.setdefault("favs", [])


def go(page: str):
    st.session_state.page = page


def toggle_fav(book_id: int):
    favs = st.session_state.favs
    if book_id in favs:
        favs.remove(book_id)
    else:
        favs.append(book_id)


# ---------------------------------------------------------------- компоненттер
@st.dialog("Кітап туралы")
def show_book(bid: int):
    r = by_id.loc[bid]
    st.subheader(r.title)
    st.caption(f"{r.author} · {r.genre}" + (f" · {YEARS[r.title]}" if r.title in YEARS else ""))
    st.write(f"Бет саны: {int(r.pages)}")
    if isinstance(r.description, str) and r.description.strip():
        st.write(r.description)
    else:
        st.caption("Сипаттамасы әлі қосылмаған.")
    st.caption(f"Басылым мәртебесі: {r.edition_status}")
    st.link_button("Каталогтан іздеу", r.search_url)
    is_fav = bid in st.session_state.favs
    st.button("♥ Таңдаулыда" if is_fav else "♡ Таңдаулыға қосу", key=f"dlg_{bid}",
              on_click=toggle_fav, args=(bid,), type="primary" if is_fav else "secondary")


def header():
    c_logo, c_menu = st.columns([5, 1], vertical_alignment="center")
    with c_logo:
        st.markdown(logo_html(), unsafe_allow_html=True)
    with c_menu:
        with st.container(key="menu"):
            with st.popover("☰"):
                items = [("home", "Басты бет", ":material/home:"), ("books", "Кітаптар", ":material/menu_book:"),
                         ("recs", "Ұсыныстар", ":material/auto_awesome:"),
                         ("favs", f"Таңдаулылар ({len(st.session_state.favs)})", ":material/favorite:")]
                for key, label, icon in items:
                    st.button(label, key=f"nav_{key}", icon=icon, on_click=go, args=(key,),
                              type="primary" if st.session_state.page == key else "secondary",
                              use_container_width=True)
    st.markdown('<hr class="nav-line">', unsafe_allow_html=True)


def card(row, prefix: str, similarity: float | None = None):
    bid = int(row.book_id)
    is_fav = bid in st.session_state.favs
    with st.container(border=True, key=f"card_{prefix}_{bid}"):
        st.button("♥" if is_fav else "♡", key=f"heart_{prefix}_{bid}", on_click=toggle_fav, args=(bid,))
        c1, c2 = st.columns([1, 1.35], gap="small")
        with c1:
            st.markdown(cover_html(row.title, row.author, row.genre), unsafe_allow_html=True)
        with c2:
            year = f"{YEARS[row.title]}" if row.title in YEARS else ""
            chip = row.genre.split(",")[0].strip()
            extra = ""
            if similarity is not None:
                extra = (f'<div class="sim">Ұқсастық: {similarity:.0%}</div>'
                         f'<div class="bar"><i style="width:{min(similarity, 1) * 100:.0f}%"></i></div>')
            st.markdown(
                f'<p class="b-title">{esc(row.title)}</p><p class="b-author">{esc(row.author)}</p>'
                f'<span class="chip">{esc(chip)}</span>'
                f'<div class="b-year">{year}</div>{extra}', unsafe_allow_html=True)
            if st.button("Толығырақ", key=f"more_{prefix}_{bid}", type="primary", icon=":material/arrow_forward:"):
                show_book(bid)


def grid(df: pd.DataFrame, prefix: str, sims: dict | None = None, per_row: int = 4):
    rows = list(df.itertuples())
    for i in range(0, len(rows), per_row):
        cols = st.columns(per_row)
        for col, r in zip(cols, rows[i:i + per_row]):
            with col:
                card(r, prefix, sims.get(r.book_id) if sims else None)


def section(eyebrow: str, title: str, sub: str = ""):
    st.markdown((f'<div class="sec-eyebrow">{esc(eyebrow)}</div>' if eyebrow else "")
                + f'<div class="sec-title">{esc(title)}</div>'
                + (f'<div class="sec-sub">{esc(sub)}</div>' if sub else '<div style="height:.8rem"></div>'),
                unsafe_allow_html=True)


def search_books(query: str) -> pd.DataFrame:
    q = query.strip().lower()
    if not q:
        return books
    m = books.title.str.lower().str.contains(q, regex=False) | books.author.str.lower().str.contains(q, regex=False)
    return books[m]


# ---------------------------------------------------------------- беттер
def page_home():
    with st.container(key="hero"):
        st.markdown(HERO_HTML, unsafe_allow_html=True)
        with st.form("search", border=False):
            c1, c2 = st.columns([14, 1], vertical_alignment="center")
            c1.text_input("Іздеу", key="q", placeholder="🔍  Кітаптың атауын немесе авторын іздеңіз...",
                          label_visibility="collapsed")
            c2.form_submit_button("→")
    query = st.session_state.get("q", "")
    if query.strip():
        found = search_books(query)
        section("Іздеу нәтижесі", f"Табылды: {len(found)}")
        if found.empty:
            st.info("Ештеңе табылмады. Басқа сөзбен көріңіз.")
        else:
            if len(found) > PER_PAGE:
                st.caption(f"Алғашқы {PER_PAGE} нәтиже көрсетілді. Толығын «Кітаптар» бетінен қараңыз.")
            grid(found.head(PER_PAGE), "hs")
        return
    c_t, c_b = st.columns([3, 1], vertical_alignment="bottom")
    with c_t:
        section("Біздің жинақ", "Оқуға тұрарлық шығармалар")
    with c_b:
        st.button("Барлық кітаптар", key="allbooks", icon=":material/arrow_right_alt:", on_click=go, args=("books",))
    wanted = ["Абай жолы", "Ақбілек", "Қан мен тер", "Менің атым Қожа"]
    picks = pd.concat([books[books.title == t].head(1) for t in wanted])
    grid(picks, "hf")


def show_more(key: str):
    st.session_state[key] += PER_PAGE


def page_books():
    section("Каталог", "Барлық кітаптар", "Жанр, автор, атау немесе бет саны бойынша сүзгілеңіз.")
    c1, c2, c3, c4 = st.columns([2.2, 2.2, 2.2, 1.1])
    groups = c1.multiselect("Жанр", list(GENRE_NAMES), format_func=lambda g: GENRE_NAMES[g], placeholder="Таңдаңыз...")
    authors = c2.multiselect("Автор", sorted(books.author.unique()), placeholder="Таңдаңыз...")
    text = c3.text_input("Атауы немесе авторы", placeholder="мысалы: Абай")
    pages_txt = c4.text_input("Бет саны", placeholder="мысалы: 200").strip()
    df = search_books(text)
    if groups:
        df = df[df.genre_group.isin(groups)]
    if authors:
        df = df[df.author.isin(authors)]
    if pages_txt:
        if pages_txt.isdigit():
            df = df[df.pages == int(pages_txt)]
        else:
            st.caption("Бет санын тек санмен жазыңыз, мысалы: 200")
    if df.empty:
        st.info("Сүзгіге сай кітап жоқ.")
        return
    # сүзгі өзгерсе, көрсетілетін кітап саны бастапқы мәнге қайтады
    key = f"show_{hash((tuple(groups), tuple(authors), text, pages_txt))}"
    st.session_state.setdefault(key, PER_PAGE)
    n = st.session_state[key]
    st.caption(f"Табылды: {len(df)} / {len(books)} кітап")
    grid(df.head(n), "bk")
    if len(df) > n:
        st.button("Тағы көрсету", key="load_next", icon=":material/expand_more:", on_click=show_more, args=(key,))


def page_recs():
    section("", "Сізге арналған ұсыныстар")
    default = [ID_TO_LABEL[b] for b in st.session_state.favs if b in ID_TO_LABEL]
    liked_titles = st.multiselect("Маған мына кітаптар ұнады", LABELS, default=default, placeholder="Кітап таңдаңыз...")
    k = st.slider("Ұсыныс саны", 1, 8, 4)
    if not liked_titles:
        st.info("Кемінде бір кітапты таңдаңыз немесе «Таңдаулылар» тізіміне кітап қосыңыз.")
        return
    out = rec.recommend([LABEL_TO_ID[t] for t in liked_titles], k=k)
    grid(out, "rc", sims=dict(zip(out.book_id, out.similarity)))


def page_favs():
    section("Менің тізімім", "Таңдаулылар")
    favs = st.session_state.favs
    if not favs:
        st.info("Тізім бос. Кітап карточкасындағы жүрекшені басып қосыңыз.")
        st.button("Кітаптарға өту", key="to_books", icon=":material/arrow_forward:", on_click=go, args=("books",))
        return
    grid(books[books.book_id.isin(favs)], "fv")
    st.button("Осыларға ұқсас кітаптарды көру", key="to_recs", icon=":material/auto_awesome:",
              on_click=go, args=("recs",), type="primary")


# ---------------------------------------------------------------- іске қосу
header()
{"home": page_home, "books": page_books, "recs": page_recs, "favs": page_favs}[st.session_state.page]()
st.markdown(FOOTER_HTML, unsafe_allow_html=True)
