"""BookRec — қазақ әдебиетіне арналған Streamlit сервисі."""
import html
import math
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="BookRec | Қазақ әдебиеті",page_icon="📖",layout="wide",initial_sidebar_state="collapsed")
@st.cache_data
def catalog():
    df=pd.read_csv("books.csv").fillna("")
    df["book_id"]=df.book_id.astype(int)
    return df
books=catalog()
st.session_state.setdefault("page","Басты бет")
st.session_state.setdefault("selected",int(books.book_id.iloc[0]))
st.session_state.setdefault("favs",[])
st.session_state.setdefault("query","")
st.session_state.setdefault("page_no",1)
def esc(x): return html.escape(str(x),quote=True)
def go(page,bid=None):
    st.session_state.page=page
    if bid is not None: st.session_state.selected=int(bid)
def toggle(bid):
    f=st.session_state.favs
    if bid in f: f.remove(bid)
    else: f.append(bid)
def svg_cover(row):
    colors=["#8c624e","#537b69","#5e7b88","#b48b55","#725365","#6a6f46"]
    bg=colors[int(row.book_id)%len(colors)]
    title=esc(row.title)
    author=esc(row.author)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="340" height="480" viewBox="0 0 340 480"><rect width="340" height="480" fill="{bg}"/><rect x="15" y="15" width="310" height="450" rx="2" fill="none" stroke="#e5cfa0" stroke-width="2"/><path d="M60 280 Q170 210 280 280 M60 290 Q170 220 280 290" stroke="#e5cfa0" stroke-width="3" fill="none" opacity=".5"/><circle cx="170" cy="184" r="70" stroke="#dfc5a4" fill="none" opacity=".5"/><text x="170" y="85" text-anchor="middle" font-family="Georgia" font-size="14" fill="#f7e6cd">BOOKREC • ҚАЗАҚ ӘДЕБИЕТІ</text><foreignObject x="32" y="315" width="276" height="100"><div xmlns="http://www.w3.org/1999/xhtml" style="font: bold 25px Georgia; color:#fff2de; text-align:center;overflow-wrap:anywhere;">{title}</div></foreignObject><foreignObject x="40" y="417" width="260" height="45"><div xmlns="http://www.w3.org/1999/xhtml" style="font: 15px Georgia; color:#fff2de; text-align:center;">{author}</div></foreignObject></svg>"""
def cover(row):
    return svg_cover(row).encode("utf-8")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&display=swap');
:root {--chocolate:#62391f;--ink:#2f1b10;--cream:#fbecdd}
.stApp {background:linear-gradient(110deg,#fff2e5,#f9e9da);color:var(--ink)}
.block-container {max-width:1450px;padding-top:1.25rem;padding-bottom:2rem}
header[data-testid="stHeader"],#MainMenu,footer {display:none}
h1,h2,h3 {font-family:'Playfair Display',Georgia,serif!important;color:var(--ink)}
body,p,button,input {font-family:'DM Sans',sans-serif}
.stButton button {border-radius:80px;border:1px solid #c2a48b;background:transparent;color:var(--ink)}
.stButton button:hover {color:#fff;background:#73452a;border-color:#73452a}
.stButton button[kind="primary"] {background:#62391f;color:#fff;border:1px solid #62391f}
.brand {font:700 44px 'Playfair Display',Georgia,serif;letter-spacing:-2px}
.brand span {color:#975b37}
.brandline {font:bold 11px 'DM Sans',sans-serif;letter-spacing:.23em}
.rule {height:1px;background:#d8bba5;margin:10px 0 24px}
.hero {padding:45px 36px 40px;border-radius:4px;background:radial-gradient(circle at 86% 55%,#b98761 0,#d4b097 18%,transparent 37%),linear-gradient(100deg,#fae8d6 55%,#e5c5a9);min-height:340px;position:relative;overflow:hidden}
.hero:after {content:"📚";position:absolute;right:7%;top:10%;font-size:160px;opacity:.38;transform:rotate(-5deg)}
.hero h1 {font-size:clamp(39px,4.4vw,68px);letter-spacing:-2px;line-height:1.12;margin:10px 0}
.hero h1 em {color:#814b2e;font-weight:400}
.hero p {font:18px/1.5 Georgia;color:#3b271a}
.kicker {font:bold 12px 'DM Sans';letter-spacing:.08em;color:#70452d}
.section {font:600 38px 'Playfair Display',Georgia,serif;margin:4px 0}
.copyright {text-align:center;border-top:1px solid #dfc3ae;margin-top:35px;padding-top:25px;font:12px 'DM Sans';color:#7c5d49}
.cardheading {font:700 20px 'Playfair Display',Georgia,serif;line-height:1.2;min-height:52px}
.author {font:13px 'DM Sans';color:#745641;min-height:38px}
.synopsis {font:13px/1.55 'DM Sans';color:#6a4b3a;min-height:62px}
.chip {display:inline-block;background:#f2dcc9;border-radius:99px;padding:4px 9px;font:12px 'DM Sans';color:#58341f}
div[data-testid="stVerticalBlockBorderWrapper"] {border:1px solid #ead5c1;background:#fffaf4bb;border-radius:15px}
[data-testid="stImage"] img {border-radius:5px;box-shadow:0 3px 12px #48322128}
@media(max-width:800px){.hero {padding:25px 18px}.hero:after{opacity:.15}.brand{font-size:32px}.section{font-size:29px}}
</style>
""",unsafe_allow_html=True)

nav=st.columns([3,1.18,1,1.25,1.35],gap="small",vertical_alignment="center")
with nav[0]:
    st.markdown('<div class="brand">Book<span>Rec</span></div><div class="brandline">ҚАЗАҚ ӘДЕБИЕТІ</div>',unsafe_allow_html=True)
for c,page,icon in zip(nav[1:],["Басты бет","Кітаптар","Ұсыныстар","Таңдаулылар"],["⌂","▤","✦","♡"]):
    with c: st.button(f"{icon} {page}",key="nav"+page,type="primary" if st.session_state.page==page else "secondary",on_click=go,args=(page,),use_container_width=True)
st.markdown('<div class="rule"></div>',unsafe_allow_html=True)

def section(eyebrow,title,caption=""):
    st.markdown(f'<div class="kicker">{esc(eyebrow)}</div><div class="section">{esc(title)}</div><p>{esc(caption)}</p>',unsafe_allow_html=True)
def cards(df,key):
    rows=list(df.itertuples(index=False))
    for ix in range(0,len(rows),4):
        cols=st.columns(4,gap="small")
        for col,r in zip(cols,rows[ix:ix+4]):
            with col:
                with st.container(border=True):
                    img,text=st.columns([.9,1.1],gap="small")
                    with img:st.image(cover(r),use_container_width=True)
                    with text:
                        st.markdown(f'<div class="cardheading">{esc(r.title)}</div><div class="author">{esc(r.author)}</div><span class="chip">{esc(str(r.genre).split(",")[0])}</span>',unsafe_allow_html=True)
                        d=str(r.description).strip() or "Шығарманың мазмұндық сипаттамасы әлі тексерілмеген."
                        st.markdown(f'<div class="synopsis">{esc(d)}</div>',unsafe_allow_html=True)
                        st.button("Толығырақ →",key=f"detail_{key}_{r.book_id}",on_click=go,args=("Кітап туралы",r.book_id),type="primary",use_container_width=True)
                    st.button("♥ Таңдаулыда" if r.book_id in st.session_state.favs else "♡ Таңдаулыға",key=f"fav_{key}_{r.book_id}",on_click=toggle,args=(r.book_id,),use_container_width=True)

page=st.session_state.page
if page=="Басты бет":
    st.markdown('<div class="hero"><div class="kicker">ҚАЗАҚ ӘДЕБИЕТІНІҢ ӘЛЕМІНЕ ҚОШ КЕЛДІҢІЗ</div><h1>Әр кітаптың өз әлемі бар.<br><em>Өзіңіздікін табыңыз.</em></h1><p>Қазақ әдебиетінің бай мұрасын зерттеңіз.<br>Жасанды интеллект көмегімен келесі сүйікті кітабыңызды табыңыз.</p></div>',unsafe_allow_html=True)
    with st.form("hero-search"):
        a,b=st.columns([9,1],vertical_alignment="bottom")
        q=a.text_input("Кітаптың атауын немесе авторын іздеңіз",value=st.session_state.query,placeholder="Кітаптың атауын немесе авторын іздеңіз...")
        if b.form_submit_button("➜",use_container_width=True):
            st.session_state.query=q
            st.rerun()
    if st.session_state.query:
        mask=books.title.str.contains(st.session_state.query,case=False,regex=False)|books.author.str.contains(st.session_state.query,case=False,regex=False)
        found=books[mask]
        section("ІЗДЕУ НӘТИЖЕЛЕРІ",f"{len(found)} кітап табылды")
        cards(found.head(12),"search")
        if st.button("Іздеуді тазарту"):
            st.session_state.query=""
            st.rerun()
    else:
        section("БІЗДІҢ ЖИНАҚ","Оқуға тұрарлық шығармалар","Қазақ әдебиетіндегі ерекше туындылармен танысыңыз.")
        selected=[]
        for target in ["Абай жолы: 1-том","Ақбілек","Қан мен тер","Менің атым Қожа"]:
            match=books[books.title.str.casefold()==target.casefold()]
            if not match.empty:selected.append(match.iloc[0])
        cards(pd.DataFrame(selected) if selected else books.head(4),"home")
        st.button("Барлық кітаптар →",on_click=go,args=("Кітаптар",))
elif page=="Кітаптар":
    section("БІЗДІҢ КАТАЛОГ",f"{len(books)} кітап","Барлық шығармаларды іздеңіз және сүзгілеңіз.")
    a,b=st.columns([2,1])
    query=a.text_input("Атауы немесе авторы",placeholder="Іздеу...")
    opts=["Барлығы"]+sorted(books.genre_group.unique().tolist())
    choice=b.selectbox("Жанр",opts)
    mask=books.title.str.contains(query,case=False,regex=False)|books.author.str.contains(query,case=False,regex=False)
    selected=books[mask]
    if choice!="Барлығы":selected=selected[selected.genre_group==choice]
    per=16
    total=max(1,math.ceil(len(selected)/per))
    p=st.number_input("Бет",min_value=1,max_value=total,value=1)
    st.caption(f"{len(selected)} кітап · {p}/{total} бет")
    cards(selected.iloc[(p-1)*per:p*per],"catalog")
elif page=="Ұсыныстар":
    section("AI ҰСЫНЫСТАРЫ","Өзіңізге ұқсас кітап табыңыз","TF-IDF және Cosine Similarity негізіндегі ұсыныстар.")
    names={f"{r.title} — {r.author} (#{r.book_id})":r.book_id for r in books.itertuples()}
    chosen=st.multiselect("Ұнаған кітаптарыңыз",list(names),default=[k for k,v in names.items() if v in st.session_state.favs],placeholder="Бір немесе бірнеше кітапты таңдаңыз")
    if chosen:
        docs=(books.title+" "+books.author+" "+books.genre+" "+books.description).tolist()
        matrix=TfidfVectorizer(analyzer="char_wb",ngram_range=(2,5),sublinear_tf=True).fit_transform(docs)
        idx=[books.index[books.book_id==names[x]][0] for x in chosen]
        import numpy as np
        profile=np.asarray(matrix[idx].mean(axis=0))
        scores=cosine_similarity(profile,matrix).ravel()
        scores[idx]=-1
        order=np.argsort(-scores)[:8]
        cards(books.iloc[order],"recommend")
        st.caption("Ұқсастық мәтін бойынша есептеледі. Бұл болашақ ұнатудың ықтималдығы емес.")
    else:st.info("Ұсыныс алу үшін бір кітап таңдаңыз.")
elif page=="Таңдаулылар":
    section("МЕНІҢ ТІЗІМІМ","Таңдаулылар","Сізге қызық кітаптар.")
    selected=books[books.book_id.isin(st.session_state.favs)]
    if len(selected):cards(selected,"favorites")
    else:st.info("Әзірше таңдаулылар жоқ.")
elif page in ["Кітап туралы","Оқу"]:
    row=books.set_index("book_id").loc[st.session_state.selected]
    st.button("← Кітаптарға",on_click=go,args=("Кітаптар",))
    if page=="Кітап туралы":
        a,b=st.columns([1,3],gap="large")
        with a:st.image(cover(row),use_container_width=True)
        with b:
            st.markdown(f"## {esc(row.title)}")
            st.markdown(f"### {esc(row.author)}")
            st.write(f"{row.genre} · {row.pages} бет")
            st.write(row.description if str(row.description).strip() else "Мазмұн туралы расталған сипаттама әлі енгізілмеген.")
            st.caption(f"Дереккөзі: {row.source}. Мұқаба — уақытша типографиялық иллюстрация.")
            st.button("Осы сайтта оқу →",type="primary",on_click=go,args=("Оқу",))
            st.button("♥ Таңдаулыда" if row.name in st.session_state.favs else "♡ Таңдаулыға",on_click=toggle,args=(int(row.name),))
    else:
        section("ОҚУ БЕТІ",row.title,str(row.author))
        url=str(row.read_url).strip()
        st.info("Кітап осы бетте ашылады, егер бастапқы сайт кірістірілген терезеге рұқсат берсе. Кейбір дереккөздер бұған тыйым салады.")
        if url.startswith(("https://","http://")):
            components.iframe(url,height=750,scrolling=True)
            st.markdown(f"[Дереккөзде ашу]({url})")
        else:st.warning("Бұл кітапқа жарамды оқу сілтемесі жоқ.")
st.markdown('<div class="copyright"><div class="brand">Book<span>Rec</span></div>ҚАЗАҚ ӘДЕБИЕТІН БІРГЕ ЗЕРТТЕЙІК · © 2026 BookRec</div>',unsafe_allow_html=True)
