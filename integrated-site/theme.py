"""BookRec дизайны: CSS, SVG-безендіру және HTML бөлшектері (Streamlit-ке тәуелсіз)."""
import html
from urllib.parse import quote

GENRE_NAMES = {
    "роман_повесть_әңгіме": "Роман, повесть, әңгіме",
    "тарихи_проза": "Тарихи проза",
    "мемуарлық_проза": "Мемуарлық проза",
    "балалар_прозасы": "Балалар прозасы",
    "детектив": "Детектив",
}
GENRE_GRADIENT = {
    "роман_повесть_әңгіме": "linear-gradient(180deg,#6d5aa8 0%,#d98a4e 70%,#f0b36a 100%)",
    "тарихи_проза": "linear-gradient(180deg,#6b3b1f 0%,#c07a3a 70%,#e8b878 100%)",
    "мемуарлық_проза": "linear-gradient(180deg,#4b4b52 0%,#9a8f80 70%,#d9cbb4 100%)",
    "балалар_прозасы": "linear-gradient(180deg,#2f5d4a 0%,#6fa388 70%,#bfd8c0 100%)",
    "детектив": "linear-gradient(180deg,#3d5a8a 0%,#7fa0c9 70%,#c9d8e6 100%)",
}

# Тек сенімді білетін жылдар (атау бойынша). Қалғаны үшін жыл көрсетілмейді.
YEARS = {"Абай жолы": 1942, "Ақбілек": 1928, "Қан мен тер": 1961, "Менің атым Қожа": 1957}


def esc(x) -> str:
    return html.escape(str(x))


HERO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 560 420">
<defs>
<linearGradient id="b1" x1="0" x2="1"><stop offset="0" stop-color="#2a170b"/><stop offset=".6" stop-color="#4b2b16"/><stop offset="1" stop-color="#2f1c0e"/></linearGradient>
<linearGradient id="b2" x1="0" x2="1"><stop offset="0" stop-color="#33200f"/><stop offset=".6" stop-color="#5a3820"/><stop offset="1" stop-color="#3b2512"/></linearGradient>
<linearGradient id="b3" x1="0" x2="1"><stop offset="0" stop-color="#6a4220"/><stop offset=".6" stop-color="#946334"/><stop offset="1" stop-color="#744a26"/></linearGradient>
<linearGradient id="q" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#3a2212"/><stop offset=".5" stop-color="#8a5a34"/><stop offset="1" stop-color="#d1a574"/></linearGradient>
</defs>
<ellipse cx="270" cy="392" rx="260" ry="14" fill="#8a5a34" opacity=".22"/>
<rect x="40" y="292" width="338" height="70" rx="6" fill="#f1e2c4"/>
<rect x="58" y="284" width="352" height="70" rx="8" fill="url(#b3)"/>
<rect x="66" y="292" width="336" height="54" rx="5" fill="none" stroke="#e8c98f" stroke-width="1.5" opacity=".7"/>
<text x="118" y="328" font-family="Georgia,'Noto Serif',serif" font-size="25" fill="#f4dcaa">Қан мен тер</text>
<rect x="66" y="218" width="318" height="62" rx="6" fill="#f1e2c4"/>
<rect x="84" y="208" width="336" height="66" rx="8" fill="url(#b2)"/>
<text x="150" y="250" font-family="Georgia,'Noto Serif',serif" font-size="26" fill="#f0d29a">Көшпенділер</text>
<g transform="rotate(-4 280 160)">
<rect x="112" y="124" width="318" height="74" rx="10" fill="url(#b1)"/>
<rect x="124" y="134" width="294" height="54" rx="6" fill="none" stroke="#d8b070" stroke-width="2" opacity=".75"/>
<rect x="132" y="140" width="34" height="42" rx="3" fill="none" stroke="#d8b070" stroke-width="1.5" opacity=".7"/>
<text x="205" y="173" font-family="Georgia,'Noto Serif',serif" font-size="28" fill="#f2d49a">Абай жолы</text>
</g>
<path d="M440 334 Q440 292 470 282 L512 282 Q542 292 542 334 Q542 356 491 358 Q440 356 440 334Z" fill="#1d120b"/>
<ellipse cx="491" cy="282" rx="24" ry="7" fill="#3a2515"/>
<rect x="472" y="262" width="38" height="22" rx="4" fill="#2a1a10"/>
<ellipse cx="491" cy="262" rx="20" ry="6" fill="#4a301c"/>
<ellipse cx="468" cy="320" rx="8" ry="22" fill="#fff" opacity=".13"/>
<path d="M494 262 C468 192 478 92 552 14 C540 70 550 124 522 172 C510 204 504 232 494 262Z" fill="url(#q)"/>
<path d="M494 262 C500 180 522 92 552 14" fill="none" stroke="#2a170b" stroke-width="3"/>
<g stroke="#3a2212" stroke-width="1" opacity=".35" fill="none">
<path d="M500 230 L526 190"/><path d="M504 200 L534 150"/><path d="M508 170 L538 110"/><path d="M514 140 L544 70"/>
<path d="M490 220 L478 170"/><path d="M492 190 L484 130"/><path d="M498 150 L498 90"/>
</g></svg>"""

HERO_URI = "data:image/svg+xml;utf8," + quote(HERO_SVG, safe="")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif:ital,wght@0,400;0,600;0,700;1,400;1,600&display=swap');
:root{ --bg:#fbeee0; --card:#fff9f2; --ink:#3a2012; --brown:#6b3a20; --brown2:#8a5232; --line:#e4c9ad; --chip:#f6e0c8; }
html, body, [class*="st-"], .stApp, button, input, textarea{ font-family:'Noto Serif', Georgia, serif !important; }
span[data-testid="stIconMaterial"], [data-testid="stIconMaterial"]{
  font-family:"Material Symbols Rounded","Material Symbols Outlined" !important;
  font-feature-settings:"liga"; letter-spacing:normal; text-transform:none; font-size:1.2rem; }
.stApp{ background:linear-gradient(180deg,#fdf1e4 0%,#f9e8d6 100%); color:var(--ink); }
#MainMenu, footer, header[data-testid="stHeader"]{ display:none !important; }
.block-container{ padding:1rem 2rem 2rem; max-width:1280px; }

/* ---------- шапка ---------- */
.logo{ font-size:2.6rem; font-weight:700; color:var(--brown2); line-height:1; letter-spacing:-.5px; }
.logo span{ color:var(--brown); }
.logo b{ color:#4a2412; font-weight:700; }
.logo-sub{ font-size:.74rem; letter-spacing:.3em; color:var(--ink); margin-top:.3rem; }
.nav-line{ border:none; border-top:1px solid var(--line); margin:.7rem -2rem 0; }

/* ---------- батырмалар ---------- */
.stButton > button{ border-radius:999px; border:1px solid var(--brown2); background:transparent; color:var(--ink);
  padding:.4rem 1.1rem; font-size:.9rem; min-height:0; transition:all .15s; }
.stButton > button p{ color:inherit; font-size:.9rem; }
.stButton > button:hover{ background:var(--chip); border-color:var(--brown); color:var(--brown); }
.stButton > button[kind="primary"]{ background:var(--brown); color:#fff8f0; border-color:var(--brown); }
.stButton > button[kind="primary"]:hover{ background:#55301a; color:#fff; }

/* ---------- hero ---------- */
.st-key-hero{ position:relative; border-radius:0 0 30px 30px; padding:2.6rem 3rem 2.4rem; margin:0 -2rem 1.6rem; min-height:400px;
  background:url("__HERO__") no-repeat right 3% center / auto 92%,
             radial-gradient(circle at 82% 30%, #f3d7bb 0%, #f8e3cd 42%, #fbeee0 100%); }
.eyebrow{ font-size:.8rem; letter-spacing:.12em; color:var(--brown); text-transform:uppercase; margin-bottom:.9rem; }
.eyebrow:before,.eyebrow:after{ content:""; display:inline-block; width:56px; height:1px; background:var(--brown2); vertical-align:middle; margin:0 .8rem 0 0; }
.eyebrow:after{ margin:0 0 0 .8rem; width:36px; }
.hero-h{ font-size:3.5rem; line-height:1.1; margin:0 0 1.8rem; font-weight:700; color:#2f170a; letter-spacing:-.5px; }
.hero-h em{ color:var(--brown2); font-weight:600; }
.hero-p{ font-size:1.02rem; max-width:560px; margin:0 0 1.4rem; line-height:1.6; }
.st-key-hero [data-testid="stForm"]{ max-width:62%; border:none; padding:0; background:transparent; }
.st-key-hero div[data-baseweb="input"]{ background:#fffaf4 !important; border:1px solid var(--line) !important; border-radius:999px !important; min-height:56px; }
.st-key-hero [data-testid="stFormSubmitButton"] button{ width:46px; height:46px; border-radius:50%; padding:0; background:var(--brown); color:#fff; border-color:var(--brown); }
@media (max-width:900px){ .st-key-hero{ background-size:0 0, auto; padding:1.6rem 1.2rem; } .hero-h{ font-size:2.2rem; } .st-key-hero [data-testid="stForm"]{ max-width:100%; } }

/* ---------- секция ---------- */
.sec-eyebrow{ font-size:.8rem; letter-spacing:.12em; color:var(--brown); text-transform:uppercase; }
.sec-eyebrow:after{ content:""; display:inline-block; width:40px; height:1px; background:var(--brown2); vertical-align:middle; margin-left:.7rem; }
.sec-title{ font-size:2.2rem; font-weight:700; margin:.15rem 0 .25rem; color:#2f170a; }
.sec-sub{ color:#5d4030; margin-bottom:1.1rem; }
.st-key-allbooks{ display:flex; justify-content:flex-end; margin-top:2.4rem; }

/* ---------- карточка ---------- */
div[data-testid="stVerticalBlockBorderWrapper"]{ background:var(--card); border-color:var(--line) !important; border-radius:18px !important;
  box-shadow:0 4px 14px rgba(107,58,32,.07); }
[class*="st-key-card_"]{ position:relative; }
[class*="st-key-heart_"]{ position:absolute; top:6px; right:8px; width:auto !important; z-index:5; }
[class*="st-key-heart_"] button{ border:none; background:transparent; padding:0 .2rem; font-size:1.25rem; color:var(--brown2); }
[class*="st-key-heart_"] button:hover{ background:transparent; color:var(--brown); }
[class*="st-key-more_"] button{ flex-direction:row-reverse; gap:.3rem; width:100%; justify-content:center; padding:.4rem .5rem; white-space:nowrap; }
[class*="st-key-more_"] button p{ font-size:.82rem; white-space:nowrap; }
.cover{ position:relative; height:210px; border-radius:8px; padding:12px 8px; color:#fff8ea; overflow:hidden;
  box-shadow:0 6px 14px rgba(60,30,10,.3); }
.cover .ct{ position:relative; z-index:2; font-size:.8rem; font-weight:700; line-height:1.15; text-transform:uppercase; text-align:center; text-shadow:0 1px 3px rgba(0,0,0,.55); }
.cover .ca{ position:absolute; z-index:2; left:0; right:0; bottom:6px; text-align:center; font-size:.62rem; opacity:.95; }
.cover svg{ position:absolute; left:0; right:0; bottom:0; width:100%; height:55%; z-index:1; }
.b-title{ font-size:1.15rem; font-weight:700; margin:0; line-height:1.2; padding-right:1.6rem; color:#2f170a; }
.b-author{ font-size:.85rem; color:#6b5444; margin:.25rem 0 .6rem; }
.chip{ display:inline-block; background:var(--chip); border-radius:999px; padding:.18rem .7rem; font-size:.76rem; }
.b-year{ font-size:.85rem; margin:.55rem 0 .5rem; color:#4a3022; min-height:1.2rem; }
.sim{ font-size:.78rem; color:var(--brown); margin:.1rem 0 .3rem; }
.bar{ height:5px; background:var(--chip); border-radius:5px; overflow:hidden; margin-bottom:.4rem; }
.bar i{ display:block; height:100%; background:var(--brown2); }

/* ---------- футер ---------- */
.foot{ display:flex; align-items:center; gap:1.2rem; margin:2.6rem -2rem -2rem; padding:1.4rem 2rem; border-top:1px solid var(--line); }
.foot .l{ flex:1; height:1px; background:var(--line); }
.foot .c{ text-align:center; }
.foot .logo{ font-size:1.8rem; }
.foot .c small{ display:block; letter-spacing:.28em; font-size:.62rem; margin-top:.2rem; }
.foot .r{ flex:1; font-size:.72rem; color:#6b5444; text-align:right; }

/* ---------- inputs (қараңғы режимде де ашық түсті) ---------- */
[data-testid="stWidgetLabel"] p, label, .stApp [data-testid="stCaptionContainer"]{ color:var(--ink) !important; }
div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="select"] > div{
  background:#fffaf4 !important; border:1px solid var(--line) !important; border-radius:14px !important; }
.stApp input, .stApp textarea, div[data-baseweb="select"] *{ color:var(--ink) !important; -webkit-text-fill-color:var(--ink); }
.stApp input::placeholder{ color:#9a8070 !important; -webkit-text-fill-color:#9a8070; }
[data-testid="stNumberInput"] button{ background:transparent !important; color:var(--ink) !important; border:none !important; }
span[data-baseweb="tag"]{ background:var(--chip) !important; color:var(--ink) !important; }
span[data-baseweb="tag"] *{ color:var(--ink) !important; }
div[data-baseweb="popover"], div[data-baseweb="popover"] > div, div[data-baseweb="popover"] ul,
div[data-baseweb="popover"] li, [data-testid="stPopoverBody"]{ background:#3a2012 !important; }
div[data-baseweb="popover"] *{ color:#fff4e6 !important; -webkit-text-fill-color:#fff4e6; }
div[data-baseweb="popover"] li:hover, div[data-baseweb="popover"] li[aria-selected="true"]{ background:#6b3a20 !important; }
[data-testid="stPopoverBody"]{ border:1px solid var(--brown2) !important; border-radius:16px !important; min-width:230px; }
[data-testid="stPopoverBody"] .stButton > button{ border-color:#d8b98f; color:#fff4e6; justify-content:flex-start; }
[data-testid="stPopoverBody"] .stButton > button:hover{ background:#6b3a20; color:#fff; }
[data-testid="stPopoverBody"] .stButton > button[kind="primary"]{ background:#8a5232; border-color:#8a5232; }

/* ☰ мәзір батырмасы (оң жақ жоғарыда) */
.st-key-menu{ display:flex; justify-content:flex-end; }
.st-key-menu button{ font-size:1.5rem; padding:.15rem .9rem; line-height:1.2;
  background:#fffaf4 !important; border:1px solid var(--brown2) !important; border-radius:14px !important; }
.st-key-menu button, .st-key-menu button *{ color:var(--brown) !important; -webkit-text-fill-color:var(--brown); }
.st-key-menu button:hover{ background:var(--chip) !important; }
[data-testid="stAlert"]{ background:#fff4e6 !important; color:var(--ink) !important; border:1px solid var(--line); }
[data-testid="stAlert"] *{ color:var(--ink) !important; }
</style>
""".replace("__HERO__", HERO_URI.replace('"', "%22"))


def cover_html(title: str, author: str, genre: str) -> str:
    grad = GENRE_GRADIENT.get(genre, "linear-gradient(180deg,#6b3a20,#c07a3a)")
    return (
        f'<div class="cover" style="background:{grad}"><div class="ct">{esc(title)}</div>'
        '<svg viewBox="0 0 100 60" preserveAspectRatio="none">'
        '<ellipse cx="72" cy="12" rx="8" ry="4.6" fill="#ffe6a8" opacity=".85"/>'
        '<path d="M0 34 Q25 18 50 30 T100 24 V60 H0Z" fill="rgba(30,15,5,.35)"/>'
        '<path d="M0 46 Q30 34 60 44 T100 38 V60 H0Z" fill="rgba(20,10,3,.55)"/></svg>'
        f'<div class="ca">{esc(author)}</div></div>'
    )


def logo_html(sub: str = "ҚАЗАҚ ӘДЕБИЕТІ") -> str:
    return f'<div class="logo">Book<span>Rec</span></div><div class="logo-sub">{esc(sub)}</div>'


HERO_HTML = (
    '<div class="eyebrow">Қазақ әдебиетінің әлеміне қош келдіңіз</div>'
    '<div class="hero-h">Әр кітаптың өз әлемі бар.<br><em>Өзіңіздікін табыңыз.</em></div>'
)

FOOTER_HTML = (
    '<div class="foot"><div class="l"></div><div class="c"><div class="logo">Book<span>Rec</span></div>'
    '<small>ҚАЗАҚ ӘДЕБИЕТІН БІРГЕ ЗЕРТТЕЙІК</small></div><div class="l"></div>'
    '<div class="r">© 2026 BookRec. Оқу жобасы: деректер мен оқырмандар синтетикалық.</div></div>'
)
