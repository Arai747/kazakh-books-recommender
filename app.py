"""BookRec — қазақ әдебиетінің интерактивті кітапханасы."""
from __future__ import annotations
import html
from urllib.parse import quote
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="BookRec — Қазақ әдебиеті", page_icon="📚",
                   layout="wide", initial_sidebar_state="collapsed")

@st.cache_data
def load_books():
    df = pd.read_csv("books.csv").fillna("")
    df["book_id"] = pd.to_numeric(df["book_id"], errors="coerce").fillna(0).astype(int)
    return df

@st.cache_resource
def tfidf():
    text = (books["title"].astype(str) + " " + books["author"].astype(str) + " " +
            books["genre"].astype(str) + " " + books["description"].astype(str)).tolist()
    return TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), min_df=1).fit_transform(text)

books = load_books()
by_id = books.set_index("book_id")
q = st.query_params
page = q.get("page", "home")
if page not in ("home", "books", "recommend", "favorites", "detail", "read"):
    page = "home"
try:
    selected_id = int(q.get("id", "1"))
except (ValueError, TypeError):
    selected_id = 1
if selected_id not in by_id.index:
    selected_id = int(books.iloc[0]["book_id"])
favs = [int(v) for v in q.get("fav", "").split(",") if v.isdecimal()]
favs = list(dict.fromkeys(favs))
try:
    change = int(q.get("toggle", "0"))
except (ValueError, TypeError):
    change = 0
if change:
    if change in favs:
        favs.remove(change)
    else:
        favs.append(change)
    st.query_params["fav"] = ",".join(map(str, favs))
    if "toggle" in st.query_params:
        del st.query_params["toggle"]
    st.rerun()

def escape(v):
    return html.escape(str(v), quote=True)

def link(page="home", book_id=None, **params):
    args = {"page": page}
    if book_id is not None:
        args["id"] = book_id
    if favs:
        args["fav"] = ",".join(map(str, favs))
    args.update({k: v for k, v in params.items() if v is not None})
    return "?" + "&".join(quote(str(k)) + "=" + quote(str(v)) for k, v in args.items())

def snippet(v):
    v = str(v).strip()
    return v if v else "Мазмұны бойынша расталған сипаттама әзірге қосылмаған."

def cover(book):
    colors = [
        ("#7d4d40", "#bd9371"), ("#356756", "#87a283"),
        ("#3e6980", "#9cc6bd"), ("#9a633a", "#e2b783"),
        ("#61517a", "#b8a4c5"), ("#6d7050", "#c5b887")
    ]
    first, second = colors[int(book["book_id"]) % len(colors)]
    title = escape(book["title"])
    author = escape(book["author"])
    return (
        f'<div class="cover" style="--c1:{first};--c2:{second}">'
        '<div class="cover-border"></div><div class="cover-top">ҚАЗАҚ ӘДЕБИЕТІ</div>'
        '<div class="cover-art"><span>✦</span><span>❦</span><span>✦</span></div>'
        f'<div class="cover-name">{title}</div><div class="cover-author">{author}</div></div>'
    )

def book_card(book):
    bid = int(book["book_id"])
    liked = bid in favs
    toggle_url = link(page, selected_id if page in ("detail", "read") else None, toggle=bid)
    if page == "books" and "genre" in q:
        toggle_url = link("books", toggle=bid, genre=q["genre"])
    name = escape(book["title"])
    author = escape(book["author"])
    genre = escape(str(book["genre"]).split(",")[0])
    desc = escape(snippet(book["description"]))
    return (
        '<article class="book-card">'
        f'<a href="{escape(link("detail", bid))}" class="cover-link">{cover(book)}</a>'
        '<div class="book-info">'
        f'<a class="favorite {"chosen" if liked else ""}" title="Таңдаулыға қосу" href="{escape(toggle_url)}">{"♥" if liked else "♡"}</a>'
        f'<h3><a href="{escape(link("detail", bid))}">{name}</a></h3>'
        f'<div class="book-author">{author}</div>'
        f'<span class="genre">{genre}</span>'
        f'<p class="book-description">{desc}</p>'
        f'<a class="detail-btn" href="{escape(link("detail", bid))}">Толығырақ <span>→</span></a>'
        '</div></article>'
    )

def grid(data):
    if data.empty:
        st.info("Бұл сұраныс бойынша кітап табылмады.")
        return
    st.markdown('<div class="book-grid">' + "".join(book_card(r) for _, r in data.iterrows()) + '</div>',
                unsafe_allow_html=True)

style = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600&display=swap');
:root{--ink:#311d13;--brown:#714024;--line:#d9bca4;--muted:#795b46;--paper:#fff9f2}
html,body,.stApp{background:#f9ede1!important;color:var(--ink)}
#MainMenu,header[data-testid="stHeader"],footer,[data-testid="stDecoration"]{display:none!important}
.block-container{padding:0 35px 24px!important;max-width:1500px!important}
[data-testid="stAppViewContainer"]>.main{background:linear-gradient(125deg,#faebdf,#fff4e8 55%,#f8e9db)}
h1,h2,h3{font-family:'Playfair Display',Georgia,serif!important}
a{text-decoration:none!important;color:inherit}
.site-header{height:90px;display:flex;justify-content:space-between;align-items:center;gap:20px}
.brand{font:700 45px/.9 'Playfair Display',Georgia,serif;letter-spacing:-2px}
.brand span{color:#975a36}
.brand-sub{font:700 10px 'DM Sans',sans-serif;letter-spacing:3px;margin-top:7px}
.navigation{display:flex;gap:12px;align-items:center}
.navigation a{font:500 12px 'DM Sans',sans-serif;border:1px solid #a88b73;border-radius:40px;padding:11px 18px;white-space:nowrap;transition:.2s}
.navigation a.active,.navigation a:hover{background:#714024;color:white;border-color:#714024}
.navigation .nav-icon{font-size:16px;margin-right:9px}
.top-rule{border-top:1px solid #d8bba4;margin:0 -35px}
.hero{min-height:344px;margin:0 -35px;padding:35px 5.2%;background:radial-gradient(circle at 83% 65%,#caa080aa,transparent 33%),linear-gradient(100deg,#fae8d6,#f1d1b4);position:relative;overflow:hidden}
.hero-copy{position:relative;z-index:1;max-width:720px}
.kicker{font:600 12px 'DM Sans',sans-serif;letter-spacing:.06em;color:#6a402b;margin-bottom:10px}
.kicker:before,.kicker:after{display:inline-block;content:"";height:1px;width:50px;background:#986c53;vertical-align:middle;margin:0 12px 3px 0}
.kicker:after{width:25px;margin:0 0 3px 12px}
.hero h1{font:600 clamp(36px,4.7vw,67px)/1.08 'Playfair Display',Georgia,serif;letter-spacing:-2px;margin:0 0 15px;color:#29160e}
.hero h1 em{font-weight:400;color:#824c2e}
.hero p{font:18px/1.35 Georgia,serif;max-width:680px;margin:0;color:#3e281e}
.hero-art{position:absolute;right:5%;bottom:0;width:33%;height:100%;pointer-events:none}
.art-book{position:absolute;right:15%;height:49px;width:70%;bottom:38px;background:linear-gradient(180deg,#805339,#4c2d1b);border:5px solid #9b7250;border-radius:7px 14px 14px 5px;box-shadow:0 11px 19px #5f371c52;transform:rotate(-3deg)}
.art-book.two{bottom:93px;right:5%;transform:rotate(4deg);background:linear-gradient(#9b6845,#5b3521)}
.art-book.three{bottom:150px;right:15%;transform:rotate(-5deg);background:linear-gradient(#70503b,#3f291c)}
.art-book:after{content:"";position:absolute;right:11%;top:5px;height:29px;width:60%;border-right:6px solid #d5a77b;border-left:2px solid #d5a77b}
.art-feather{position:absolute;right:6%;top:10px;font-size:134px;transform:rotate(17deg);filter:sepia(1);opacity:.85}
.hero-search{max-width:670px;margin-top:17px}
.hero-search .stTextInput>div>div{border-radius:40px!important;background:#fffaf5!important;border:1px solid #dbc1aa!important;min-height:48px}
.hero-search [data-testid="stForm"]{border:0!important;padding:0!important}
.hero-search [data-testid="stFormSubmitButton"] button{border-radius:40px!important;background:#714024!important;color:white!important;border:0!important;min-height:48px}
section.content-section{padding:25px 0 10px}
.section-label{font:700 13px 'DM Sans',sans-serif;letter-spacing:1px;color:#7b4e37}
.section-label:after{content:"";display:inline-block;width:80px;height:1px;background:#997057;vertical-align:middle;margin-left:14px}
.section-heading{font:600 clamp(28px,3vw,40px)/1.15 'Playfair Display',Georgia,serif;color:#2e1a11;margin:3px 0}
.section-sub{font:17px Georgia,serif;color:#644736;margin:0 0 16px}
.book-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:13px;margin:12px 0 22px}
.book-card{border:1px solid #ead7c8;background:#fffaf5bb;border-radius:14px;display:flex;padding:13px;gap:13px;min-height:218px;min-width:0;box-shadow:0 2px 7px #68442d0b}
.book-card .cover-link{flex:0 0 43%;min-width:0;display:flex}
.cover{width:100%;min-height:188px;aspect-ratio:2/3;background:linear-gradient(145deg,var(--c1),var(--c2));border-radius:4px;box-shadow:3px 3px 8px #51301b3b;position:relative;overflow:hidden;display:flex;flex-direction:column;align-items:center;text-align:center;justify-content:flex-end;padding:13px 9px;color:#fff0d9}
.cover-border{position:absolute;inset:6px;border:1px solid #f9dfbc88;pointer-events:none}
.cover-top{position:absolute;top:14px;font:600 7px 'DM Sans',sans-serif;letter-spacing:1px}
.cover-art{position:absolute;top:25%;font-size:18px;opacity:.6;display:flex;gap:8px;align-items:center}
.cover-art span:nth-child(2){font-size:53px}
.cover-name{position:relative;font:700 clamp(13px,1.4vw,21px)/1.08 'Playfair Display',Georgia,serif;overflow-wrap:anywhere;max-height:95px;overflow:hidden;text-shadow:0 1px 4px #0003}
.cover-author{position:relative;font:10px/1.3 'DM Sans',sans-serif;margin-top:9px;max-height:29px;overflow:hidden}
.book-info{flex:1;min-width:0;display:flex;flex-direction:column;position:relative;padding-top:15px}
.book-info h3{font:700 17px/1.15 'Playfair Display',Georgia,serif;margin:0 20px 8px 0;overflow-wrap:anywhere}
.book-author{font:12px/1.35 'DM Sans',sans-serif;min-height:30px;color:#624534}
.genre{display:table;align-self:flex-start;border-radius:20px;background:#f1ddca;color:#55321f;font:11px 'DM Sans',sans-serif;padding:4px 9px;margin:7px 0}
.book-description{font:11px/1.4 'DM Sans',sans-serif;color:#715341;margin:0 0 7px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.detail-btn{display:flex;justify-content:center;align-items:center;gap:10px;color:white!important;background:#704026;border-radius:22px;text-align:center;padding:8px 6px;font:11px 'DM Sans',sans-serif;margin-top:auto}
.detail-btn:hover{background:#4d2a17}
.favorite{position:absolute;right:-2px;top:-5px;border-radius:100%;background:#fffaf4;border:1px solid #ebddcf;width:27px;height:27px;text-align:center;font-size:22px;line-height:22px;color:#825239}
.favorite.chosen{color:#b44d42}
.view-all{border:1px solid #a98b75;border-radius:30px;padding:10px 18px;display:inline-block;font:12px 'DM Sans',sans-serif}
.view-all:hover{background:#704026;color:white}
.page-head{padding:30px 0 9px}
.reader-note{font-size:14px;color:#624534}
.detail-layout{display:grid;grid-template-columns:230px 1fr;gap:35px;max-width:970px;margin:20px auto}
.detail-layout .cover{max-width:230px;min-height:350px}
.detail-layout h1{font-size:42px;line-height:1.1}
.detail-layout p{font-size:17px;line-height:1.6}
.info-line{color:#7b5640;font-size:14px}
.action-row{display:flex;gap:10px;flex-wrap:wrap}
.action-row a{border-radius:30px;padding:10px 18px;background:#704026;color:white}
.action-row .outline{background:transparent;color:#704026;border:1px solid #704026}
.footer{border-top:1px solid #dfc4b0;text-align:center;margin:30px -35px 0;padding:18px;color:#785947;font:12px 'DM Sans',sans-serif}
.footer strong{display:block;color:#382014;font:600 29px 'Playfair Display',Georgia,serif}
.stButton button{background:#704026!important;color:white!important;border:0!important;border-radius:25px!important}
[data-testid="stTextInput"] input{background:#fffaf5}
@media(max-width:1250px){.book-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.book-card .cover-link{flex-basis:37%}.book-info h3{font-size:19px}.cover-name{font-size:21px}}
@media(max-width:740px){.block-container{padding:0 15px 20px!important}.top-rule,.hero,.footer{margin-left:-15px;margin-right:-15px}.site-header{height:auto;padding:15px 0;flex-direction:column;align-items:flex-start}.brand{font-size:37px}.navigation{width:100%;overflow-x:auto;gap:6px;padding-bottom:4px}.navigation a{padding:8px 10px;font-size:11px}.navigation .nav-icon{margin-right:4px}.hero{padding:24px 20px 28px;min-height:300px}.hero h1{font-size:38px}.hero p{font-size:15px}.hero-art{opacity:.16;width:70%}.book-grid{grid-template-columns:1fr}.book-card .cover-link{flex-basis:38%}.cover-name{font-size:20px}.detail-layout{grid-template-columns:1fr;gap:12px}.detail-layout .cover{width:180px;min-height:270px}.detail-layout h1{font-size:34px}}
</style>
"""
st.markdown(style, unsafe_allow_html=True)

tabs = [
    ("home", "⌂", "Басты бет"),
    ("books", "▤", "Кітаптар"),
    ("recommend", "✦", "Ұсыныстар"),
    ("favorites", "♡", "Таңдаулылар")
]
nav = "".join(
    f'<a class="{"active" if page == target else ""}" href="{escape(link(target))}">'
    f'<span class="nav-icon">{icon}</span>{name}</a>'
    for target, icon, name in tabs
)
st.markdown(
    '<div class="site-header"><div><div class="brand">Book<span>Rec</span></div>'
    '<div class="brand-sub">ҚАЗАҚ ӘДЕБИЕТІ</div></div>'
    f'<nav class="navigation">{nav}</nav></div><div class="top-rule"></div>',
    unsafe_allow_html=True
)

def section(label, heading, sub=""):
    st.markdown(
        f'<section class="content-section"><div class="section-label">{escape(label)}</div>'
        f'<div class="section-heading">{escape(heading)}</div>'
        f'<p class="section-sub">{escape(sub)}</p></section>',
        unsafe_allow_html=True
    )

if page == "home":
    st.markdown(
        '<div class="hero"><div class="hero-copy">'
        '<div class="kicker">ҚАЗАҚ ӘДЕБИЕТІНІҢ ӘЛЕМІНЕ ҚОШ КЕЛДІҢІЗ</div>'
        '<h1>Әр кітаптың өз әлемі бар.<br><em>Өзіңіздікін табыңыз.</em></h1>'
        '<p>Қазақ әдебиетінің бай мұрасын зерттеңіз.<br>'
        'Жасанды интеллект көмегімен келесі сүйікті кітабыңызды табыңыз.</p>'
        '</div><div class="hero-art"><div class="art-book"></div>'
        '<div class="art-book two"></div><div class="art-book three"></div>'
        '<div class="art-feather">🪶</div></div></div>', unsafe_allow_html=True)
    with st.container():
        with st.form("home_search", border=False):
            a,b=st.columns([8,1],vertical_alignment="bottom")
            query=a.text_input("Кітаптың атауы немесе авторы",placeholder="Кітаптың атауын немесе авторын іздеңіз...",label_visibility="collapsed")
            submit=b.form_submit_button("Іздеу",use_container_width=True)
            if submit:
                st.query_params["page"]="books"
                st.query_params["search"]=query
                st.rerun()
    section("БІЗДІҢ ЖИНАҚ","Оқуға тұрарлық шығармалар",
            "Қазақ әдебиетіндегі ерекше туындылармен танысыңыз.")
    wanted=["Абай жолы: 1-том","Ақбілек","Қан мен тер","Менің атым Қожа"]
    choices=pd.concat([books[books.title.str.casefold()==name.casefold()].head(1) for name in wanted])
    grid(choices if len(choices) else books.head(4))
    st.markdown(f'<div style="text-align:right"><a class="view-all" href="{escape(link("books"))}">Барлық кітаптар →</a></div>',unsafe_allow_html=True)
elif page == "books":
    section("КІТАПХАНА",f"Кітаптар каталогы · {len(books)}",
            "Атауы, авторы немесе жанры бойынша қалаған шығармаңызды табыңыз.")
    with st.form("catalog_search", border=False):
        a,b,c=st.columns([3,2,1],vertical_alignment="bottom")
        search=a.text_input("Іздеу",value=q.get("search",""),placeholder="Кітап немесе автор")
        genres=["Барлық жанр"]+sorted(books.genre.astype(str).unique().tolist())
        current_genre=q.get("genre","Барлық жанр")
        index=genres.index(current_genre) if current_genre in genres else 0
        genre=b.selectbox("Жанр",genres,index=index)
        go=c.form_submit_button("Іздеу",use_container_width=True)
        if go:
            st.query_params["search"]=search
            st.query_params["genre"]=genre
            st.query_params["page"]="books"
            st.query_params.pop("p",None)
            st.rerun()
    selected=books
    if q.get("search","").strip():
        needle=q["search"].strip()
        selected=selected[
            selected.title.str.contains(needle,case=False,regex=False) |
            selected.author.str.contains(needle,case=False,regex=False)
        ]
    if q.get("genre","Барлық жанр")!="Барлық жанр":
        selected=selected[selected.genre==q["genre"]]
    st.caption(f"{len(selected)} кітап табылды")
    try:
        p=max(1,int(q.get("p","1")))
    except ValueError:
        p=1
    per=16
    total=max(1,(len(selected)+per-1)//per)
    p=min(p,total)
    grid(selected.iloc[(p-1)*per:p*per])
    if total>1:
        st.markdown('<div style="display:flex;gap:12px;justify-content:center;padding-top:10px">'
            + (f'<a class="view-all" href="{escape(link("books",search=q.get("search",""),genre=q.get("genre","Барлық жанр"),p=p-1))}">← Артқа</a>' if p>1 else '')
            + f'<span style="padding:10px">{p} / {total}</span>'
            + (f'<a class="view-all" href="{escape(link("books",search=q.get("search",""),genre=q.get("genre","Барлық жанр"),p=p+1))}">Келесі →</a>' if p<total else '')+'</div>',
            unsafe_allow_html=True)
elif page == "favorites":
    section("МЕНІҢ КІТАПТАРЫМ","Таңдаулылар","Жүрекшемен белгілеген кітаптарыңыз.")
    grid(books[books.book_id.isin(favs)])
elif page == "recommend":
    section("AI ҰСЫНЫСТАРЫ","Сізге ұқсас кітаптар",
            "TF-IDF және Cosine Similarity арқылы тақырыбы ұқсас шығармаларды іздейміз.")
    options={f'{r.title} — {r.author} (№{r.book_id})':int(r.book_id) for r in books.itertuples()}
    choice=st.selectbox("Қай кітап сізге ұнайды?",list(options),index=0)
    n=st.slider("Ұсыныс саны",min_value=3,max_value=12,value=8)
    if choice:
        pos=books.index[books.book_id==options[choice]][0]
        matrix=tfidf()
        sim=cosine_similarity(matrix[pos],matrix).ravel()
        sim[pos]=-1
        picks=np.argsort(-sim)[:n]
        grid(books.iloc[picks])
        st.caption("Ұқсастық кітаптар туралы мәтінге негізделген; бұл бағалау немесе болжау ықтималдығы емес.")
elif page in ("detail","read"):
    book=by_id.loc[selected_id]
    if page=="detail":
        details=(
            '<div class="detail-layout">'
            f'{cover(book)}<div><div class="section-label">КІТАП ТУРАЛЫ</div>'
            f'<h1>{escape(book["title"])}</h1>'
            f'<p class="info-line">{escape(book["author"])} · {escape(book["genre"])}'
            f' · {escape(book["pages"])} бет</p>'
            f'<p>{escape(snippet(book["description"]))}</p>'
            f'<p class="info-line">Дереккөз: {escape(book["source"])}. Мұқаба уақытша дизайн ретінде жасалған.</p>'
            '<div class="action-row">'
            f'<a href="{escape(link("read",selected_id))}">Осы сайтта оқу →</a>'
            f'<a class="outline" href="{escape(link("detail",selected_id,toggle=selected_id))}">'
            f'{"♥ Таңдаулыдан алу" if selected_id in favs else "♡ Таңдаулыға қосу"}</a>'
            '</div></div></div>'
        )
        st.markdown(details,unsafe_allow_html=True)
    else:
        section("ОНЛАЙН ОҚУ",str(book["title"]),str(book["author"]))
        url=str(book["read_url"]).strip()
        st.info("Дереккөз рұқсат берсе, кітап төменде сайттың ішінде ашылады. Кейбір сайттар бұған техникалық шектеу қояды.")
        if url.startswith(("https://","http://")):
            components.iframe(url,height=780,scrolling=True)
            st.markdown(f'[Кітап ашылмаса, түпнұсқа дереккөзін қарау]({url})')
        else:
            st.warning("Бұл кітаптың оқу сілтемесі әлі қосылмаған.")
        st.markdown(f'<a class="view-all" href="{escape(link("detail",selected_id))}">← Кітап туралы</a>',unsafe_allow_html=True)
st.markdown('<div class="footer"><strong>BookRec</strong>ҚАЗАҚ ӘДЕБИЕТІН БІРГЕ ЗЕРТТЕЙІК · © 2026 BookRec</div>',unsafe_allow_html=True)
