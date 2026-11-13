"""BookRec — қазақ әдебиетіне арналған Streamlit сайты."""

from __future__ import annotations

from pathlib import Path
from access_code import generate_access_code, validate_access_code, normalize_access_code

import pandas as pd
import streamlit as st

from database import (
    init_db,
    add_to_reading_list,
    remove_from_reading_list,
    get_reading_list,
    register_access_code,
    access_code_exists,
    get_reading_entries,
    set_reading_status,
    READING_STATUSES,
)
from recommender import BookRecommender
from service import RecommendationService
from theme import (
    CSS,
    FOOTER_HTML,
    GENRE_NAMES,
    HERO_HTML,
    YEARS,
    cover_html,
    cover_image_html,
    esc,
    logo_html,
)


BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="BookRec · Қазақ әдебиеті",
    page_icon="📚",
    layout="wide",
)
st.markdown(CSS, unsafe_allow_html=True)


# -------------------- ДЕРЕКТЕР --------------------

@st.cache_data
def load_books():
    df = pd.read_csv(BASE_DIR / "data" / "books.csv")

    for col in ["title", "author", "genre", "description"]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].astype("string").fillna("")

    if "genre_group" not in df.columns:
        df["genre_group"] = df["genre"]

    if "pages" not in df.columns:
        df["pages"] = 0

    if "read_url" not in df.columns:
        df["read_url"] = ""

    return df


@st.cache_resource
def load_model(catalogue):
    return BookRecommender(catalogue, kind="char")


books = load_books()
rec = load_model(books)
service = RecommendationService(books, rec)

by_id = books.set_index("book_id")

LABELS = (
    books["title"] + " — " + books["author"]
).tolist()

# Бірдей атау мен автор кездессе, ID арқылы ажыратамыз.
BOOK_OPTIONS = {
    int(row.book_id): f"{row.title} — {row.author} (#{row.book_id})"
    for row in books.itertuples()
}

PER_PAGE = 12


# -------------------- ПАЙДАЛАНУШЫ ЖӘНЕ ДЕРЕКТЕР БАЗАСЫ --------------------

init_db()

st.session_state.setdefault("page", "home")

if "user_id" not in st.session_state:
    # Жаңа сеансқа бірегей құпия код беріп, оны базаға тіркейміз.
    new_code = generate_access_code()
    register_access_code(new_code)
    st.session_state["user_id"] = new_code


def access_code_panel():
    """Кодты көрсету және сақталған тізімді басқа сеанста ашу."""
    with st.container():
        st.subheader("🔑 Менің жеке кодым")
        st.caption("Таңдаулы кітаптарды басқа құрылғыда ашу үшін кодты сақтаңыз. Оны ешкімге бермеңіз.")
        st.code(st.session_state["user_id"], language=None)
        with st.form("restore_access_code", clear_on_submit=True):
            entered_code = st.text_input(
                "Бұрынғы жеке кодты енгізіңіз",
                type="password",
                placeholder="32 таңбалы код",
            )
            submitted = st.form_submit_button("Тізімімді қалпына келтіру")

        if submitted:
            if not validate_access_code(entered_code):
                st.error("Код форматы дұрыс емес. 32 таңбалы код енгізіңіз.")
            else:
                code = normalize_access_code(entered_code)
                if not access_code_exists(code):
                    st.error("Мұндай код деректер базасында тіркелмеген.")
                else:
                    st.session_state["user_id"] = code
                    st.success("Тізіміңіз ашылды!")
                    st.rerun()




def refresh_favs():
    st.session_state["favs"] = get_reading_list(
        st.session_state["user_id"]
    )


refresh_favs()


def go(page):
    st.session_state["page"] = page


def toggle_fav(book_id):
    user_id = st.session_state["user_id"]
    favs = get_reading_list(user_id)

    if book_id in favs:
        remove_from_reading_list(user_id, book_id)
    else:
        add_to_reading_list(user_id, book_id)

    refresh_favs()


# -------------------- КІТАП ТУРАЛЫ --------------------

@st.dialog("Кітап туралы")
def show_book(bid):
    r = by_id.loc[bid]

    st.markdown(cover_image_html(BASE_DIR / "covers" / f"{bid}.webp", r.title, r.author, r.genre), unsafe_allow_html=True)
    st.subheader(r.title)
    st.caption(f"{r.author} · {r.genre}")

    if pd.notna(r.pages):
        st.write(f"Бет саны: {int(r.pages)}")

    if r.description.strip():
        st.write(r.description)

    if pd.notna(r.read_url) and str(r.read_url).strip():
        st.link_button(
            "Кітапты оқу",
            str(r.read_url),
        )
    else:
        st.caption("Кітаптың сілтемесі әзірге жоқ.")

    is_fav = bid in st.session_state["favs"]

    st.button(
        "♥ Таңдаулыда" if is_fav else "♡ Таңдаулыға қосу",
        key=f"dialog_{bid}",
        on_click=toggle_fav,
        args=(bid,),
        type="primary" if is_fav else "secondary",
    )


# -------------------- HEADER --------------------

def header():
    c_logo, c_menu = st.columns(
        [5, 1],
        vertical_alignment="center",
    )

    with c_logo:
        st.markdown(
            logo_html(),
            unsafe_allow_html=True,
        )

    with c_menu:
        with st.container(key="menu"):
            with st.popover("☰"):
                items = [
                    ("home", "Басты бет", ":material/home:"),
                    ("books", "Кітаптар", ":material/menu_book:"),
                    ("recs", "Ұсыныстар", ":material/auto_awesome:"),
                    (
                        "favs",
                        f"My Reading List ({len(st.session_state['favs'])})",
                        ":material/favorite:",
                    ),
                ]

                items.append(("access", "🔑 Менің жеке кодым", ":material/key:"))

                for key, label, icon in items:
                    st.button(
                        label,
                        key=f"nav_{key}",
                        icon=icon,
                        on_click=go,
                        args=(key,),
                        type=(
                            "primary"
                            if st.session_state["page"] == key
                            else "secondary"
                        ),
                        use_container_width=True,
                    )

    st.markdown(
        '<hr class="nav-line">',
        unsafe_allow_html=True,
    )


# -------------------- КІТАП КАРТОЧКАСЫ --------------------

def card(row, prefix, similarity=None):
    bid = int(row.book_id)
    is_fav = bid in st.session_state["favs"]

    with st.container(
        border=True,
        key=f"card_{prefix}_{bid}",
    ):
        st.button(
            "♥" if is_fav else "♡",
            key=f"heart_{prefix}_{bid}",
            on_click=toggle_fav,
            args=(bid,),
        )

        c1, c2 = st.columns(
            [1, 1.35],
            gap="small",
        )

        with c1:
            st.markdown(
                cover_image_html(
                    BASE_DIR / "covers" / f"{bid}.webp",
                    row.title,
                    row.author,
                    row.genre,
                ),
                unsafe_allow_html=True,
            )

        with c2:
            year = (
                str(YEARS[row.title])
                if row.title in YEARS
                else ""
            )

            chip = row.genre.split(",")[0].strip()

            extra = ""

            if similarity is not None:
                extra = (
                    f'<div class="sim">'
                    f'Ұқсастық: {similarity:.0%}'
                    f'</div>'
                    f'<div class="bar">'
                    f'<i style="width:{min(max(similarity, 0), 1) * 100:.0f}%"></i>'
                    f'</div>'
                )

            st.markdown(
                f'<p class="b-title">{esc(row.title)}</p>'
                f'<p class="b-author">{esc(row.author)}</p>'
                f'<span class="chip">{esc(chip)}</span>'
                f'<div class="b-year">{year}</div>'
                f'{extra}',
                unsafe_allow_html=True,
            )

            if st.button(
                "Толығырақ",
                key=f"more_{prefix}_{bid}",
                type="primary",
                icon=":material/arrow_forward:",
            ):
                show_book(bid)


def grid(df, prefix, sims=None, per_row=4):
    rows = list(df.itertuples())

    for i in range(0, len(rows), per_row):
        cols = st.columns(per_row)

        for col, row in zip(
            cols,
            rows[i:i + per_row],
        ):
            with col:
                score = (
                    sims.get(row.book_id)
                    if sims
                    else None
                )
                card(row, prefix, score)


def section(eyebrow, title, sub=""):
    html = (
        f'<div class="sec-eyebrow">{esc(eyebrow)}</div>'
        if eyebrow
        else ""
    )

    html += f'<div class="sec-title">{esc(title)}</div>'

    if sub:
        html += f'<div class="sec-sub">{esc(sub)}</div>'
    else:
        html += '<div style="height:.8rem"></div>'

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


def search_books(query):
    q = query.strip().lower()

    if not q:
        return books

    mask = (
        books.title.str.lower().str.contains(q, regex=False)
        | books.author.str.lower().str.contains(q, regex=False)
    )

    return books[mask]


# -------------------- БАСТЫ БЕТ --------------------

def page_home():
    with st.container(key="hero"):
        st.markdown(
            HERO_HTML,
            unsafe_allow_html=True,
        )

        with st.form("search", border=False):
            c1, c2 = st.columns(
                [14, 1],
                vertical_alignment="center",
            )

            c1.text_input(
                "Іздеу",
                key="q",
                placeholder="🔍 Кітаптың атауын немесе авторын іздеңіз...",
                label_visibility="collapsed",
            )

            c2.form_submit_button("→")

    query = st.session_state.get("q", "")

    if query.strip():
        found = search_books(query)

        section(
            "Іздеу нәтижесі",
            f"Табылды: {len(found)}",
        )

        if found.empty:
            st.info("Ештеңе табылмады.")
        else:
            grid(
                found.head(PER_PAGE),
                "hs",
            )
        return

    c_t, c_b = st.columns(
        [3, 1],
        vertical_alignment="bottom",
    )

    with c_t:
        section(
            "Біздің жинақ",
            "Оқуға тұрарлық шығармалар",
        )

    with c_b:
        st.button(
            "Барлық кітаптар",
            key="allbooks",
            icon=":material/arrow_right_alt:",
            on_click=go,
            args=("books",),
        )

    wanted = [
        "Абай жолы: 1-том",
        "Ақбілек",
        "Қан мен тер",
        "Менің атым Қожа",
    ]

    picks = pd.concat(
        [
            books[books.title == title].head(1)
            for title in wanted
        ]
    )

    if picks.empty:
        picks = books.head(4)

    grid(picks, "hf")


# -------------------- КАТАЛОГ --------------------

def show_more(key):
    st.session_state[key] += PER_PAGE


def page_books():
    section(
        "Каталог",
        "Барлық кітаптар",
        "Жанр, автор, атау немесе бет саны бойынша сүзгілеңіз.",
    )

    c1, c2, c3, c4 = st.columns(
        [2.2, 2.2, 2.2, 1.1]
    )

    available_groups = sorted(
        books.genre_group.dropna().unique()
    )

    groups = c1.multiselect(
        "Жанр",
        available_groups,
        format_func=lambda g: GENRE_NAMES.get(g, g),
        placeholder="Таңдаңыз...",
    )

    authors = c2.multiselect(
        "Автор",
        sorted(books.author.unique()),
        placeholder="Таңдаңыз...",
    )

    text = c3.text_input(
        "Атауы немесе авторы",
        placeholder="мысалы: Абай",
    )

    pages_txt = c4.text_input(
        "Бет саны",
        placeholder="мысалы: 200",
    ).strip()

    df = search_books(text)

    if groups:
        df = df[df.genre_group.isin(groups)]

    if authors:
        df = df[df.author.isin(authors)]

    if pages_txt:
        if pages_txt.isdigit():
            df = df[df.pages == int(pages_txt)]
        else:
            st.caption("Бет санын тек санмен жазыңыз.")

    if df.empty:
        st.info("Сүзгіге сай кітап жоқ.")
        return

    key = (
        f"show_{hash((tuple(groups), tuple(authors), text, pages_txt))}"
    )

    st.session_state.setdefault(key, PER_PAGE)
    n = st.session_state[key]

    st.caption(
        f"Табылды: {len(df)} / {len(books)} кітап"
    )

    grid(df.head(n), "bk")

    if len(df) > n:
        st.button(
            "Тағы көрсету",
            key="load_next",
            icon=":material/expand_more:",
            on_click=show_more,
            args=(key,),
        )


# -------------------- ҰСЫНЫСТАР --------------------

def page_recs():
    section(
        "",
        "Сізге арналған ұсыныстар",
    )

    user_id = st.session_state["user_id"]
    selected_key = f"liked_books_{user_id}"
    if selected_key not in st.session_state:
        st.session_state[selected_key] = service.saved_likes(user_id)

    def save_likes():
        service.save_likes(user_id, st.session_state[selected_key])

    st.multiselect(
        "Маған мына кітаптар ұнады",
        options=list(BOOK_OPTIONS),
        key=selected_key,
        format_func=lambda bid: BOOK_OPTIONS[bid],
        placeholder="Кітап таңдаңыз...",
        on_change=save_likes,
    )
    k = st.slider("Ұсыныс саны", 1, 12, 5)
    if not st.session_state[selected_key]:
        st.info("Кемінде бір ұнаған кітабыңызды таңдаңыз. Таңдау жеке кодыңызбен бірге сақталады.")
        return
    out = service.recommend_for_user(user_id, k=k)
    if out.empty:
        st.info("Қалған кітаптар табылмады. Таңдауыңызды өзгертіп көріңіз.")
        return
    st.caption("Ұсыныстар атау, автор, жанр және сипаттаманың ұқсастығына негізделеді. Тізіміңіздегі кітаптар қайталанбайды.")
    sims = dict(zip(out.book_id, out.similarity))
    grid(out, "rc", sims=sims)


# -------------------- МЕНІҢ ТІЗІМІМ --------------------

def page_favs():
    section("МЕНІҢ КІТАП СӨРЕМ", "My Reading List", "Оқу жоспарыңыз бен оқылған кітаптар бір жерде.")
    entries = get_reading_entries(st.session_state["user_id"])
    if not entries:
        st.info("Тізім бос. Кітап карточкасындағы жүрекшені басып қосыңыз.")
        st.button("Кітаптарға өту", key="to_books", on_click=go, args=("books",))
        return
    entry_by_id = {entry["book_id"]: entry for entry in entries}
    counts = {status: sum(entry["status"] == status for entry in entries) for status in READING_STATUSES}
    cols = st.columns(3)
    for col, (status, label) in zip(cols, READING_STATUSES.items()):
        col.metric(label, counts[status])
    status_filter = st.selectbox("Оқу мәртебесі", ["all", *READING_STATUSES], format_func=lambda value: "Барлығы" if value == "all" else READING_STATUSES[value])
    ids = [entry["book_id"] for entry in entries if status_filter == "all" or entry["status"] == status_filter]
    for bid in ids:
        if bid not in by_id.index:
            continue
        row = by_id.loc[bid]
        with st.container(border=True):
            image_col, text_col = st.columns([1, 5])
            with image_col:
                st.markdown(cover_image_html(BASE_DIR / "covers" / f"{bid}.webp", row.title, row.author, row.genre), unsafe_allow_html=True)
            with text_col:
                st.subheader(row.title)
                st.caption(row.author)
                widget_key = f"reading_status_{st.session_state['user_id']}_{bid}"
                current = entry_by_id[bid]["status"]
                def update_status(book_id=bid, key=widget_key):
                    set_reading_status(st.session_state["user_id"], book_id, st.session_state[key])
                st.selectbox("Мәртебе", list(READING_STATUSES), index=list(READING_STATUSES).index(current), format_func=lambda value: READING_STATUSES[value], key=widget_key, on_change=update_status)
                left, right = st.columns(2)
                with left:
                    if st.button("Толығырақ", key=f"reading_details_{bid}"):
                        show_book(bid)
                with right:
                    st.button("Тізімнен алып тастау", key=f"reading_remove_{bid}", on_click=toggle_fav, args=(bid,))
    if not ids:
        st.info("Бұл мәртебеде кітап жоқ.")
    rows = [{"title": by_id.loc[e["book_id"]].title, "author": by_id.loc[e["book_id"]].author, "status": READING_STATUSES[e["status"]], "added_at": e["added_at"]} for e in entries if e["book_id"] in by_id.index]
    st.download_button("Тізімді CSV ретінде жүктеу", pd.DataFrame(rows).to_csv(index=False).encode("utf-8-sig"), file_name="my-reading-list.csv", mime="text/csv")
    st.button("Маған кітап ұсыну", key="to_recs", on_click=go, args=("recs",), type="primary")


# -------------------- ІСКЕ ҚОСУ --------------------

header()

pages = {
    "home": page_home,
    "books": page_books,
    "recs": page_recs,
    "favs": page_favs,
    "access": access_code_panel,
}

pages.get(
    st.session_state["page"],
    page_home,
)()

st.markdown(
    FOOTER_HTML,
    unsafe_allow_html=True,
)
