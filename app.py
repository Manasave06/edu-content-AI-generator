import streamlit as st
import sys
import os
import time
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from processor import process_file, chunk_text
from generator import (
    generate_quiz, generate_flashcards, chat_with_doc,
    generate_true_false, generate_fill_blanks, generate_study_content
)
from database import (
    init_db, save_document, save_quiz, save_flashcards,
    save_quiz_result, get_quiz_results, get_study_streak,
    get_total_xp, get_streak_count, save_flashcard_confidence,
    get_flashcard_confidence_stats
)

try:
    from speech import text_to_speech, get_audio_html, LANGUAGE_CODES
    TTS_AVAILABLE = True
except Exception as e:
    TTS_AVAILABLE = False
    LANGUAGE_CODES = {"English": "en"}

try:
    from youtube_api import (
        search_youtube_videos, get_educational_links,
        get_subject_category, get_performance_insights,
        get_study_schedule, search_wikipedia,
        search_books, get_adaptive_difficulty
    )
    YOUTUBE_AVAILABLE = True
except:
    YOUTUBE_AVAILABLE = False
    def search_youtube_videos(q, max_results=6): return []
    def get_educational_links(t): return []
    def get_subject_category(t): return "📚 General Studies"
    def get_performance_insights(r): return {}
    def get_study_schedule(t, h=2): return []
    def search_wikipedia(t): return {}
    def search_books(t, max_results=4): return []
    def get_adaptive_difficulty(r): return "Medium"

try:
    from export_utils import (
        export_quiz_results_txt, export_flashcards_txt,
        export_study_notes_txt, export_quiz_questions_txt,
        validate_document_text
    )
    EXPORT_AVAILABLE = True
except:
    EXPORT_AVAILABLE = False
    def validate_document_text(t): return [], []

init_db()

st.set_page_config(
    page_title="EduContent AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Fira+Code:wght@500&display=swap');
html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
.stApp {
    background: linear-gradient(160deg, #f0f4ff 0%, #fdf0ff 50%, #fff0f7 100%);
    color: #1a1a2e;
}
#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%) !important;
    border-right: none !important;
}
section[data-testid="stSidebar"] * { color: white !important; }
section[data-testid="stSidebar"] .stRadio label {
    background: rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    padding: 8px 14px !important;
    margin: 3px 0 !important;
    display: block !important;
}
.hero-title {
    font-size: 3em; font-weight: 900;
    background: linear-gradient(135deg, #667eea, #f093fb, #f5576c);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; line-height: 1.2; margin-bottom: 6px;
}
.hero-sub { color: #6b7280; font-size: 1.1em; font-weight: 600; margin-bottom: 24px; }
.feature-card {
    background: white; border-radius: 20px; padding: 24px; margin: 8px 0;
    box-shadow: 0 4px 20px rgba(102,126,234,0.12);
    position: relative; overflow: hidden; text-align: center;
    cursor: pointer; transition: all 0.3s ease;
    border: 3px solid transparent;
}
.feature-card:hover {
    transform: translateY(-4px);
    border-color: #667eea;
    box-shadow: 0 8px 30px rgba(102,126,234,0.25);
}
.feature-card::after {
    content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 5px;
    background: var(--card-color, linear-gradient(90deg,#667eea,#764ba2));
}
.feature-icon { font-size: 2.5em; margin-bottom: 10px; }
.feature-title { font-size: 1.1em; font-weight: 800; color: #1a1a2e; }
.feature-desc { font-size: 0.88em; color: #6b7280; margin-top: 4px; }
.xp-card {
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 20px; padding: 20px; text-align: center; color: white;
}
.xp-number { font-size: 2.5em; font-weight: 900; }
.xp-label { font-size: 0.85em; opacity: 0.85; margin-top: 4px; }
.streak-card {
    background: linear-gradient(135deg, #f5576c, #f093fb);
    border-radius: 20px; padding: 20px; text-align: center; color: white;
}
.content-card {
    background: white; border-radius: 16px; padding: 20px 24px; margin: 10px 0;
    box-shadow: 0 3px 15px rgba(102,126,234,0.1);
    border-left: 5px solid var(--accent, #667eea);
}
.quiz-card {
    background: white; border-radius: 16px; padding: 22px 26px; margin: 14px 0;
    box-shadow: 0 2px 15px rgba(102,126,234,0.1); border-left: 5px solid #667eea;
}
.quiz-number {
    font-family: 'Fira Code', monospace; font-size: 0.72em; color: #667eea;
    font-weight: 600; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px;
}
.quiz-question { font-size: 1.1em; font-weight: 700; color: #1a1a2e; line-height: 1.5; }
.badge-correct {
    background: linear-gradient(135deg,#d4edda,#c3e6cb); border: 2px solid #28a745;
    border-radius: 10px; padding: 10px 18px; color: #155724;
    font-weight: 800; display: inline-block; margin: 6px 0;
}
.badge-wrong {
    background: linear-gradient(135deg,#f8d7da,#f5c6cb); border: 2px solid #dc3545;
    border-radius: 10px; padding: 10px 18px; color: #721c24;
    font-weight: 800; display: inline-block; margin: 6px 0;
}
.explanation-box {
    background: linear-gradient(135deg,#e8f4fd,#d1ecf1); border-left: 4px solid #17a2b8;
    border-radius: 0 10px 10px 0; padding: 12px 16px; color: #0c5460;
    font-size: 0.92em; margin-top: 10px; font-weight: 600;
}
.hint-box {
    background: linear-gradient(135deg,#fff3cd,#ffeeba); border-left: 4px solid #ffc107;
    border-radius: 0 10px 10px 0; padding: 10px 14px; color: #856404;
    font-size: 0.88em; margin-top: 6px; font-weight: 600;
}
.score-display {
    background: linear-gradient(135deg,#667eea,#764ba2); border-radius: 24px; padding: 40px;
    text-align: center; box-shadow: 0 10px 40px rgba(102,126,234,0.35);
}
.score-number { font-size: 5em; font-weight: 900; color: white; line-height: 1; }
.score-label { color: rgba(255,255,255,0.8); font-size: 1.1em; font-weight: 600; margin-top: 10px; }
.fc-front {
    background: linear-gradient(135deg,#667eea,#764ba2); border-radius: 24px; padding: 45px 35px;
    text-align: center; font-size: 1.4em; font-weight: 800; color: white; min-height: 180px;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 15px 50px rgba(102,126,234,0.3);
}
.fc-back {
    background: linear-gradient(135deg,#11998e,#38ef7d); border-radius: 24px; padding: 45px 35px;
    text-align: center; font-size: 1.1em; font-weight: 700; color: white; min-height: 180px;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 15px 50px rgba(17,153,142,0.25); margin-top: 16px;
}
.conf-know {
    background: linear-gradient(135deg,#28a745,#20c997); border-radius: 14px; padding: 14px;
    text-align: center; color: white; font-weight: 800;
}
.conf-almost {
    background: linear-gradient(135deg,#ffc107,#fd7e14); border-radius: 14px; padding: 14px;
    text-align: center; color: white; font-weight: 800;
}
.conf-noidea {
    background: linear-gradient(135deg,#dc3545,#c82333); border-radius: 14px; padding: 14px;
    text-align: center; color: white; font-weight: 800;
}
.chat-user {
    background: linear-gradient(135deg,#667eea,#764ba2); border-radius: 20px 20px 6px 20px;
    padding: 16px 20px; margin: 12px 0; color: white;
}
.chat-ai {
    background: white; border: 2px solid #e8e8ff; border-radius: 20px 20px 20px 6px;
    padding: 16px 20px; margin: 12px 0; color: #1a1a2e;
}
.chat-label {
    font-size: 0.72em; font-weight: 800; letter-spacing: 2px;
    text-transform: uppercase; margin-bottom: 6px; opacity: 0.75;
}
.stat-card {
    background: white; border-radius: 20px; padding: 28px; text-align: center;
    box-shadow: 0 4px 20px rgba(102,126,234,0.1);
}
.stat-number {
    font-size: 3em; font-weight: 900;
    background: linear-gradient(135deg,#667eea,#f093fb);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.stat-label {
    color: #6b7280; font-size: 0.9em; font-weight: 700;
    margin-top: 6px; text-transform: uppercase; letter-spacing: 1px;
}
.doc-loaded {
    background: rgba(255,255,255,0.2); border: 2px solid rgba(255,255,255,0.4);
    border-radius: 14px; padding: 14px; margin: 8px 0;
}
.doc-not-loaded {
    background: rgba(0,0,0,0.15); border: 2px solid rgba(255,255,255,0.2);
    border-radius: 14px; padding: 14px; margin: 8px 0;
}
.badge-easy {
    background: linear-gradient(135deg,#d4edda,#c3e6cb); border: 2px solid #28a745;
    border-radius: 20px; padding: 4px 14px; color: #155724;
    font-weight: 800; font-size: 0.85em; display: inline-block;
}
.badge-medium {
    background: linear-gradient(135deg,#fff3cd,#ffeeba); border: 2px solid #ffc107;
    border-radius: 20px; padding: 4px 14px; color: #856404;
    font-weight: 800; font-size: 0.85em; display: inline-block;
}
.badge-hard {
    background: linear-gradient(135deg,#f8d7da,#f5c6cb); border: 2px solid #dc3545;
    border-radius: 20px; padding: 4px 14px; color: #721c24;
    font-weight: 800; font-size: 0.85em; display: inline-block;
}
.timer-box {
    background: linear-gradient(135deg,#667eea,#764ba2); border-radius: 16px;
    padding: 16px 24px; text-align: center; color: white; margin: 12px 0;
    font-size: 1.5em; font-weight: 900; font-family: 'Fira Code', monospace;
}
.timer-warning {
    background: linear-gradient(135deg,#f5576c,#f093fb); border-radius: 16px;
    padding: 16px 24px; text-align: center; color: white; margin: 12px 0;
    font-size: 1.5em; font-weight: 900; font-family: 'Fira Code', monospace;
}
.audio-box {
    background: linear-gradient(135deg,#667eea,#764ba2); border-radius: 14px;
    padding: 14px 18px; color: white; margin: 8px 0;
}
.nav-brand { font-size: 1.5em; font-weight: 900; color: white; }
.nav-sub { font-size: 0.85em; color: rgba(255,255,255,0.7); font-weight: 600; }
.stProgress > div > div {
    background: linear-gradient(90deg,#667eea,#f093fb) !important;
    border-radius: 10px !important;
}
.stButton > button {
    border-radius: 12px !important; font-family: 'Nunito', sans-serif !important;
    font-weight: 800 !important; font-size: 1em !important;
    transition: all 0.2s ease !important; border: none !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg,#667eea,#764ba2) !important;
    color: white !important; box-shadow: 0 4px 15px rgba(102,126,234,0.4) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(102,126,234,0.5) !important;
}
[data-testid="metric-container"] {
    background: white !important; border-radius: 16px !important;
    padding: 20px !important; box-shadow: 0 4px 15px rgba(102,126,234,0.1) !important;
}
hr { border-color: rgba(102,126,234,0.15) !important; }
/* Hide default streamlit upload label */
.stFileUploader label { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────
defaults = {
    "doc_text": "", "doc_name": "", "doc_id": None,
    "quiz_questions": [], "quiz_answers": [],
    "quiz_submitted": False, "quiz_score": 0, "quiz_id": None,
    "quiz_type": "MCQ", "quiz_difficulty": "Medium",
    "tf_questions": [], "tf_answers": [], "tf_submitted": False, "tf_score": 0,
    "fb_questions": [], "fb_answers": [], "fb_submitted": False, "fb_score": 0,
    "flashcards": [], "fc_index": 0, "fc_flipped": False, "fc_confidence": [],
    "chat_history": [], "selected_lang": "English",
    "timer_active": False, "timer_start": None,
    "timer_duration": 600, "timer_expired": False,
    "study_content": None, "current_page": "🏠 Home",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Page Navigation Helper ────────────────────────────────────────────────
def go_to(page_name):
    st.session_state["current_page"] = page_name
    st.rerun()

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="nav-brand">🎓 EduContent AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-sub">Powered by Groq · LLaMA3</div>', unsafe_allow_html=True)
    st.divider()

    if TTS_AVAILABLE:
        st.markdown("#### 🌍 Language")
        lang_name = st.selectbox("Language", list(LANGUAGE_CODES.keys()),
                                 index=0, label_visibility="collapsed")
        st.session_state["selected_lang"] = lang_name
        st.divider()

    total_xp = get_total_xp()
    streak = get_streak_count()
    level = total_xp // 100 + 1
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.15);border-radius:14px;padding:12px;
                margin-bottom:8px;text-align:center">
        <div style="font-size:1.4em;font-weight:900">⚡ {total_xp} XP</div>
        <div style="font-size:0.8em;opacity:0.85">Level {level} · 🔥 {streak} day streak</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    pages = [
        "🏠 Home", "📤 Upload Document",
        "📝 Generate Quiz", "🃏 Flashcards",
        "📚 Study Content", "🎥 Resources",
        "💬 Chat with Doc", "📊 Progress"
    ]

    # Sync sidebar with session state
    cur_page = st.session_state.get("current_page", "🏠 Home")
    if cur_page not in pages:
        cur_page = "🏠 Home"
    default_idx = pages.index(cur_page)

    page = st.radio("Navigation", pages, index=default_idx,
                    label_visibility="collapsed")

    # Update session when sidebar clicked
    if page != st.session_state["current_page"]:
        st.session_state["current_page"] = page
        st.rerun()

    st.divider()
    if st.session_state["doc_name"]:
        st.markdown(f"""
        <div class="doc-loaded">
            <div style="font-size:0.7em;font-weight:800;letter-spacing:2px;
                        text-transform:uppercase;margin-bottom:4px">✅ Loaded</div>
            <div style="font-weight:700;font-size:0.95em">{st.session_state["doc_name"]}</div>
            <div style="font-size:0.8em;opacity:0.8">{len(st.session_state["doc_text"]):,} chars</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="doc-not-loaded">
            <div style="font-size:0.7em;font-weight:800;letter-spacing:2px;
                        text-transform:uppercase;margin-bottom:4px">⚠️ No Document</div>
            <div style="font-size:0.85em;opacity:0.8">Upload a document first</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    if st.button("🏠 Go to Home", use_container_width=True, type="primary"):
        go_to("🏠 Home")
    if st.button("🗑️ Clear Session", use_container_width=True):
        for k, v in defaults.items():
            st.session_state[k] = v
        st.rerun()

# Use session state for page
page = st.session_state.get("current_page", "🏠 Home")

# ── Home Button Helper ────────────────────────────────────────────────────
def home_button():
    if st.button("🏠 Home", key=f"hb_{page}_{id(st.session_state)}"):
        go_to("🏠 Home")

# ═══════════════════════════════════════════════════════════════════════════
# HOME
# ═══════════════════════════════════════════════════════════════════════════
if page == "🏠 Home":
    st.markdown('<div class="hero-title">🎓 EduContent AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Upload any document → AI generates quizzes, flashcards & more ✨</div>',
                unsafe_allow_html=True)

    total_xp = get_total_xp()
    streak = get_streak_count()
    results = get_quiz_results()
    level = total_xp // 100 + 1
    avg = sum(r[1]/r[2]*100 for r in results)/len(results) if results else 0

    # Stats row
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f'<div class="xp-card"><div class="xp-number">⚡ {total_xp}</div><div class="xp-label">XP · Level {level}</div></div>', unsafe_allow_html=True)
    with s2:
        st.markdown(f'<div class="streak-card"><div class="xp-number">🔥 {streak}</div><div class="xp-label">Day Streak</div></div>', unsafe_allow_html=True)
    with s3:
        st.markdown(f"""<div style="background:linear-gradient(135deg,#4facfe,#00f2fe);
            border-radius:20px;padding:20px;text-align:center;color:white">
            <div class="xp-number">📝 {len(results)}</div>
            <div class="xp-label">Quizzes Done</div></div>""", unsafe_allow_html=True)
    with s4:
        st.markdown(f"""<div style="background:linear-gradient(135deg,#43e97b,#38f9d7);
            border-radius:20px;padding:20px;text-align:center;color:white">
            <div class="xp-number">🎯 {avg:.0f}%</div>
            <div class="xp-label">Avg Score</div></div>""", unsafe_allow_html=True)

    st.write("")
    st.progress((total_xp % 100) / 100)
    st.caption(f"⚡ {total_xp % 100}/100 XP to Level {level+1}")

    # Adaptive suggestion
    if results:
        try:
            adaptive_diff = get_adaptive_difficulty(results)
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#667eea,#764ba2);
                        border-radius:14px;padding:12px 20px;color:white;font-weight:700;margin:8px 0">
                🤖 Recommended Difficulty: <b>{adaptive_diff}</b> based on your performance
            </div>""", unsafe_allow_html=True)
        except:
            pass

    st.divider()
    st.markdown("### 🎯 What would you like to do?")

    # Feature cards — clicking Open button navigates
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    cards_data = [
        ("📤", "Upload Document", "Upload PDF, TXT or DOCX",
         "linear-gradient(90deg,#667eea,#764ba2)", "📤 Upload Document"),
        ("📝", "Generate Quiz", "MCQ, True/False, Fill Blanks",
         "linear-gradient(90deg,#f093fb,#f5576c)", "📝 Generate Quiz"),
        ("🃏", "Flashcards", "Flip cards with XP rewards",
         "linear-gradient(90deg,#4facfe,#00f2fe)", "🃏 Flashcards"),
        ("📚", "Study Content", "AI summary and mind map",
         "linear-gradient(90deg,#43e97b,#38f9d7)", "📚 Study Content"),
        ("🎥", "Resources", "YouTube, Wikipedia, Free Books",
         "linear-gradient(90deg,#ff512f,#dd2476)", "🎥 Resources"),
        ("💬", "Chat with Doc", "Ask questions about document",
         "linear-gradient(90deg,#fa709a,#fee140)", "💬 Chat with Doc"),
    ]

    for col, (icon, title, desc, color, target) in zip(
        [col1, col2, col3, col4, col5, col6], cards_data
    ):
        with col:
            st.markdown(f"""
            <div class="feature-card" style="--card-color:{color}">
                <div class="feature-icon">{icon}</div>
                <div class="feature-title">{title}</div>
                <div class="feature-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Open", key=f"home_nav_{title}",
                        use_container_width=True, type="primary"):
                go_to(target)

    st.divider()

    # Recent activity or welcome
    if results:
        st.markdown("### 📊 Recent Activity")
        for r in results[:3]:
            pct = r[1]/r[2]*100
            color = "#28a745" if pct >= 70 else "#ffc107" if pct >= 50 else "#dc3545"
            emoji = "🏆" if pct >= 80 else "👍" if pct >= 60 else "📚"
            qtype = r[4] if len(r) > 4 else "MCQ"
            diff = r[5] if len(r) > 5 else "Medium"
            st.markdown(f"""
            <div style='background:white;border-radius:14px;padding:14px 18px;margin:6px 0;
                        box-shadow:0 3px 15px rgba(102,126,234,0.1);border-left:5px solid {color}'>
                <div style='display:flex;justify-content:space-between;align-items:center'>
                    <div>
                        <span>{emoji}</span>
                        <b style='margin-left:6px'>{r[3][:25]}</b>
                        <span style='background:#f0f4ff;border-radius:8px;padding:2px 8px;
                                    font-size:0.75em;margin-left:6px;color:#667eea'>{qtype}</span>
                        <span style='background:#fff0f7;border-radius:8px;padding:2px 8px;
                                    font-size:0.75em;margin-left:4px;color:#f5576c'>{diff}</span>
                    </div>
                    <b style='color:{color}'>{pct:.0f}%</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
        if st.button("📊 View Full Progress", use_container_width=True):
            go_to("📊 Progress")
    else:
        st.markdown("""
        <div style="background:white;border-radius:16px;padding:30px;
                    text-align:center;box-shadow:0 3px 15px rgba(102,126,234,0.1)">
            <div style="font-size:3em">🎓</div>
            <div style="font-weight:800;font-size:1.2em;margin:10px 0">Welcome to EduContent AI!</div>
            <div style="color:#6b7280">Start by uploading a document to generate quizzes and flashcards</div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("📤 Upload Your First Document", type="primary", use_container_width=True):
            go_to("📤 Upload Document")

# ═══════════════════════════════════════════════════════════════════════════
# UPLOAD
# ═══════════════════════════════════════════════════════════════════════════
elif page == "📤 Upload Document":
    home_button()
    st.markdown('<div class="hero-title">📤 Upload Document</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Supports PDF, TXT and DOCX — all pages extracted</div>',
                unsafe_allow_html=True)
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class="feature-card" style="--card-color:linear-gradient(90deg,#667eea,#764ba2)">
            <div class="feature-icon">📄</div><div class="feature-title">PDF Files</div>
            <div class="feature-desc">Textbooks, papers, articles — ALL pages</div></div>""",
            unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="feature-card" style="--card-color:linear-gradient(90deg,#f093fb,#f5576c)">
            <div class="feature-icon">📝</div><div class="feature-title">TXT Files</div>
            <div class="feature-desc">Notes, transcripts, content</div></div>""",
            unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="feature-card" style="--card-color:linear-gradient(90deg,#43e97b,#38f9d7)">
            <div class="feature-icon">📘</div><div class="feature-title">DOCX Files</div>
            <div class="feature-desc">Word documents including tables</div></div>""",
            unsafe_allow_html=True)

    st.divider()
    uploaded = st.file_uploader(
        "Upload", type=["pdf","txt","docx"],
        label_visibility="collapsed"
    )

    if uploaded:
        with st.spinner("⚙️ Processing — extracting ALL pages..."):
            try:
                text = process_file(uploaded)

                # Validate
                if EXPORT_AVAILABLE:
                    errors, warnings = validate_document_text(text)
                    if errors:
                        for err in errors:
                            st.error(err)
                        st.stop()
                    for warn in warnings:
                        st.warning(warn)

                chunks = chunk_text(text)
                st.session_state["doc_text"] = text
                st.session_state["doc_name"] = uploaded.name
                st.session_state["study_content"] = None
                st.session_state["flashcards"] = []
                doc_id = save_document(uploaded.name, text)
                st.session_state["doc_id"] = doc_id

                col1, col2, col3 = st.columns(3)
                col1.metric("📝 Characters", f"{len(text):,}")
                col2.metric("💬 Words", f"{len(text.split()):,}")
                col3.metric("🧩 Chunks", len(chunks))

                try:
                    subject = get_subject_category(text)
                    st.info(f"📂 Detected Subject: **{subject}**")
                except:
                    pass

                with st.expander("👀 Preview (first 1000 chars)"):
                    st.code(text[:1000], language=None)

                st.success(f"✅ '{uploaded.name}' fully loaded — {len(text):,} characters from all pages!")

                st.markdown("### What would you like to do?")
                c1, c2, c3, c4, c5 = st.columns(5)
                with c1:
                    if st.button("📚 Study Notes", use_container_width=True, type="primary"):
                        go_to("📚 Study Content")
                with c2:
                    if st.button("📝 Quiz", use_container_width=True, type="primary"):
                        go_to("📝 Generate Quiz")
                with c3:
                    if st.button("🃏 Flashcards", use_container_width=True, type="primary"):
                        go_to("🃏 Flashcards")
                with c4:
                    if st.button("🎥 Resources", use_container_width=True, type="primary"):
                        go_to("🎥 Resources")
                with c5:
                    if st.button("💬 Chat", use_container_width=True, type="primary"):
                        go_to("💬 Chat with Doc")

            except ValueError as e:
                st.error(f"❌ File error: {e}")
                st.info("💡 Make sure the file is not corrupted and contains readable text")
            except Exception as e:
                st.error(f"❌ Unexpected error: {e}")
                st.info("💡 Try a different file format or check if the file is password protected")

# ═══════════════════════════════════════════════════════════════════════════
# STUDY CONTENT
# ═══════════════════════════════════════════════════════════════════════════
elif page == "📚 Study Content":
    home_button()
    st.markdown('<div class="hero-title">📚 Study Content</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">AI summary, key points, mind map, exam tips + audio</div>',
                unsafe_allow_html=True)
    st.divider()

    if not st.session_state["doc_text"]:
        st.warning("⚠️ Please upload a document first!")
        if st.button("📤 Go to Upload", type="primary"):
            go_to("📤 Upload Document")
        st.stop()

    if st.button("⚡ Generate Study Content", type="primary", use_container_width=True):
        with st.spinner("🤖 AI analyzing your document..."):
            try:
                content = generate_study_content(st.session_state["doc_text"])
                st.session_state["study_content"] = content
                st.success("✅ Study content ready!")
            except Exception as e:
                st.error(f"❌ Error generating content: {e}")
                st.info("💡 Try again or check your internet connection")

    if st.session_state["study_content"]:
        content = st.session_state["study_content"]
        st.divider()

        if "one_liner" in content:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#667eea,#764ba2);
                        border-radius:16px;padding:20px 24px;color:white;
                        font-size:1.2em;font-weight:700;text-align:center;margin-bottom:16px">
                💡 {content["one_liner"]}
            </div>""", unsafe_allow_html=True)

        # Audio Summary
        if TTS_AVAILABLE and content.get("summary"):
            st.markdown("### 🔊 Audio Lesson")
            st.markdown('<div class="audio-box">🎧 Listen to AI Summary</div>', unsafe_allow_html=True)
            try:
                lang_code = LANGUAGE_CODES.get(st.session_state["selected_lang"], "en")
                audio = text_to_speech(content["summary"][:500], lang_code)
                if audio:
                    st.markdown(get_audio_html(audio, autoplay=False), unsafe_allow_html=True)
                else:
                    st.warning("⚠️ Audio not available. gTTS may be unavailable on this server.")
            except Exception as e:
                st.warning(f"⚠️ Audio error: {e}")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🔊 Listen to Key Points"):
                    if content.get("key_points"):
                        try:
                            kp_text = "Key points: " + ". ".join(content["key_points"][:5])
                            audio = text_to_speech(kp_text[:500], lang_code)
                            if audio:
                                st.markdown(get_audio_html(audio, True), unsafe_allow_html=True)
                        except:
                            st.warning("Audio unavailable")
            with col_b:
                if st.button("🔊 Listen to Exam Tips"):
                    if content.get("exam_tips"):
                        try:
                            tips_text = "Exam tips: " + ". ".join(content["exam_tips"][:5])
                            audio = text_to_speech(tips_text[:500], lang_code)
                            if audio:
                                st.markdown(get_audio_html(audio, True), unsafe_allow_html=True)
                        except:
                            st.warning("Audio unavailable")

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📖 Summary")
            st.markdown(f'<div class="content-card" style="--accent:#667eea">{content.get("summary","")}</div>',
                       unsafe_allow_html=True)
            st.markdown("### 🎯 Key Points")
            for i, point in enumerate(content.get("key_points",[]), 1):
                st.markdown(f"""
                <div style="background:white;border-radius:12px;padding:12px 16px;margin:6px 0;
                            box-shadow:0 2px 10px rgba(102,126,234,0.1);border-left:4px solid #667eea">
                    <b style="color:#667eea">{i}.</b> {point}
                </div>""", unsafe_allow_html=True)

        with col2:
            st.markdown("### 📝 Exam Tips")
            for tip in content.get("exam_tips",[]):
                st.markdown(f"""
                <div style="background:white;border-radius:12px;padding:12px 16px;margin:6px 0;
                            box-shadow:0 2px 10px rgba(102,126,234,0.1);border-left:4px solid #f093fb">
                    ✅ {tip}
                </div>""", unsafe_allow_html=True)
            st.markdown("### 📖 Key Terms")
            for term in content.get("difficult_terms",[]):
                st.markdown(f"""
                <div style="background:white;border-radius:12px;padding:12px 16px;margin:6px 0;
                            box-shadow:0 2px 10px rgba(102,126,234,0.1);border-left:4px solid #43e97b">
                    <b style="color:#11998e">{term.get("term","")}</b>: {term.get("definition","")}
                </div>""", unsafe_allow_html=True)

        st.markdown("### 🗺️ Mind Map")
        for main_topic, subtopics in content.get("mind_map",{}).items():
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#667eea,#764ba2);border-radius:14px;
                        padding:14px 20px;color:white;font-weight:800;font-size:1.1em;margin:8px 0">
                🧠 {main_topic}
            </div>""", unsafe_allow_html=True)
            cols = st.columns(min(len(subtopics), 3))
            for i, sub in enumerate(subtopics):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div style="background:white;border-radius:10px;padding:10px 14px;margin:4px 0;
                                box-shadow:0 2px 10px rgba(102,126,234,0.1);
                                border-left:3px solid #667eea;font-size:0.9em">→ {sub}</div>""",
                        unsafe_allow_html=True)

        # Export
        if EXPORT_AVAILABLE:
            st.divider()
            st.markdown("### 📥 Export")
            c1, c2 = st.columns(2)
            with c1:
                notes_txt = export_study_notes_txt(content, st.session_state.get("doc_name","doc"))
                st.download_button("📥 Download Study Notes",
                    data=notes_txt,
                    file_name=f"study_notes_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain", use_container_width=True)
            with c2:
                if st.session_state.get("flashcards"):
                    fc_txt = export_flashcards_txt(
                        st.session_state["flashcards"],
                        st.session_state.get("doc_name","doc"))
                    st.download_button("📥 Download Flashcards",
                        data=fc_txt,
                        file_name=f"flashcards_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                        mime="text/plain", use_container_width=True)

        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("📝 Take Quiz", use_container_width=True, type="primary"):
                go_to("📝 Generate Quiz")
        with c2:
            if st.button("🃏 Flashcards", use_container_width=True, type="primary"):
                go_to("🃏 Flashcards")
        with c3:
            if st.button("🎥 Resources", use_container_width=True, type="primary"):
                go_to("🎥 Resources")
        with c4:
            if st.button("💬 Chat", use_container_width=True, type="primary"):
                go_to("💬 Chat with Doc")

# ═══════════════════════════════════════════════════════════════════════════
# QUIZ
# ═══════════════════════════════════════════════════════════════════════════
elif page == "📝 Generate Quiz":
    home_button()
    st.markdown('<div class="hero-title">📝 Quiz Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Adaptive difficulty based on your performance</div>',
                unsafe_allow_html=True)
    st.divider()

    if not st.session_state["doc_text"]:
        st.warning("⚠️ Please upload a document first!")
        if st.button("📤 Go to Upload", type="primary"):
            go_to("📤 Upload Document")
        st.stop()

    results = get_quiz_results()
    try:
        adaptive_diff = get_adaptive_difficulty(results)
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#43e97b,#38f9d7);border-radius:14px;
                    padding:12px 20px;color:white;font-weight:700;margin-bottom:16px">
            🤖 AI Recommends: <b>{adaptive_diff}</b> difficulty based on your recent scores
        </div>""", unsafe_allow_html=True)
    except:
        adaptive_diff = "Medium"

    st.markdown("### 📋 Select Quiz Type")
    t1, t2, t3 = st.columns(3)
    for col, qtype, icon, desc in zip(
        [t1, t2, t3],
        ["MCQ", "True/False", "Fill Blanks"],
        ["🔘", "✅", "✏️"],
        ["Multiple Choice", "True or False", "Complete the sentence"]
    ):
        with col:
            selected = st.session_state["quiz_type"] == qtype
            st.markdown(f"""
            <div style="background:white;border-radius:16px;padding:20px;text-align:center;
                        box-shadow:0 3px 15px rgba(102,126,234,0.1);
                        border:3px solid {'#667eea' if selected else 'transparent'}">
                <div style="font-size:2em">{icon}</div>
                <div style="font-weight:800;margin-top:6px">{qtype}</div>
                <div style="color:#6b7280;font-size:0.85em">{desc}</div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"{'✅ Selected' if selected else 'Select'}",
                        key=f"sel_{qtype}", use_container_width=True,
                        type="primary" if selected else "secondary"):
                st.session_state["quiz_type"] = qtype
                st.rerun()

    st.divider()
    col1, col2, col3, col4 = st.columns([2,2,2,1])
    with col1:
        num_q = st.slider("Questions", 3, 15, 5)
    with col2:
        diff_options = ["Easy","Medium","Hard"]
        diff_idx = diff_options.index(adaptive_diff) if adaptive_diff in diff_options else 1
        difficulty = st.selectbox("🎯 Difficulty", diff_options, index=diff_idx)
        st.session_state["quiz_difficulty"] = difficulty
    with col3:
        timer_mins = st.selectbox("⏱️ Timer",
            ["No Timer","5 mins","10 mins","15 mins","20 mins","30 mins"])
    with col4:
        st.write("")
        st.write("")
        gen = st.button("⚡ Go!", type="primary", use_container_width=True)

    badge_cls = {"Easy":"badge-easy","Medium":"badge-medium","Hard":"badge-hard"}
    st.markdown(
        f'<span class="{badge_cls[difficulty]}">🎯 {difficulty}</span> &nbsp;'
        f'<span style="color:#6b7280;font-size:0.9em">Type: {st.session_state["quiz_type"]}</span>',
        unsafe_allow_html=True)

    if gen:
        with st.spinner(f"🤖 Generating {st.session_state['quiz_type']} ({difficulty})..."):
            try:
                qtype = st.session_state["quiz_type"]
                if qtype == "MCQ":
                    q = generate_quiz(st.session_state["doc_text"], num_q, difficulty)
                    st.session_state["quiz_questions"] = q
                    st.session_state["quiz_answers"] = [None]*len(q)
                    st.session_state["quiz_submitted"] = False
                    st.session_state["quiz_score"] = 0
                elif qtype == "True/False":
                    q = generate_true_false(st.session_state["doc_text"], num_q, difficulty)
                    st.session_state["tf_questions"] = q
                    st.session_state["tf_answers"] = [None]*len(q)
                    st.session_state["tf_submitted"] = False
                    st.session_state["tf_score"] = 0
                elif qtype == "Fill Blanks":
                    q = generate_fill_blanks(st.session_state["doc_text"], num_q, difficulty)
                    st.session_state["fb_questions"] = q
                    st.session_state["fb_answers"] = [""]*len(q)
                    st.session_state["fb_submitted"] = False
                    st.session_state["fb_score"] = 0

                quiz_id = save_quiz(st.session_state["doc_id"] or 1, [])
                st.session_state["quiz_id"] = quiz_id

                if timer_mins != "No Timer":
                    mins = int(timer_mins.split()[0])
                    st.session_state["timer_duration"] = mins * 60
                    st.session_state["timer_active"] = True
                    st.session_state["timer_start"] = time.time()
                    st.session_state["timer_expired"] = False
                else:
                    st.session_state["timer_active"] = False
                    st.session_state["timer_expired"] = False

                st.success(f"✅ {num_q} questions ready!")
            except Exception as e:
                st.error(f"❌ Quiz generation failed: {e}")
                st.info("💡 Check internet connection and try again")

    timer_ph = st.empty()
    if st.session_state["timer_active"] and not (
        st.session_state.get("quiz_submitted") or
        st.session_state.get("tf_submitted") or
        st.session_state.get("fb_submitted")
    ):
        elapsed = time.time() - st.session_state["timer_start"]
        remaining = st.session_state["timer_duration"] - elapsed
        if remaining <= 0:
            st.session_state["timer_expired"] = True
            st.session_state["timer_active"] = False
            st.session_state["quiz_submitted"] = True
            st.session_state["tf_submitted"] = True
            st.session_state["fb_submitted"] = True
            st.rerun()
        else:
            m, s = int(remaining//60), int(remaining%60)
            cls = "timer-warning" if remaining <= 60 else "timer-box"
            timer_ph.markdown(f'<div class="{cls}">⏱️ {m:02d}:{s:02d}</div>', unsafe_allow_html=True)
            time.sleep(1)
            st.rerun()

    if st.session_state.get("timer_expired"):
        st.error("⏰ Time's Up!")

    st.divider()

    def show_score(score, total, qtype, diff):
        pct = score/total*100
        try:
            save_quiz_result(
                st.session_state["quiz_id"] or 1, score, total, qtype, diff,
                st.session_state.get("doc_name", "")
            )
        except Exception as e:
            print(f"Save result error: {e}")
        xp_earned = score * 10
        st.markdown(f"""
        <div class="score-display">
            <div class="score-number">{pct:.0f}%</div>
            <div class="score-label">🎯 {score}/{total} correct · {diff} · +{xp_earned} XP!</div>
        </div>""", unsafe_allow_html=True)

        # Audio score
        if TTS_AVAILABLE:
            try:
                lang_code = LANGUAGE_CODES.get(st.session_state["selected_lang"], "en")
                score_text = f"Quiz done! You scored {pct:.0f} percent. {xp_earned} XP earned!"
                audio = text_to_speech(score_text, lang_code)
                if audio:
                    st.markdown(get_audio_html(audio, True), unsafe_allow_html=True)
            except:
                pass

        if pct >= 80:
            st.balloons()

        # Export quiz
        if EXPORT_AVAILABLE:
            questions_export = (
                st.session_state.get("quiz_questions") or
                st.session_state.get("tf_questions") or
                st.session_state.get("fb_questions") or []
            )
            if questions_export:
                try:
                    quiz_txt = export_quiz_questions_txt(
                        questions_export,
                        st.session_state.get("doc_name","doc"),
                        qtype, diff
                    )
                    st.download_button("📥 Download Quiz Questions",
                        data=quiz_txt,
                        file_name=f"quiz_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                        mime="text/plain", use_container_width=True, key="dl_quiz")
                except:
                    pass

        st.write("")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🏠 Back to Home", use_container_width=True,
                        type="primary", key="score_home"):
                go_to("🏠 Home")
        with c2:
            if st.button("📊 View Progress", use_container_width=True, key="score_prog"):
                go_to("📊 Progress")

    # MCQ
    if st.session_state["quiz_type"] == "MCQ" and st.session_state["quiz_questions"]:
        questions = st.session_state["quiz_questions"]
        diff = st.session_state["quiz_difficulty"]
        for i, q in enumerate(questions):
            submitted = st.session_state["quiz_submitted"]
            chosen = st.session_state["quiz_answers"][i]
            correct = q["answer"]
            st.markdown(f"""
            <div class="quiz-card">
                <div style="display:flex;justify-content:space-between">
                    <div class="quiz-number">Q{i+1} of {len(questions)}</div>
                    <span class="{badge_cls.get(diff,'badge-medium')}">{diff}</span>
                </div>
                <div class="quiz-question">{q["question"]}</div>
            </div>""", unsafe_allow_html=True)

            if TTS_AVAILABLE and st.button("🔊", key=f"tts_q{i}", help="Listen to question"):
                try:
                    lang_code = LANGUAGE_CODES.get(st.session_state["selected_lang"], "en")
                    audio = text_to_speech(q["question"], lang_code)
                    if audio:
                        st.markdown(get_audio_html(audio, True), unsafe_allow_html=True)
                except:
                    pass

            sel = st.radio(f"Q{i+1}", q["options"], index=None,
                          key=f"q{i}", label_visibility="collapsed")
            if sel:
                st.session_state["quiz_answers"][i] = sel
            if submitted:
                if chosen == correct:
                    st.markdown('<div class="badge-correct">✅ Correct!</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="badge-wrong">❌ {correct}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="explanation-box">💡 {q.get("explanation","")}</div>', unsafe_allow_html=True)
            st.write("")

        if not st.session_state["quiz_submitted"]:
            if st.button("✅ Submit MCQ", type="primary", use_container_width=True):
                score = sum(1 for i,q in enumerate(questions)
                           if st.session_state["quiz_answers"][i]==q["answer"])
                st.session_state["quiz_score"] = score
                st.session_state["quiz_submitted"] = True
                st.session_state["timer_active"] = False
                st.rerun()
        else:
            show_score(st.session_state["quiz_score"], len(questions), "MCQ", diff)
            if st.button("🔄 Retake", use_container_width=True):
                st.session_state["quiz_answers"] = [None]*len(questions)
                st.session_state["quiz_submitted"] = False
                st.rerun()

    # True/False
    elif st.session_state["quiz_type"] == "True/False" and st.session_state["tf_questions"]:
        questions = st.session_state["tf_questions"]
        diff = st.session_state["quiz_difficulty"]
        for i, q in enumerate(questions):
            submitted = st.session_state["tf_submitted"]
            chosen = st.session_state["tf_answers"][i]
            correct = q["answer"]
            st.markdown(f"""
            <div class="quiz-card" style="border-left-color:#11998e">
                <div style="display:flex;justify-content:space-between">
                    <div class="quiz-number">Statement {i+1}</div>
                    <span class="{badge_cls.get(diff,'badge-medium')}">{diff}</span>
                </div>
                <div class="quiz-question">{q["question"]}</div>
            </div>""", unsafe_allow_html=True)
            sel = st.radio(f"TF{i+1}", ["True","False"], index=None,
                          key=f"tf{i}", label_visibility="collapsed", horizontal=True)
            if sel:
                st.session_state["tf_answers"][i] = sel
            if submitted:
                if chosen == correct:
                    st.markdown('<div class="badge-correct">✅ Correct!</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="badge-wrong">❌ {correct}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="explanation-box">💡 {q.get("explanation","")}</div>', unsafe_allow_html=True)
            st.write("")

        if not st.session_state["tf_submitted"]:
            if st.button("✅ Submit T/F", type="primary", use_container_width=True):
                score = sum(1 for i,q in enumerate(questions)
                           if st.session_state["tf_answers"][i]==q["answer"])
                st.session_state["tf_score"] = score
                st.session_state["tf_submitted"] = True
                st.session_state["timer_active"] = False
                st.rerun()
        else:
            show_score(st.session_state["tf_score"], len(questions), "True/False", diff)
            if st.button("🔄 Retake", use_container_width=True):
                st.session_state["tf_answers"] = [None]*len(questions)
                st.session_state["tf_submitted"] = False
                st.rerun()

    # Fill Blanks
    elif st.session_state["quiz_type"] == "Fill Blanks" and st.session_state["fb_questions"]:
        questions = st.session_state["fb_questions"]
        diff = st.session_state["quiz_difficulty"]
        for i, q in enumerate(questions):
            submitted = st.session_state["fb_submitted"]
            correct = q["answer"]
            st.markdown(f"""
            <div class="quiz-card" style="border-left-color:#f093fb">
                <div style="display:flex;justify-content:space-between">
                    <div class="quiz-number">Q{i+1}</div>
                    <span class="{badge_cls.get(diff,'badge-medium')}">{diff}</span>
                </div>
                <div class="quiz-question">{q["question"]}</div>
            </div>""", unsafe_allow_html=True)
            if not submitted:
                st.markdown(f'<div class="hint-box">💡 Hint: {q.get("hint","")}</div>', unsafe_allow_html=True)
                ans = st.text_input(f"Answer {i+1}", key=f"fb{i}",
                                   placeholder="Type your answer...",
                                   label_visibility="collapsed")
                if ans:
                    st.session_state["fb_answers"][i] = ans
            else:
                user_ans = st.session_state["fb_answers"][i] or ""
                if user_ans.strip().lower() == correct.strip().lower():
                    st.markdown('<div class="badge-correct">✅ Correct!</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="badge-wrong">❌ {correct}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="explanation-box">💡 {q.get("explanation","")}</div>', unsafe_allow_html=True)
            st.write("")

        if not st.session_state["fb_submitted"]:
            if st.button("✅ Submit", type="primary", use_container_width=True):
                score = sum(
                    1 for i,q in enumerate(questions)
                    if (st.session_state["fb_answers"][i] or "").strip().lower() == q["answer"].strip().lower()
                )
                st.session_state["fb_score"] = score
                st.session_state["fb_submitted"] = True
                st.session_state["timer_active"] = False
                st.rerun()
        else:
            show_score(st.session_state["fb_score"], len(questions), "Fill Blanks", diff)
            if st.button("🔄 Retake", use_container_width=True):
                st.session_state["fb_answers"] = [""]*len(questions)
                st.session_state["fb_submitted"] = False
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# FLASHCARDS
# ═══════════════════════════════════════════════════════════════════════════
elif page == "🃏 Flashcards":
    home_button()
    st.markdown('<div class="hero-title">🃏 Smart Flashcards</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Rate confidence to earn XP and track weak areas</div>',
                unsafe_allow_html=True)
    st.divider()

    if not st.session_state["doc_text"]:
        st.warning("⚠️ Please upload a document first!")
        if st.button("📤 Go to Upload", type="primary"):
            go_to("📤 Upload Document")
        st.stop()

    col1, col2 = st.columns([3,1])
    with col1:
        num_cards = st.slider("Number of flashcards", 5, 20, 8)
    with col2:
        st.write("")
        gen = st.button("⚡ Generate", type="primary", use_container_width=True)

    if gen:
        with st.spinner("🤖 Creating flashcards..."):
            try:
                cards = generate_flashcards(st.session_state["doc_text"], num_cards)
                save_flashcards(st.session_state["doc_id"] or 1, cards)
                st.session_state["flashcards"] = cards
                st.session_state["fc_index"] = 0
                st.session_state["fc_flipped"] = False
                st.session_state["fc_confidence"] = [None]*len(cards)
                st.success(f"✅ {len(cards)} flashcards ready!")
            except Exception as e:
                st.error(f"❌ Flashcard generation failed: {e}")

    cards = st.session_state["flashcards"]
    if cards:
        st.divider()
        idx = st.session_state["fc_index"]
        card = cards[idx]
        confidence_list = st.session_state["fc_confidence"]
        rated = sum(1 for c in confidence_list if c is not None)

        st.markdown(f"**Card {idx+1} of {len(cards)}** · {rated}/{len(cards)} rated")
        st.progress((idx+1)/len(cards))

        _, col, _ = st.columns([1,3,1])
        with col:
            st.write("")
            st.markdown(f'<div class="fc-front">❓ {card["front"]}</div>', unsafe_allow_html=True)

            if TTS_AVAILABLE:
                try:
                    lang_code = LANGUAGE_CODES.get(st.session_state["selected_lang"], "en")
                    af = text_to_speech(card["front"], lang_code)
                    if af:
                        st.markdown(get_audio_html(af), unsafe_allow_html=True)
                except:
                    pass

            if st.session_state["fc_flipped"]:
                st.markdown(f'<div class="fc-back">✅ {card["back"]}</div>', unsafe_allow_html=True)
                if TTS_AVAILABLE:
                    try:
                        ab = text_to_speech(card["back"], lang_code)
                        if ab:
                            st.markdown(get_audio_html(ab), unsafe_allow_html=True)
                    except:
                        pass

                st.divider()
                st.markdown("**How well did you know this?**")
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("😎 Know it!\n+15 XP", use_container_width=True, key="know"):
                        st.session_state["fc_confidence"][idx] = "Know it"
                        save_flashcard_confidence(card["front"], "Know it")
                        if idx < len(cards)-1:
                            st.session_state["fc_index"] += 1
                            st.session_state["fc_flipped"] = False
                        st.rerun()
                with c2:
                    if st.button("🤔 Almost\n+8 XP", use_container_width=True, key="almost"):
                        st.session_state["fc_confidence"][idx] = "Almost"
                        save_flashcard_confidence(card["front"], "Almost")
                        if idx < len(cards)-1:
                            st.session_state["fc_index"] += 1
                            st.session_state["fc_flipped"] = False
                        st.rerun()
                with c3:
                    if st.button("😅 No idea\n+3 XP", use_container_width=True, key="noidea"):
                        st.session_state["fc_confidence"][idx] = "No idea"
                        save_flashcard_confidence(card["front"], "No idea")
                        if idx < len(cards)-1:
                            st.session_state["fc_index"] += 1
                            st.session_state["fc_flipped"] = False
                        st.rerun()
            else:
                st.write("")
                if st.button("👁️ Reveal Answer", type="primary", use_container_width=True):
                    st.session_state["fc_flipped"] = True
                    st.rerun()

            st.write("")
            b1, b2 = st.columns(2)
            with b1:
                if st.button("⬅️ Prev", use_container_width=True):
                    if idx > 0:
                        st.session_state["fc_index"] -= 1
                        st.session_state["fc_flipped"] = False
                        st.rerun()
            with b2:
                if st.button("Next ➡️", use_container_width=True):
                    if idx < len(cards)-1:
                        st.session_state["fc_index"] += 1
                        st.session_state["fc_flipped"] = False
                        st.rerun()

        if rated > 0:
            st.divider()
            stats = {}
            for c in confidence_list:
                if c:
                    stats[c] = stats.get(c, 0) + 1
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="conf-know">😎 Know it<br><b style="font-size:1.5em">{stats.get("Know it",0)}</b></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="conf-almost">🤔 Almost<br><b style="font-size:1.5em">{stats.get("Almost",0)}</b></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="conf-noidea">😅 No idea<br><b style="font-size:1.5em">{stats.get("No idea",0)}</b></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# RESOURCES
# ═══════════════════════════════════════════════════════════════════════════
elif page == "🎥 Resources":
    home_button()
    st.markdown('<div class="hero-title">🎥 Learning Resources</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">YouTube · Wikipedia · Free Books · Study Sites</div>',
                unsafe_allow_html=True)
    st.divider()

    try:
        if st.session_state["doc_text"]:
            subject = get_subject_category(st.session_state["doc_text"])
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#667eea,#764ba2);border-radius:14px;
                        padding:14px 20px;color:white;font-weight:700;font-size:1.1em;margin-bottom:16px">
                📂 Detected Subject: {subject}
            </div>""", unsafe_allow_html=True)
            default_topic = st.session_state["doc_name"].replace(".pdf","").replace(".txt","").replace(".docx","")
        else:
            default_topic = ""
    except:
        default_topic = ""

    topic = st.text_input("🔍 Search topic", value=default_topic,
        placeholder="e.g. Machine Learning, Photosynthesis...",
        label_visibility="collapsed")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        search_videos = st.button("🎥 YouTube", type="primary", use_container_width=True)
    with col2:
        search_wiki = st.button("📖 Wikipedia", use_container_width=True)
    with col3:
        search_books_btn = st.button("📚 Free Books", use_container_width=True)
    with col4:
        search_links = st.button("🌐 Study Sites", use_container_width=True)

    st.divider()

    if search_videos and topic:
        with st.spinner("🔍 Searching YouTube..."):
            try:
                videos = search_youtube_videos(topic, max_results=6)
            except:
                videos = []
        if videos:
            st.markdown("### 🎥 YouTube Videos")
            col1, col2 = st.columns(2)
            for i, video in enumerate(videos):
                with col1 if i % 2 == 0 else col2:
                    st.markdown(f"""
                    <div style="background:white;border-radius:16px;padding:16px;margin:8px 0;
                                box-shadow:0 3px 15px rgba(102,126,234,0.1);border-left:5px solid #ff0000">
                        <div style="font-weight:800;color:#1a1a2e;font-size:0.95em;margin-bottom:6px">
                            {video['title']}</div>
                        <div style="color:#6b7280;font-size:0.82em;margin-bottom:8px">
                            📺 {video['channel']} · ⏱️ {video['duration']}</div>
                        <a href="{video['url']}" target="_blank"
                           style="background:linear-gradient(135deg,#ff0000,#cc0000);color:white;
                                  padding:6px 14px;border-radius:8px;text-decoration:none;
                                  font-weight:700;font-size:0.85em">▶️ Watch</a>
                    </div>""", unsafe_allow_html=True)
        else:
            st.warning("No videos found. Try a different search term!")

    if search_wiki and topic:
        with st.spinner("🔍 Searching Wikipedia..."):
            try:
                wiki = search_wikipedia(topic)
            except:
                wiki = {}
        if wiki:
            st.markdown("### 📖 Wikipedia")
            st.markdown(f"""
            <div style="background:white;border-radius:16px;padding:20px;margin:10px 0;
                        box-shadow:0 3px 15px rgba(102,126,234,0.1);border-left:5px solid #636466">
                <div style="font-weight:800;font-size:1.2em;margin-bottom:8px">{wiki.get('title','')}</div>
                <div style="color:#4a4a4a;line-height:1.6;margin-bottom:12px">{wiki.get('summary','')}</div>
                <a href="{wiki.get('url','')}" target="_blank"
                   style="background:#636466;color:white;padding:8px 16px;border-radius:8px;
                          text-decoration:none;font-weight:700">🔗 Read Full Article</a>
            </div>""", unsafe_allow_html=True)
            if TTS_AVAILABLE and wiki.get("summary"):
                if st.button("🔊 Listen to Wikipedia Summary"):
                    try:
                        lang_code = LANGUAGE_CODES.get(st.session_state["selected_lang"], "en")
                        audio = text_to_speech(wiki["summary"][:500], lang_code)
                        if audio:
                            st.markdown(get_audio_html(audio, True), unsafe_allow_html=True)
                    except:
                        st.warning("Audio unavailable")
        else:
            st.warning("No Wikipedia article found!")

    if search_books_btn and topic:
        with st.spinner("🔍 Searching free books..."):
            try:
                books = search_books(topic, max_results=4)
            except:
                books = []
        if books:
            st.markdown("### 📚 Free Books — Open Library")
            col1, col2 = st.columns(2)
            for i, book in enumerate(books):
                with col1 if i % 2 == 0 else col2:
                    st.markdown(f"""
                    <div style="background:white;border-radius:16px;padding:16px;margin:8px 0;
                                box-shadow:0 3px 15px rgba(102,126,234,0.1);border-left:5px solid #CC4B00">
                        <div style="font-weight:800;font-size:0.95em;margin-bottom:4px">{book['title']}</div>
                        <div style="color:#6b7280;font-size:0.85em;margin-bottom:8px">
                            ✍️ {book['author']} · 📅 {book['year']}</div>
                        <a href="{book['url']}" target="_blank"
                           style="background:#CC4B00;color:white;padding:6px 14px;border-radius:8px;
                                  text-decoration:none;font-weight:700;font-size:0.85em">📖 Read Free</a>
                    </div>""", unsafe_allow_html=True)
        else:
            st.warning("No books found. Try a different topic!")

    if search_links and topic:
        try:
            links = get_educational_links(topic)
        except:
            links = []
        if links:
            st.markdown("### 🌐 Free Educational Websites")
            col1, col2, col3 = st.columns(3)
            for i, link in enumerate(links):
                with [col1, col2, col3][i % 3]:
                    st.markdown(f"""
                    <div style="background:white;border-radius:16px;padding:20px;margin:8px 0;
                                box-shadow:0 3px 15px rgba(102,126,234,0.1);
                                border-top:5px solid {link['color']};text-align:center">
                        <div style="font-weight:800;margin-bottom:6px">{link['name']}</div>
                        <div style="color:#6b7280;font-size:0.82em;margin-bottom:12px">{link['desc']}</div>
                        <a href="{link['url']}" target="_blank"
                           style="background:{link['color']};color:white;padding:8px 16px;
                                  border-radius:8px;text-decoration:none;font-weight:700">🔗 Visit</a>
                    </div>""", unsafe_allow_html=True)

    if not topic:
        st.markdown("""
        <div style="background:white;border-radius:16px;padding:30px;text-align:center;
                    box-shadow:0 3px 15px rgba(102,126,234,0.1)">
            <div style="font-size:3em">🔍</div>
            <div style="font-weight:800;font-size:1.2em;margin:10px 0">Search any topic!</div>
            <div style="color:#6b7280">YouTube · Wikipedia · Free Books · Study Sites</div>
        </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# CHAT
# ═══════════════════════════════════════════════════════════════════════════
elif page == "💬 Chat with Doc":
    home_button()
    st.markdown('<div class="hero-title">💬 Voice Q&A Chat</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Ask anything — AI answers from your document 🔊</div>',
                unsafe_allow_html=True)
    st.divider()

    if not st.session_state["doc_text"]:
        st.warning("⚠️ Please upload a document first!")
        if st.button("📤 Go to Upload", type="primary"):
            go_to("📤 Upload Document")
        st.stop()

    if not TTS_AVAILABLE:
        st.warning("⚠️ Audio not available on this server. Text answers will still work.")

    for h in st.session_state["chat_history"]:
        st.markdown(f'<div class="chat-user"><div class="chat-label">🧑 You</div>{h["user"]}</div>',
                   unsafe_allow_html=True)
        st.markdown(f'<div class="chat-ai"><div class="chat-label">🤖 AI</div>{h["assistant"]}</div>',
                   unsafe_allow_html=True)
        if TTS_AVAILABLE and h.get("audio"):
            st.markdown(get_audio_html(h["audio"]), unsafe_allow_html=True)

    question = st.chat_input("Ask anything about your document...")
    if question:
        with st.spinner("🤔 Thinking..."):
            try:
                answer = chat_with_doc(
                    st.session_state["doc_text"], question,
                    st.session_state["chat_history"]
                )
                audio_b64 = None
                if TTS_AVAILABLE:
                    try:
                        lang_code = LANGUAGE_CODES.get(st.session_state["selected_lang"], "en")
                        audio_b64 = text_to_speech(answer[:500], lang_code)
                    except:
                        pass
                st.session_state["chat_history"].append({
                    "user": question,
                    "assistant": answer,
                    "audio": audio_b64
                })
                st.rerun()
            except Exception as e:
                st.error(f"❌ Chat error: {e}")
                st.info("💡 Check your internet connection and try again")

    if st.session_state["chat_history"]:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state["chat_history"] = []
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# PROGRESS
# ═══════════════════════════════════════════════════════════════════════════
elif page == "📊 Progress":
    home_button()
    st.markdown('<div class="hero-title">📊 Your Progress</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Analytics, insights and personalized recommendations</div>',
                unsafe_allow_html=True)
    st.divider()

    total_xp = get_total_xp()
    streak = get_streak_count()
    results = get_quiz_results()
    level = total_xp // 100 + 1
    conf_stats = get_flashcard_confidence_stats()
    avg = sum(r[1]/r[2]*100 for r in results)/len(results) if results else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="xp-card"><div class="xp-number">⚡ {total_xp}</div><div class="xp-label">XP · Level {level}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="streak-card"><div class="xp-number">🔥 {streak}</div><div class="xp-label">Day Streak</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{avg:.0f}%</div><div class="stat-label">Avg Score</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len(results)}</div><div class="stat-label">Quizzes</div></div>', unsafe_allow_html=True)

    st.divider()
    st.markdown(f"### ⚡ Level {level} Progress")
    st.progress((total_xp % 100) / 100)
    st.caption(f"{total_xp % 100}/100 XP to Level {level+1}")

    # Performance insights
    try:
        if results:
            insights = get_performance_insights(results)
            if insights:
                st.divider()
                st.markdown("### 💡 Learning Analytics")
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown(f"""<div style="background:white;border-radius:14px;padding:16px;
                        text-align:center;box-shadow:0 3px 15px rgba(102,126,234,0.1)">
                        <div style="font-size:0.85em;color:#6b7280">📈 Trend</div>
                        <div style="font-weight:800">{insights.get("trend","")}</div></div>""",
                        unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""<div style="background:white;border-radius:14px;padding:16px;
                        text-align:center;box-shadow:0 3px 15px rgba(102,126,234,0.1)">
                        <div style="font-size:0.85em;color:#6b7280">🏆 Best</div>
                        <div style="font-weight:800;color:#28a745">{insights.get("best_score",0):.0f}%</div></div>""",
                        unsafe_allow_html=True)
                with c3:
                    st.markdown(f"""<div style="background:white;border-radius:14px;padding:16px;
                        text-align:center;box-shadow:0 3px 15px rgba(102,126,234,0.1)">
                        <div style="font-size:0.85em;color:#6b7280">📊 Average</div>
                        <div style="font-weight:800;color:#667eea">{insights.get("avg_score",0):.0f}%</div></div>""",
                        unsafe_allow_html=True)
                with c4:
                    adaptive = insights.get("adaptive_difficulty","Medium")
                    st.markdown(f"""<div style="background:linear-gradient(135deg,#667eea,#764ba2);
                        border-radius:14px;padding:16px;text-align:center;color:white">
                        <div style="font-size:0.85em;opacity:0.85">🤖 Next Level</div>
                        <div style="font-weight:800">{adaptive}</div></div>""",
                        unsafe_allow_html=True)

                st.markdown("### 📋 Recommendations")
                for rec in insights.get("recommendations",[]):
                    st.markdown(f"""<div style="background:white;border-radius:12px;padding:12px 16px;
                        margin:6px 0;box-shadow:0 2px 10px rgba(102,126,234,0.1);
                        border-left:4px solid #667eea">{rec}</div>""", unsafe_allow_html=True)

                if TTS_AVAILABLE and insights.get("recommendations"):
                    if st.button("🔊 Listen to Recommendations"):
                        try:
                            lang_code = LANGUAGE_CODES.get(st.session_state["selected_lang"], "en")
                            rec_text = "Your recommendations: " + ". ".join(insights["recommendations"])
                            audio = text_to_speech(rec_text[:500], lang_code)
                            if audio:
                                st.markdown(get_audio_html(audio, True), unsafe_allow_html=True)
                        except:
                            pass
    except:
        pass

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📝 Quiz History")
        if not results:
            st.info("No quizzes yet!")
            if st.button("📝 Take First Quiz", type="primary"):
                go_to("📝 Generate Quiz")
        for r in results[:8]:
            pct = r[1]/r[2]*100
            color = "#28a745" if pct >= 70 else "#ffc107" if pct >= 50 else "#dc3545"
            emoji = "🏆" if pct >= 80 else "👍" if pct >= 60 else "📚"
            qtype = r[4] if len(r) > 4 else "MCQ"
            diff = r[5] if len(r) > 5 else "Medium"
            st.markdown(f"""
            <div style='background:white;border-radius:14px;padding:14px 18px;margin:6px 0;
                        box-shadow:0 3px 15px rgba(102,126,234,0.1);border-left:5px solid {color}'>
                <div style='display:flex;justify-content:space-between;align-items:center'>
                    <div>
                        <span>{emoji}</span>
                        <b style='margin-left:6px'>{r[3][:20]}</b>
                        <span style='background:#f0f4ff;border-radius:8px;padding:2px 8px;
                                    font-size:0.75em;margin-left:6px;color:#667eea'>{qtype}</span>
                        <span style='background:#fff0f7;border-radius:8px;padding:2px 8px;
                                    font-size:0.75em;margin-left:4px;color:#f5576c'>{diff}</span>
                    </div>
                    <b style='color:{color}'>{pct:.0f}%</b>
                </div>
                <div style='color:#6b7280;font-size:0.8em;margin-top:4px'>
                    {r[0][:16]} · {r[1]}/{r[2]} correct</div>
            </div>""", unsafe_allow_html=True)

        # Export results
        if EXPORT_AVAILABLE and results:
            st.write("")
            results_txt = export_quiz_results_txt(results)
            st.download_button("📥 Download Progress Report",
                data=results_txt,
                file_name=f"progress_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain", use_container_width=True)

    with col2:
        st.markdown("### 🃏 Flashcard Stats")
        total_cards = sum(conf_stats.values()) if conf_stats else 0
        if total_cards == 0:
            st.info("Review flashcards to see stats!")
        else:
            for label, icon, color in [
                ("Know it","😎","#28a745"),
                ("Almost","🤔","#ffc107"),
                ("No idea","😅","#dc3545")
            ]:
                count = conf_stats.get(label, 0)
                pct = count/total_cards*100 if total_cards > 0 else 0
                st.markdown(f"""
                <div style='background:white;border-radius:12px;padding:14px 18px;margin:8px 0;
                            box-shadow:0 3px 15px rgba(102,126,234,0.1);border-left:5px solid {color}'>
                    <div style='display:flex;justify-content:space-between'>
                        <span>{icon} {label}</span>
                        <b style='color:{color}'>{count} ({pct:.0f}%)</b>
                    </div>
                    <div style='background:#f0f0f0;border-radius:8px;height:8px;margin-top:8px'>
                        <div style='background:{color};height:8px;border-radius:8px;width:{pct}%'></div>
                    </div>
                </div>""", unsafe_allow_html=True)

        st.markdown("### 📅 Study Activity")
        streak_data = get_study_streak()
        if streak_data:
            for study_date, xp in streak_data[:7]:
                st.markdown(f"""
                <div style='background:white;border-radius:10px;padding:10px 16px;margin:4px 0;
                            box-shadow:0 2px 10px rgba(102,126,234,0.08);
                            display:flex;justify-content:space-between'>
                    <span style='color:#6b7280'>📅 {study_date}</span>
                    <span style='color:#667eea;font-weight:800'>+{xp} XP</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("Start studying to build your streak!")