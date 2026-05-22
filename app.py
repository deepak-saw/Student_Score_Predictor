import streamlit as st
import joblib
import pandas as pd
import json
import os
import io
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ── ReportLab imports ──
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT

st.set_page_config(
    page_title="EduPredict | Student Performance Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing:border-box; margin:0; padding:0; }
html, body, .stApp { background:#050912 !important; color:#dce3f0; font-family:'DM Sans',sans-serif; }
#MainMenu, footer, header { visibility:hidden; }
.stDeployButton,[data-testid="stToolbar"],[data-testid="stDecoration"] { display:none; }

.stApp::before {
    content:''; position:fixed; inset:0; z-index:0; pointer-events:none;
    background:
        radial-gradient(ellipse 90% 70% at 5% 10%, rgba(0,114,255,.14) 0%, transparent 55%),
        radial-gradient(ellipse 70% 60% at 95% 90%, rgba(0,255,213,.09) 0%, transparent 55%),
        radial-gradient(ellipse 50% 50% at 50% 50%, rgba(124,58,237,.07) 0%, transparent 65%);
}
.stApp::after {
    content:''; position:fixed; inset:0; z-index:0; pointer-events:none;
    background-image: linear-gradient(rgba(0,255,213,.018) 1px,transparent 1px), linear-gradient(90deg,rgba(0,255,213,.018) 1px,transparent 1px);
    background-size:80px 80px;
    animation:gridScroll 30s linear infinite;
}
@keyframes gridScroll { to { background-position:0 80px; } }

.nav-bar {
    display:flex; align-items:center; justify-content:space-between;
    padding:18px 56px; position:relative; z-index:100;
    border-bottom:1px solid rgba(255,255,255,.05);
    background:rgba(5,9,18,.85); backdrop-filter:blur(16px);
}
.nav-logo { font-family:'Syne',sans-serif; font-size:22px; font-weight:800; color:#dce3f0; letter-spacing:-0.5px; }
.nav-logo .accent { color:#00ffd5; }
.nav-links { display:flex; gap:36px; font-size:13px; color:#6b7a99; font-weight:500; }
.nav-links span { cursor:pointer; transition:color .2s; }
.nav-links span:hover { color:#00ffd5; }
.nav-pill {
    padding:9px 24px; background:linear-gradient(135deg,#00ffd5,#0072ff);
    border-radius:99px; font-family:'Syne',sans-serif; font-size:13px; font-weight:700;
    color:#050912; cursor:pointer; box-shadow:0 4px 24px rgba(0,255,213,.3);
    transition:all .2s;
}
.nav-pill:hover { box-shadow:0 8px 32px rgba(0,255,213,.45); transform:translateY(-1px); }

.hero-section { padding:90px 56px 50px; text-align:center; position:relative; z-index:5; }
.hero-badge {
    display:inline-flex; align-items:center; gap:8px; padding:6px 18px;
    background:rgba(0,255,213,.07); border:1px solid rgba(0,255,213,.2);
    border-radius:99px; font-size:11px; font-weight:600; color:#00ffd5;
    letter-spacing:1.2px; text-transform:uppercase; margin-bottom:30px;
    animation:fadeUp .6s ease both;
}
.hero-badge .pulse { width:6px; height:6px; background:#00ffd5; border-radius:50%; animation:blink 1.5s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(0,255,213,.4)} 50%{opacity:.4;box-shadow:0 0 0 6px rgba(0,255,213,0)} }
.hero-title {
    font-family:'Syne',sans-serif;
    font-size:clamp(38px,5.5vw,72px); font-weight:800; line-height:1.06;
    letter-spacing:-2.5px; color:#dce3f0; margin-bottom:22px;
    animation:fadeUp .7s .1s ease both;
}
.hero-title .hl {
    background:linear-gradient(135deg,#00ffd5 0%,#0072ff 50%,#7c3aed 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.hero-desc {
    font-size:17px; color:#6b7a99; line-height:1.75; max-width:540px; margin:0 auto 44px;
    animation:fadeUp .7s .2s ease both; font-weight:300;
}
@keyframes fadeUp { from{opacity:0;transform:translateY(24px)} to{opacity:1;transform:translateY(0)} }

.stats-wrap {
    display:flex; justify-content:center; align-items:center; gap:0;
    padding:0 56px 64px; position:relative; z-index:5;
    animation:fadeUp .7s .3s ease both;
}
.stat-box { text-align:center; padding:0 48px; }
.stat-num {
    font-family:'Syne',sans-serif; font-size:40px; font-weight:800;
    background:linear-gradient(135deg,#00ffd5,#0072ff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
    line-height:1;
}
.stat-lbl { font-size:12px; color:#6b7a99; margin-top:6px; letter-spacing:.5px; font-weight:400; }
.stat-sep { width:1px; height:50px; background:rgba(255,255,255,.08); }

.section-wrap { padding:0 56px 72px; position:relative; z-index:5; }
.section-eyebrow {
    font-size:11px; font-weight:700; color:#00ffd5; text-transform:uppercase;
    letter-spacing:2px; text-align:center; margin-bottom:12px;
}
.section-title {
    font-family:'Syne',sans-serif; font-size:34px; font-weight:800;
    color:#dce3f0; text-align:center; letter-spacing:-1px; margin-bottom:8px;
}
.section-sub { text-align:center; color:#6b7a99; font-size:14px; margin-bottom:48px; }
.features-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; max-width:1000px; margin:0 auto; }
.feat-card {
    background:rgba(255,255,255,.025); border:1px solid rgba(255,255,255,.07);
    border-radius:20px; padding:32px 26px; transition:all .3s ease;
    position:relative; overflow:hidden;
}
.feat-card::after {
    content:''; position:absolute; inset:0; border-radius:20px;
    background:linear-gradient(135deg,rgba(0,255,213,.06),transparent 60%);
    opacity:0; transition:opacity .3s;
}
.feat-card:hover { border-color:rgba(0,255,213,.25); transform:translateY(-4px); box-shadow:0 20px 60px rgba(0,0,0,.4); }
.feat-card:hover::after { opacity:1; }
.feat-icon-wrap {
    width:52px; height:52px; border-radius:14px;
    background:linear-gradient(135deg,rgba(0,114,255,.2),rgba(0,255,213,.1));
    border:1px solid rgba(0,255,213,.15);
    display:flex; align-items:center; justify-content:center;
    font-size:24px; margin-bottom:18px;
}
.feat-name { font-family:'Syne',sans-serif; font-size:16px; font-weight:700; color:#dce3f0; margin-bottom:8px; }
.feat-text { font-size:13px; color:#6b7a99; line-height:1.65; }

.hiw-wrap { max-width:900px; margin:0 auto; padding:0 56px 72px; position:relative; z-index:5; }
.steps-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:24px; }
.step-card {
    background:rgba(255,255,255,.025); border:1px solid rgba(255,255,255,.07);
    border-radius:20px; padding:28px 24px; text-align:center; position:relative;
}
.step-badge {
    display:inline-flex; align-items:center; justify-content:center;
    width:44px; height:44px; border-radius:12px;
    background:linear-gradient(135deg,#0072ff,#00ffd5);
    font-family:'Syne',sans-serif; font-size:20px; font-weight:800; color:#050912;
    margin-bottom:16px; box-shadow:0 8px 24px rgba(0,114,255,.3);
}
.step-name { font-family:'Syne',sans-serif; font-size:15px; font-weight:700; color:#dce3f0; margin-bottom:8px; }
.step-text { font-size:13px; color:#6b7a99; line-height:1.6; }

.auth-wrapper { max-width:500px; margin:0 auto; padding:0 24px 80px; position:relative; z-index:5; }
.auth-head { text-align:center; margin-bottom:32px; }
.auth-head-title { font-family:'Syne',sans-serif; font-size:28px; font-weight:800; color:#dce3f0; letter-spacing:-0.8px; margin-bottom:8px; }
.auth-head-sub { font-size:14px; color:#6b7a99; }

.auth-card {
    background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.09);
    border-radius:24px; padding:38px 34px;
    backdrop-filter:blur(24px);
    box-shadow:0 40px 100px rgba(0,0,0,.6), 0 0 0 1px rgba(255,255,255,.04) inset;
    position:relative; overflow:hidden;
}
.auth-card::before {
    content:''; position:absolute; top:0; left:10%; right:10%; height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,255,213,.6),transparent);
}
.auth-form-title { font-family:'Syne',sans-serif; font-size:22px; font-weight:700; color:#dce3f0; margin-bottom:4px; }
.auth-form-sub { font-size:13px; color:#6b7a99; margin-bottom:26px; line-height:1.5; }
.a-divider { display:flex; align-items:center; gap:12px; color:#374151; font-size:11px; margin:22px 0; text-transform:uppercase; letter-spacing:.6px; }
.a-divider::before,.a-divider::after { content:''; flex:1; height:1px; background:rgba(255,255,255,.06); }

.stTextInput > div > div > input {
    background:rgba(255,255,255,.05) !important; border:1px solid rgba(255,255,255,.1) !important;
    border-radius:12px !important; color:#dce3f0 !important;
    font-family:'DM Sans',sans-serif !important; font-size:15px !important;
    padding:13px 16px !important; transition:all .25s !important;
}
.stTextInput > div > div > input:focus {
    border-color:#00ffd5 !important; background:rgba(0,255,213,.04) !important;
    box-shadow:0 0 0 3px rgba(0,255,213,.1) !important; outline:none !important;
}
.stTextInput label {
    color:#6b7a99 !important; font-size:11px !important; font-weight:600 !important;
    text-transform:uppercase !important; letter-spacing:1px !important; font-family:'DM Sans',sans-serif !important;
}
.stCheckbox label { color:#9aa3b5 !important; font-size:13px !important; }
.stCheckbox input[type="checkbox"] { accent-color:#00ffd5 !important; }
.stCaption { color:#6b7a99 !important; font-size:12px !important; }

.stButton > button {
    width:100% !important;
    background:linear-gradient(135deg,#00ffd5,#0072ff) !important;
    color:#050912 !important; font-family:'Syne',sans-serif !important;
    font-size:15px !important; font-weight:700 !important;
    border:none !important; border-radius:14px !important;
    padding:15px 20px !important; letter-spacing:.3px !important;
    box-shadow:0 8px 32px rgba(0,255,213,.2) !important;
    transition:all .25s !important; cursor:pointer !important;
}
.stButton > button:hover {
    transform:translateY(-2px) !important; box-shadow:0 14px 44px rgba(0,255,213,.4) !important;
}
div[data-testid="stAlert"] { border-radius:12px !important; font-family:'DM Sans',sans-serif !important; font-size:14px !important; }
.stSelectbox > div > div { background:rgba(255,255,255,.05) !important; border:1px solid rgba(255,255,255,.1) !important; border-radius:12px !important; color:#dce3f0 !important; }
.stSlider label { color:#9aa3b5 !important; font-size:13px !important; font-weight:500 !important; }

section[data-testid="stSidebar"] { background:#080e1c !important; border-right:1px solid rgba(255,255,255,.05) !important; }
section[data-testid="stSidebar"] .stButton > button {
    background:linear-gradient(135deg,#ff5e7a,#c0392b) !important;
    color:white !important; box-shadow:0 4px 20px rgba(255,94,122,.25) !important;
}

.dash-hero { padding:32px 0 24px; position:relative; z-index:5; }
.dash-greeting { font-size:13px; color:#00ffd5; font-weight:600; letter-spacing:1px; text-transform:uppercase; margin-bottom:6px; }
.dash-title { font-family:'Syne',sans-serif; font-size:40px; font-weight:800; color:#dce3f0; letter-spacing:-1.5px; line-height:1.1; margin-bottom:8px; }
.dash-title .acc { color:#00ffd5; }
.dash-sub { color:#6b7a99; font-size:14px; font-weight:300; }

.kpi-card {
    background:rgba(255,255,255,.03); border:1px solid rgba(255,255,255,.07);
    border-radius:18px; padding:24px 20px; text-align:center; position:relative; overflow:hidden;
    transition:all .25s;
}
.kpi-card::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; background:linear-gradient(90deg,#0072ff,#00ffd5); }
.kpi-card:hover { border-color:rgba(0,255,213,.2); transform:translateY(-3px); box-shadow:0 16px 48px rgba(0,0,0,.4); }
.kpi-icon { font-size:28px; margin-bottom:10px; }
.kpi-label { font-family:'Syne',sans-serif; font-size:14px; font-weight:700; color:#dce3f0; margin-bottom:4px; }
.kpi-sub { font-size:12px; color:#6b7a99; }

.input-card {
    background:rgba(255,255,255,.025); border:1px solid rgba(255,255,255,.07);
    border-radius:22px; padding:32px 28px;
    box-shadow:0 8px 48px rgba(0,0,0,.4); margin-bottom:24px;
    position:relative; overflow:hidden;
}
.input-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,114,255,.5),transparent);
}
.input-section-title {
    font-family:'Syne',sans-serif; font-size:17px; font-weight:700; color:#dce3f0;
    margin-bottom:20px; display:flex; align-items:center; gap:8px;
}

.score-card {
    background:linear-gradient(135deg,rgba(0,114,255,.08),rgba(0,255,213,.04));
    border:1px solid rgba(0,255,213,.15); border-radius:22px;
    padding:40px 28px; text-align:center; margin-bottom:24px;
    position:relative; overflow:hidden;
    box-shadow:0 0 80px rgba(0,255,213,.06);
}
.score-card::before { content:''; position:absolute; top:0; left:10%; right:10%; height:1px; background:linear-gradient(90deg,transparent,#00ffd5,transparent); }
.score-big {
    font-family:'Syne',sans-serif; font-size:96px; font-weight:800; line-height:1;
    background:linear-gradient(135deg,#00ffd5,#0072ff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.score-grade {
    display:inline-block; padding:6px 20px; border-radius:99px;
    background:linear-gradient(135deg,#0072ff,#7c3aed);
    font-family:'Syne',sans-serif; font-size:14px; font-weight:700; color:white;
    margin:12px 0 8px; box-shadow:0 4px 20px rgba(0,114,255,.3);
}
.score-remark { font-size:15px; color:#6b7a99; letter-spacing:.3px; }

/* Download button special styling */
.stDownloadButton > button {
    background:linear-gradient(135deg,#7c3aed,#0072ff) !important;
    color:white !important;
    box-shadow:0 8px 32px rgba(124,58,237,.3) !important;
}
.stDownloadButton > button:hover {
    box-shadow:0 14px 44px rgba(124,58,237,.5) !important;
}
</style>
""", unsafe_allow_html=True)

# =========================
# USER FILE
# =========================
USER_FILE = "users.json"
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# =========================
# PDF REPORT GENERATOR
# =========================
def generate_pdf_report(username, hours, attendance, previous, sleep,
                        motivation, teacher, school, internet,
                        final_score, grade, remark):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    # Colors
    TEAL    = colors.HexColor("#00ffd5")
    BLUE    = colors.HexColor("#0072ff")
    PURPLE  = colors.HexColor("#7c3aed")
    LIGHT   = colors.HexColor("#dce3f0")
    MUTED   = colors.HexColor("#6b7a99")
    CARD_BG = colors.HexColor("#0d1526")
    DARK_BG = colors.HexColor("#0a1020")
    BORDER  = colors.HexColor("#1a2744")
    RED     = colors.HexColor("#ef4444")
    AMBER   = colors.HexColor("#f59e0b")

    GRADE_COLOR = {
        "A+": TEAL, "A": BLUE, "B": PURPLE, "C": AMBER, "D": RED
    }.get(grade, TEAL)

    def ps(name, **kw):
        return ParagraphStyle(name, **kw)

    S = {
        "brand":   ps("brand",   fontName="Helvetica-Bold", fontSize=14, textColor=TEAL,   alignment=TA_CENTER, spaceAfter=2),
        "title":   ps("title",   fontName="Helvetica-Bold", fontSize=24, textColor=LIGHT,  alignment=TA_CENTER, spaceAfter=4),
        "sub":     ps("sub",     fontName="Helvetica",      fontSize=9,  textColor=MUTED,  alignment=TA_CENTER, spaceAfter=2),
        "section": ps("section", fontName="Helvetica-Bold", fontSize=11, textColor=TEAL,   spaceAfter=8, spaceBefore=12, leftIndent=2),
        "normal":  ps("normal",  fontName="Helvetica",      fontSize=10, textColor=LIGHT,  spaceAfter=5, leading=16),
        "score":   ps("score",   fontName="Helvetica-Bold", fontSize=56, textColor=TEAL,   alignment=TA_CENTER),
        "grade":   ps("grade",   fontName="Helvetica-Bold", fontSize=20, textColor=GRADE_COLOR, alignment=TA_CENTER, spaceAfter=2),
        "remark":  ps("remark",  fontName="Helvetica",      fontSize=12, textColor=LIGHT,  alignment=TA_CENTER),
        "th":      ps("th",      fontName="Helvetica-Bold", fontSize=9,  textColor=LIGHT,  alignment=TA_CENTER),
        "td":      ps("td",      fontName="Helvetica",      fontSize=9,  textColor=LIGHT,  alignment=TA_LEFT),
        "tdc":     ps("tdc",     fontName="Helvetica",      fontSize=9,  textColor=LIGHT,  alignment=TA_CENTER),
        "footer":  ps("footer",  fontName="Helvetica",      fontSize=7,  textColor=MUTED,  alignment=TA_CENTER),
        "tip":     ps("tip",     fontName="Helvetica",      fontSize=9,  textColor=LIGHT,  spaceAfter=4, leading=14, leftIndent=8),
    }

    def prog_bar(val, max_val, bar_color):
        pct   = max(0.0, min(1.0, val / max_val))
        done  = int(pct * 28)
        empty = 28 - done
        hex_c = bar_color.hexval()[2:]
        hex_m = BORDER.hexval()[2:]
        txt   = f'<font color="#{hex_c}">{"█"*done}</font><font color="#{hex_m}">{"█"*empty}</font>'
        return Paragraph(txt, ps("pb", fontName="Courier", fontSize=8, textColor=LIGHT, alignment=TA_CENTER))

    def colored(text, col):
        h = col.hexval()[2:]
        return Paragraph(f'<font color="#{h}"><b>{text}</b></font>',
                         ps("cb", fontName="Helvetica-Bold", fontSize=9, textColor=col, alignment=TA_CENTER))

    story = []

    # ── HEADER ──
    story.append(Paragraph("EduPredict", S["brand"]))
    story.append(Paragraph("AI Student Performance Report", S["title"]))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}   |   Student: {username}",
        S["sub"]))
    story.append(Spacer(1, 0.25*cm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=TEAL, spaceAfter=12))

    # ── SCORE CARD TABLE ──
    score_tbl = Table([
        [Paragraph(str(final_score), S["score"])],
        [Paragraph(f"Grade: {grade}", S["grade"])],
        [Paragraph(remark, S["remark"])],
    ], colWidths=[16*cm])
    score_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), CARD_BG),
        ("BOX",           (0,0), (-1,-1), 2, GRADE_COLOR),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 14),
        ("BOTTOMPADDING", (0,-1),(-1,-1), 16),
    ]))
    story.append(score_tbl)
    story.append(Spacer(1, 0.4*cm))

    # ── ACADEMIC INPUTS ──
    story.append(Paragraph("Academic Inputs", S["section"]))
    acad_rows = [
        [Paragraph("Metric", S["th"]),   Paragraph("Value", S["th"]),
         Paragraph("Progress", S["th"]), Paragraph("Max", S["th"])],
        [Paragraph("Hours Studied / Day", S["td"]),
         Paragraph(f"{hours} hrs", S["tdc"]),
         prog_bar(hours, 24, TEAL),
         Paragraph("24 hrs", S["tdc"])],
        [Paragraph("Attendance", S["td"]),
         Paragraph(f"{attendance}%", S["tdc"]),
         prog_bar(attendance, 100, BLUE),
         Paragraph("100%", S["tdc"])],
        [Paragraph("Previous Score", S["td"]),
         Paragraph(f"{previous} / 100", S["tdc"]),
         prog_bar(previous, 100, PURPLE),
         Paragraph("100", S["tdc"])],
        [Paragraph("Sleep Hours / Day", S["td"]),
         Paragraph(f"{sleep} hrs", S["tdc"]),
         prog_bar(sleep, 12, TEAL),
         Paragraph("12 hrs", S["tdc"])],
    ]
    acad_tbl = Table(acad_rows, colWidths=[5*cm, 2.5*cm, 6*cm, 2.5*cm])
    acad_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  CARD_BG),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),  [DARK_BG, CARD_BG]),
        ("BOX",           (0,0),(-1,-1),  0.8, BORDER),
        ("INNERGRID",     (0,0),(-1,-1),  0.4, BORDER),
        ("LINEBELOW",     (0,0),(-1,0),   1.5, TEAL),
        ("ALIGN",         (0,0),(-1,-1),  "CENTER"),
        ("VALIGN",        (0,0),(-1,-1),  "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1),  7),
        ("BOTTOMPADDING", (0,0),(-1,-1),  7),
    ]))
    story.append(acad_tbl)
    story.append(Spacer(1, 0.35*cm))

    # ── ENVIRONMENTAL FACTORS ──
    story.append(Paragraph("Environmental Factors", S["section"]))

    mot_c = {"High": TEAL,   "Medium": AMBER, "Low": RED}
    tq_c  = {"Good": TEAL,   "Average": AMBER, "Poor": RED}
    sc_c  = {"Private": TEAL, "Public": BLUE}
    in_c  = {"Yes": TEAL,    "No": RED}

    env_rows = [
        [Paragraph("Factor", S["th"]),       Paragraph("Value", S["th"]),
         Paragraph("Factor", S["th"]),       Paragraph("Value", S["th"])],
        [Paragraph("Motivation Level", S["td"]),  colored(motivation, mot_c.get(motivation, MUTED)),
         Paragraph("Teacher Quality",  S["td"]),  colored(teacher,    tq_c.get(teacher, MUTED))],
        [Paragraph("School Type",      S["td"]),  colored(school,     sc_c.get(school, MUTED)),
         Paragraph("Internet Access",  S["td"]),  colored(internet,   in_c.get(internet, MUTED))],
    ]
    env_tbl = Table(env_rows, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
    env_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  CARD_BG),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [DARK_BG, CARD_BG]),
        ("BOX",           (0,0),(-1,-1), 0.8, BORDER),
        ("INNERGRID",     (0,0),(-1,-1), 0.4, BORDER),
        ("LINEBELOW",     (0,0),(-1,0),  1.5, BLUE),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
    ]))
    story.append(env_tbl)
    story.append(Spacer(1, 0.35*cm))

    # ── PERFORMANCE INSIGHTS ──
    story.append(HRFlowable(width="100%", thickness=0.6, color=BORDER, spaceAfter=8))
    story.append(Paragraph("Performance Insights", S["section"]))

    tips = []
    if hours < 4:
        tips.append("Study hours are low. Aim for at least 5-6 hours daily to see significant improvement.")
    elif hours >= 7:
        tips.append("Excellent study hours! Consistent hard work is your biggest strength.")

    if attendance < 70:
        tips.append("Attendance is below 70%. Regular attendance strongly impacts your final performance.")
    elif attendance >= 90:
        tips.append("Outstanding attendance! Your regularity gives you a solid academic foundation.")

    if sleep < 6:
        tips.append("You are getting less than 6 hours of sleep. Quality sleep improves memory retention and focus.")
    elif 7 <= sleep <= 9:
        tips.append("Great sleep schedule! 7-9 hours is the optimal range for academic performance.")

    if motivation == "Low":
        tips.append("Motivation is low. Try setting small daily goals and reward yourself for completing them.")
    elif motivation == "High":
        tips.append("High motivation is your superpower — channel it into consistent study sessions!")

    if teacher == "Poor":
        tips.append("Consider supplementing with online resources (YouTube, Khan Academy) to bridge any gaps.")

    if internet == "No":
        tips.append("No internet access detected. Use school or library resources to access study materials.")

    if previous < 50:
        tips.append("Previous scores are low. Review fundamentals and practice past papers regularly.")
    elif previous >= 80:
        tips.append("Strong previous scores — you have a solid base. Focus on maintaining this standard.")

    if not tips:
        tips.append("You have a well-balanced academic profile. Keep maintaining your current habits!")

    for t in tips:
        story.append(Paragraph(f"  *  {t}", S["tip"]))

    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=8))

    # ── FOOTER ──
    story.append(Paragraph(
        f"EduPredict AI  |  Student Performance Portal  |  Confidential Report for {username}",
        S["footer"]))
    story.append(Spacer(1, 0.1*cm))
    story.append(Paragraph(
        "This report is generated by a machine learning model trained on 12,000+ student records. "
        "Results are indicative and should be used as a guide only.",
        S["footer"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# =========================
# SESSION STATE
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "auth_tab" not in st.session_state:
    st.session_state.auth_tab = "signin"

# =========================
# LANDING PAGE
# =========================
if not st.session_state.logged_in:

    users = load_users()

    st.markdown("""
    <div class="nav-bar">
        <div class="nav-logo">🎓 Edu<span class="accent">Predict</span></div>
        <div class="nav-links">
            <span>Features</span><span>How It Works</span><span>About</span>
        </div>
        <div class="nav-pill">Get Started Free</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-section">
        <div class="hero-badge"><div class="pulse"></div>AI-Powered Academic Intelligence</div>
        <h1 class="hero-title">
            Know Your Score<br>Before the <span class="hl">Exam Day</span>
        </h1>
        <p class="hero-desc">
            Enter your study habits, attendance & lifestyle data —
            our ML model predicts your exam score instantly with visual analytics.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="stats-wrap">
        <div class="stat-box"><div class="stat-num">95%</div><div class="stat-lbl">Prediction Accuracy</div></div>
        <div class="stat-sep"></div>
        <div class="stat-box"><div class="stat-num">12K+</div><div class="stat-lbl">Students Analyzed</div></div>
        <div class="stat-sep"></div>
        <div class="stat-box"><div class="stat-num">8</div><div class="stat-lbl">Key Metrics Tracked</div></div>
        <div class="stat-sep"></div>
        <div class="stat-box"><div class="stat-num">&lt;1s</div><div class="stat-lbl">Prediction Time</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="section-wrap">
        <div class="section-eyebrow">Why EduPredict</div>
        <h2 class="section-title">Everything You Need to Succeed</h2>
        <p class="section-sub">Powerful tools designed to give students a data-driven edge</p>
        <div class="features-grid">
            <div class="feat-card">
                <div class="feat-icon-wrap">🧠</div>
                <div class="feat-name">ML-Powered Engine</div>
                <div class="feat-text">Linear regression trained on 12,000+ real student records for high-precision predictions.</div>
            </div>
            <div class="feat-card">
                <div class="feat-icon-wrap">📊</div>
                <div class="feat-name">Visual Analytics</div>
                <div class="feat-text">Beautiful gauge charts and bar graphs give instant insight into your performance drivers.</div>
            </div>
            <div class="feat-card">
                <div class="feat-icon-wrap">⚡</div>
                <div class="feat-name">Instant Results</div>
                <div class="feat-text">Sub-second predictions — no waiting, no processing delays. Just fast, accurate results.</div>
            </div>
            <div class="feat-card">
                <div class="feat-icon-wrap">🔒</div>
                <div class="feat-name">Secure Accounts</div>
                <div class="feat-text">Your data stays private with personalized login — only you can see your predictions.</div>
            </div>
            <div class="feat-card">
                <div class="feat-icon-wrap">🎯</div>
                <div class="feat-name">8 Key Metrics</div>
                <div class="feat-text">Study hours, attendance, sleep, motivation, teacher quality, internet access & more.</div>
            </div>
            <div class="feat-card">
                <div class="feat-icon-wrap">🏆</div>
                <div class="feat-name">Grade & Remarks</div>
                <div class="feat-text">Get your predicted grade (A+, A, B, C, D) and personalized performance remarks.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hiw-wrap">
        <div class="section-eyebrow">How It Works</div>
        <h2 class="section-title">Three Steps to Your Score</h2>
        <p class="section-sub" style="margin-bottom:36px;">Simple, fast, and accurate — no technical knowledge required</p>
        <div class="steps-grid">
            <div class="step-card">
                <div class="step-badge">1</div>
                <div class="step-name">Create Account</div>
                <div class="step-text">Sign up in seconds with just a username and password. No email required.</div>
            </div>
            <div class="step-card">
                <div class="step-badge">2</div>
                <div class="step-name">Enter Your Data</div>
                <div class="step-text">Use sliders & dropdowns to input your study habits, sleep, and other factors.</div>
            </div>
            <div class="step-card">
                <div class="step-badge">3</div>
                <div class="step-name">Get Your Score</div>
                <div class="step-text">Instantly see your predicted exam score, grade, and visual analytics breakdown.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="auth-wrapper">
        <div class="auth-head">
            <div class="auth-head-title">Get Started Today 🚀</div>
            <div class="auth-head-sub">Create a free account or sign in to your dashboard</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    _, center, _ = st.columns([1, 2, 1])
    with center:
        t1, t2 = st.columns(2)
        with t1:
            if st.button("🔐  Sign In", key="tab_signin", use_container_width=True):
                st.session_state.auth_tab = "signin"
                st.rerun()
        with t2:
            if st.button("📝  Create Account", key="tab_signup", use_container_width=True):
                st.session_state.auth_tab = "signup"
                st.rerun()

        st.write("")

        if st.session_state.auth_tab == "signin":
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            st.markdown('<div class="auth-form-title">Welcome back 👋</div>', unsafe_allow_html=True)
            st.markdown('<div class="auth-form-sub">Sign in to access your prediction dashboard</div>', unsafe_allow_html=True)

            username = st.text_input("Username", placeholder="Enter your username", key="si_user")
            password = st.text_input("Password", placeholder="Enter your password", type="password", key="si_pass")

            st.write("")
            if st.button("Sign In →", key="do_signin"):
                if not username or not password:
                    st.error("⚠️ Please fill in all fields")
                elif username in users and users[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")

            st.markdown('<div class="a-divider">or continue with</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1: st.button("🔵  Google", key="g_si")
            with c2: st.button("🐙  GitHub", key="gh_si")
            st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            st.markdown('<div class="auth-form-title">Create account ✨</div>', unsafe_allow_html=True)
            st.markdown('<div class="auth-form-sub">Join EduPredict — free forever, no credit card needed</div>', unsafe_allow_html=True)

            full_name = st.text_input("Full Name", placeholder="Your full name", key="su_name")
            new_user  = st.text_input("Username", placeholder="Choose a username", key="su_user")
            new_pass  = st.text_input("Password", placeholder="Min 6 characters", type="password", key="su_pass")

            if new_pass:
                score = sum([
                    len(new_pass) >= 8,
                    any(c.isupper() for c in new_pass),
                    any(c.isdigit() for c in new_pass),
                    any(c in "!@#$%^&*" for c in new_pass)
                ])
                labels = ["🔴 Weak", "🟠 Fair", "🟡 Good", "🟢 Strong"]
                st.caption(f"Password strength: **{labels[max(0, score-1)]}**")

            agree = st.checkbox("I agree to the Terms of Service and Privacy Policy")
            st.write("")

            if st.button("Create Account →", key="do_signup"):
                if not full_name or not new_user or not new_pass:
                    st.error("⚠️ Please fill in all fields")
                elif not agree:
                    st.warning("⚠️ Please accept the terms to continue")
                elif len(new_pass) < 6:
                    st.error("⚠️ Password too short — minimum 6 characters")
                elif new_user in users:
                    st.error("❌ Username already taken — try another")
                else:
                    users[new_user] = new_pass
                    save_users(users)
                    st.success("🎉 Account created! Click 'Sign In' to login.")
                    st.session_state.auth_tab = "signin"

            st.markdown('<div class="a-divider">or sign up with</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1: st.button("🔵  Google", key="g_su")
            with c2: st.button("🐙  GitHub", key="gh_su")
            st.markdown('</div>', unsafe_allow_html=True)


# =========================
# MAIN DASHBOARD
# =========================
else:
    model   = joblib.load("student_model.pkl")
    columns = joblib.load("model_columns.pkl")

    # Sidebar
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135755.png", width=80)
    st.sidebar.markdown(f"### 👋 {st.session_state.username}")
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🎓 EduPredict**")
    st.sidebar.caption("AI Student Performance Portal")
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📌 Quick Stats**")
    st.sidebar.caption("✅ Model: Linear Regression")
    st.sidebar.caption("📊 Trained on 12K+ records")
    st.sidebar.caption("⚡ Real-time predictions")
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.markdown(f"""
    <div class="dash-hero">
        <div class="dash-greeting">Welcome back</div>
        <div class="dash-title">Performance <span class="acc">Dashboard</span></div>
        <div class="dash-sub">Hello {st.session_state.username} — enter your details below and get your predicted score instantly</div>
    </div>
    """, unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown("""<div class="kpi-card"><div class="kpi-icon">🧠</div>
            <div class="kpi-label">AI Prediction</div><div class="kpi-sub">ML-powered engine</div></div>""",
            unsafe_allow_html=True)
    with k2:
        st.markdown("""<div class="kpi-card"><div class="kpi-icon">📊</div>
            <div class="kpi-label">Visual Analytics</div><div class="kpi-sub">Charts & graphs</div></div>""",
            unsafe_allow_html=True)
    with k3:
        st.markdown("""<div class="kpi-card"><div class="kpi-icon">🎯</div>
            <div class="kpi-label">95% Accuracy</div><div class="kpi-sub">High precision model</div></div>""",
            unsafe_allow_html=True)
    with k4:
        st.markdown("""<div class="kpi-card"><div class="kpi-icon">⚡</div>
            <div class="kpi-label">Instant Results</div><div class="kpi-sub">Under 1 second</div></div>""",
            unsafe_allow_html=True)

    st.write("")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="input-card"><div class="input-section-title">📐 Academic Inputs</div>', unsafe_allow_html=True)
        hours      = st.slider("📚 Hours Studied (per day)", 0, 24, 5)
        attendance = st.slider("🏫 Attendance (%)", 0, 100, 75)
        previous   = st.slider("📋 Previous Score", 0, 100, 60)
        sleep      = st.slider("😴 Sleep Hours", 0, 12, 7)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="input-card"><div class="input-section-title">🎛️ Environmental Factors</div>', unsafe_allow_html=True)
        motivation = st.selectbox("💪 Motivation Level", ["Low", "Medium", "High"])
        teacher    = st.selectbox("👨‍🏫 Teacher Quality", ["Poor", "Average", "Good"])
        school     = st.selectbox("🏛️ School Type", ["Public", "Private"])
        internet   = st.selectbox("🌐 Internet Access", ["Yes", "No"])
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀  Predict My Score"):
        data = {
            "Hours_Studied":    hours,
            "Attendance":       attendance,
            "Previous_Scores":  previous,
            "Sleep_Hours":      sleep,
            "Motivation_Level": motivation,
            "Teacher_Quality":  teacher,
            "School_Type":      school,
            "Internet_Access":  internet
        }
        input_df = pd.DataFrame([data])
        input_df = pd.get_dummies(input_df)
        input_df = input_df.reindex(columns=columns, fill_value=0)
        prediction  = model.predict(input_df)
        final_score = max(40, min(100, int(round(prediction[0]))))

        grade  = "A+" if final_score>=90 else "A" if final_score>=80 else "B" if final_score>=70 else "C" if final_score>=60 else "D"
        remark = ("Outstanding! 🌟" if final_score>=90 else
                  "Excellent! 🎉"   if final_score>=80 else
                  "Good Job! 👍"    if final_score>=70 else
                  "Keep Going! 💪"  if final_score>=60 else
                  "Need Improvement 📖")

        # Score Card
        st.markdown(f"""
        <div class="score-card">
            <div class="score-big">{final_score}</div>
            <div class="score-grade">Grade: {grade}</div>
            <div class="score-remark">{remark}</div>
        </div>
        """, unsafe_allow_html=True)

        # Charts
        r1, r2 = st.columns(2, gap="large")

        with r1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=final_score,
                title={'text': "Performance Score", 'font': {'color': '#dce3f0', 'family': 'Syne', 'size': 15}},
                number={'font': {'color': '#00ffd5', 'family': 'Syne', 'size': 48}},
                gauge={
                    'axis': {'range': [0, 100], 'tickcolor': '#4a5568', 'tickfont': {'color': '#6b7a99'}},
                    'bar': {'color': '#00ffd5', 'thickness': .28},
                    'bgcolor': 'rgba(0,0,0,0)', 'borderwidth': 0,
                    'steps': [
                        {'range': [0, 40],  'color': 'rgba(255,94,122,.12)'},
                        {'range': [40, 70], 'color': 'rgba(255,157,58,.12)'},
                        {'range': [70, 100],'color': 'rgba(0,255,213,.1)'},
                    ],
                    'threshold': {'line': {'color': '#7c3aed', 'width': 4}, 'thickness': .82, 'value': final_score}
                }
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font_color='#dce3f0', height=320,
                margin=dict(t=50, b=20, l=30, r=30)
            )
            st.plotly_chart(fig, use_container_width=True)

        with r2:
            chart_data = pd.DataFrame({
                "Metric": ["Study Hours", "Attendance", "Prev Score", "Sleep Hours"],
                "Value":  [hours, attendance, previous, sleep],
                "Max":    [24, 100, 100, 12]
            })
            chart_data["Percent"] = (chart_data["Value"] / chart_data["Max"] * 100).round(1)

            bar_fig = px.bar(
                chart_data, x="Metric", y="Value",
                color="Value", color_continuous_scale=["#1a3a8f", "#0072ff", "#00ffd5"],
                title="Your Key Metrics Breakdown", text="Value"
            )
            bar_fig.update_traces(marker_line_width=0, textposition='outside', textfont_color='#dce3f0')
            bar_fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font_color='#dce3f0', height=320,
                title_font_family='Syne', title_font_size=14,
                coloraxis_showscale=False,
                xaxis=dict(gridcolor='rgba(255,255,255,.04)', tickfont_color='#9aa3b5'),
                yaxis=dict(gridcolor='rgba(255,255,255,.04)', tickfont_color='#9aa3b5'),
                margin=dict(t=50, b=20, l=20, r=20), bargap=0.35
            )
            st.plotly_chart(bar_fig, use_container_width=True)

        # ── PDF DOWNLOAD BUTTON ──
        st.write("")
        with st.spinner("Generating PDF report..."):
            pdf_bytes = generate_pdf_report(
                username     = st.session_state.username,
                hours        = hours,
                attendance   = attendance,
                previous     = previous,
                sleep        = sleep,
                motivation   = motivation,
                teacher      = teacher,
                school       = school,
                internet     = internet,
                final_score  = final_score,
                grade        = grade,
                remark       = remark
            )

        filename = f"EduPredict_{st.session_state.username}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        st.download_button(
            label      = "📄  Download PDF Report",
            data       = pdf_bytes,
            file_name  = filename,
            mime       = "application/pdf",
            use_container_width=True
        )
