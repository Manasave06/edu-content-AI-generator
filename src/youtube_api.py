import streamlit as st
import sys
import os
import time
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date, timedelta

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
    get_flashcard_confidence_stats, get_subject_performance,
    get_all_subjects, save_study_schedule, get_study_schedule,
    complete_schedule_item
)
from youtube_api import search_youtube_videos, get_khan_academy_link

try:
    from speech import text_to_speech, get_audio_html, LANGUAGE_CODES
    from translator import translate_text, translate_quiz, translate_flashcards
    TTS_AVAILABLE = True
except:
    TTS_AVAILABLE = False
    LANGUAGE_CODES = {"English": "en"}

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
    background: linear-gradient(135deg, #667eea 0%, #764ba2 25%,
                #f093fb 50%, #f5576c 75%, #fda085 100%);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
    color: #1a1a2e;
}

@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.stApp > div {
    background: rgba(255,255,255,0.92);
    border-radius: 0;
    min-height: 100vh;
}

#MainMenu, footer, header { visibility: hidden; }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,
        #1a1a2e 0%, #16213e 40%, #0f3460 70%, #533483 100%) !important;
    border-right: 3px solid rgba(255,255,255,0.1) !important;
}
section[data-testid="stSidebar"] * { color: white !important; }
section[data-testid="stSidebar"] .stRadio label {
    background: rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    padding: 10px 16px !important;
    margin: 4px 0 !important;
    display: block !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    transition: all 0.3s !important;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.2) !important;
    transform: translateX(4px) !important;
}

.hero-title {
    font-size: 3.2em;
    font-weight: 900;
    background: linear-gradient(135deg, #667eea, #f093fb, #f5576c, #fda085);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin-bottom: 6px;
}

.hero-sub {
    color: #6b7280;
    font-size: 1.1em;
    font-weight: 600;
    margin-bottom: 24px;
}

/* Rainbow feature cards */
.feature-card {
    background: white;
    border-radius: 24px;
    padding: 28px 22px;
    margin: 8px 0;
    box-shadow: 0 8px 32px rgba(102,126,234,0.15);
    position: relative;
    overflow: hidden;
    text-align: center;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.feature-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 6px;
    background: var(--card-color);
}
.feature-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 20px 60px rgba(102,126,234,0.25);
}
.feature-icon { font-size: 3em; margin-bottom: 12px; }
.feature-title { font-size: 1.15em; font-weight: 900; color: #1a1a2e; }
.feature-desc { font-size: 0.85em; color: #6b7280; margin-top: 6px; line-height: 1.5; }

/* Subject cards */
.subject-card {
    border-radius: 20px;
    padding: 20px;
    margin: 8px 0;
    text-align: center;
    color: white;
    font-weight: 800;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}
.subject-card:hover { transform: translateY(-4px); }

/* YouTube card */
.youtube-card {
    background: white;
    border-radius: 16px;
    padding: 16px;
    margin: 10px 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    border-left: 5px solid #ff0000;
    transition: all 0.3s ease;
}
.youtube-card:hover {
    transform: translateX(4px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.12);
}

/* Khan Academy card */
.khan-card {
    background: linear-gradient(135deg, #14bf96, #0d9e7b);
    border-radius: 16px;
    padding: 20px;
    color: white;
    margin: 10px 0;
}

/* Schedule cards */
.schedule-card {
    background: white;
    border-radius: 16px;
    padding: 16px 20px;
    margin: 8px 0;
    box-shadow: 0 4px 15px rgba(102,126,234,0.1);
    border-left: 5px solid var(--accent, #667eea);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

/* Quiz cards */
.quiz-card {
    background: white;
    border-radius: 20px;
    padding: 24px 28px;
    margin: 16px 0;
    box-shadow: 0 6px 24px rgba(102,126,234,0.12);
    border-left: 6px solid #667eea;
    transition: all 0.3s ease;
}
.quiz-number {
    font-family: 'Fira Code', monospace;
    font-size: 0.72em; color: #667eea;
    font-weight: 700; letter-spacing: 3px;
    text-transform: uppercase; margin-bottom: 8px;
}
.quiz-question {
    font-size: 1.15em; font-weight: 800;
    color: #1a1a2e; line-height: 1.5;
}

/* Badges */
.badge-correct {
    background: linear-gradient(135deg,#d4edda,#c3e6cb);
    border: 2px solid #28a745; border-radius: 12px;
    padding: 10px 20px; color: #155724;
    font-weight: 800; display: inline-block; margin: 6px 0;
}
.badge-wrong {
    background: linear-gradient(135deg,#f8d7da,#f5c6cb);
    border: 2px solid #dc3545; border-radius: 12px;
    padding: 10px 20px; color: #721c24;
    font-weight: 800; display: inline-block; margin: 6px 0;
}
.explanation-box {
    background: linear-gradient(135deg,#e3f2fd,#bbdefb);
    border-left: 4px solid #2196f3;
    border-radius: 0 12px 12px 0;
    padding: 14px 18px; color: #0d47a1;
    font-size: 0.92em; margin-top: 10px; font-weight: 600;
}
.hint-box {
    background: linear-gradient(135deg,#fff9c4,#fff176);
    border-left: 4px solid #ffc107;
    border-radius: 0 12px 12px 0;
    padding: 12px 16px; color: #7c4d00;
    font-size: 0.88em; margin-top: 6px; font-weight: 600;
}

/* Score display */
.score-display {
    background: linear-gradient(135deg,#667eea,#764ba2,#f093fb);
    border-radius: 28px; padding: 48px;
    text-align: center;
    box-shadow: 0 20px 60px rgba(102,126,234,0.4);
}
.score-number { font-size: 5.5em; font-weight: 900; color: white; line-height: 1; }
.score-label { color: rgba(255,255,255,0.9); font-size: 1.2em; font-weight: 700; margin-top: 12px; }

/* Flashcards */
.fc-front {
    background: linear-gradient(135deg,#667eea,#764ba2);
    border-radius: 28px; padding: 50px 40px;
    text-align: center; font-size: 1.4em; font-weight: 800;
    color: white; min-height: 200px;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 20px 60px rgba(102,126,234,0.35);
}
.fc-back {
    background: linear-gradient(135deg,#11998e,#38ef7d);
    border-radius: 28px; padding: 50px 40px;
    text-align: center; font-size: 1.1em; font-weight: 700;
    color: white; min-height: 200px;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 20px 60px rgba(17,153,142,0.3); margin-top: 16px;
}

/* Confidence buttons */
.conf-know {
    background: linear-gradient(135deg,#28a745,#20c997);
    border-radius: 16px; padding: 16px;
    text-align: center; color: white; font-weight: 800;
    box-shadow: 0 6px 20px rgba(40,167,69,0.3);
}
.conf-almost {
    background: linear-gradient(135deg,#ffc107,#fd7e14);
    border-radius: 16px; padding: 16px;
    text-align: center; color: white; font-weight: 800;
    box-shadow: 0 6px 20px rgba(255,193,7,0.3);
}
.conf-noidea {
    background: linear-gradient(135deg,#dc3545,#c82333);
    border-radius: 16px; padding: 16px;
    text-align: center; color: white; font-weight: 800;
    box-shadow: 0 6px 20px rgba(220,53,69,0.3);
}

/* Chat */
.chat-user {
    background: linear-gradient(135deg,#667eea,#764ba2);
    border-radius: 20px 20px 6px 20px;
    padding: 18px 22px; margin: 12px 0; color: white;
    box-shadow: 0 6px 20px rgba(102,126,234,0.25);
}
.chat-ai {
    background: white; border: 2px solid #e8e8ff;
    border-radius: 20px 20px 20px 6px;
    padding: 18px 22px; margin: 12px 0; color: #1a1a2e;
    box-shadow: 0 6px 20px rgba(0,0,0,0.06);
}
.chat-label {
    font-size: 0.72em; font-weight: 900;
    letter-spacing: 3px; text-transform: uppercase;
    margin-bottom: 8px; opacity: 0.75;
}

/* XP and stat cards */
.xp-card {
    background: linear-gradient(135deg,#667eea,#764ba2,#f093fb);
    border-radius: 24px; padding: 24px;
    text-align: center; color: white;
    box-shadow: 0 10px 40px rgba(102,126,234,0.35);
}
.xp-number { font-size: 2.8em; font-weight: 900; }
.xp-label { font-size: 0.9em; opacity: 0.9; margin-top: 6px; }

.streak-card {
    background: linear-gradient(135deg,#f5576c,#f093fb);
    border-radius: 24px; padding: 24px;
    text-align: center; color: white;
    box-shadow: 0 10px 40px rgba(245,87,108,0.3);
}

.stat-card {
    background: white; border-radius: 24px;
    padding: 28px; text-align: center;
    box-shadow: 0 8px 30px rgba(102,126,234,0.1);
}
.stat-number {
    font-size: 3em; font-weight: 900;
    background: linear-gradient(135deg,#667eea,#f093fb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent; background-clip: text;
}
.stat-label {
    color: #6b7280; font-size: 0.9em; font-weight: 700;
    margin-top: 6px; text-transform: uppercase; letter-spacing: 1px;
}

/* Difficulty badges */
.badge-easy {
    background: linear-gradient(135deg,#d4edda,#c3e6cb);
    border: 2px solid #28a745; border-radius: 20px;
    padding: 4px 16px; color: #155724;
    font-weight: 800; font-size: 0.85em; display: inline-block;
}
.badge-medium {
    background: linear-gradient(135deg,#fff3cd,#ffeeba);
    border: 2px solid #ffc107; border-radius: 20px;
    padding: 4px 16px; color: #856404;
    font-weight: 800; font-size: 0.85em; display: inline-block;
}
.badge-hard {
    background: linear-gradient(135deg,#f8d7da,#f5c6cb);
    border: 2px solid #dc3545; border-radius: 20px;
    padding: 4px 16px; color: #721c24;
    font-weight: 800; font-size: 0.85em; display: inline-block;
}

/* Timer */
.timer-box {
    background: linear-gradient(135deg,#667eea,#764ba2);
    border-radius: 20px; padding: 18px 28px;
    text-align: center; color: white; margin: 14px 0;
    font-size: 1.8em; font-weight: 900;
    font-family: 'Fira Code', monospace;
    box-shadow: 0 8px 30px rgba(102,126,234,0.3);
}
.timer-warning {
    background: linear-gradient(135deg,#f5576c,#f093fb);
    border-radius: 20px; padding: 18px 28px;
    text-align: center; color: white; margin: 14px 0;
    font-size: 1.8em; font-weight: 900;
    font-family: 'Fira Code', monospace;
    animation: pulse 1s infinite;
}
@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.8; }
    100% { opacity: 1; }
}

/* Doc and sidebar status */
.doc-loaded {
    background: linear-gradient(135deg,rgba(255,255,255,0.2),rgba(255,255,255,0.1));
    border: 2px solid rgba(255,255,255,0.3);
    border-radius: 16px; padding: 14px; margin: 8px 0;
}
.doc-not-loaded {
    background: rgba(0,0,0,0.2);
    border: 2px solid rgba(255,255,255,0.15);
    border-radius: 16px; padding: 14px; margin: 8px 0;
}

/* Step cards */
.step-card {
    background: white; border-radius: 20px;
    padding: 18px 22px; margin: 8px 0;
    box-shadow: 0 6px 20px rgba(102,126,234,0.1);
    display: flex; align-items: center; gap: 16px;
    border: 1px solid rgba(102,126,234,0.1);
    transition: all 0.3s ease;
}
.step-card:hover {
    transform: translateX(6px);
    box-shadow: 0 10px 30px rgba(102,126,234,0.2);
}
.step-number {
    background: linear-gradient(135deg,#667eea,#764ba2);
    color: white; width: 42px; height: 42px;
    border-radius: 50%; display: flex;
    align-items: center; justify-content: center;
    font-weight: 900; font-size: 1.1em; flex-shrink: 0;
    box-shadow: 0 4px 15px rgba(102,126,234,0.4);
}

/* Content cards */
.content-card {
    background: white; border-radius: 20px;
    padding: 22px 26px; margin: 12px 0;
    box-shadow: 0 6px 24px rgba(102,126,234,0.1);
    border-left: 6px solid var(--accent, #667eea);
}

/* Buttons */
.stButton > button {
    border-radius: 14px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1em !important;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    border: none !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg,#667eea,#764ba2) !important;
    color: white !important;
    box-shadow: 0 6px 20px rgba(102,126,234,0.4) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow: 0 12px 30px rgba(102,126,234,0.5) !important;
}

/* Progress bar */
.stProgress > div > div {
    background: linear-gradient(90deg,#667eea,#f093fb,#f5576c) !important;
    border-radius: 10px !important;
}

/* Metrics */
[data-testid="metric-container"] {
    background: white !important;
    border-radius: 20px !important;
    padding: 20px !important;
    box-shadow: 0 6px 20px rgba(102,126,234,0.1) !important;
}

hr { border-color: rgba(102,126,234,0.15) !important; }
.nav-brand { font-size: 1.6em; font-weight: 900; color: white; }
.nav-sub { font-size: 0.85em; color: rgba(255,255,255,0.6); font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ── Subjects list ─────────────────────────────────────────────────────────
SUBJECTS = [
    "General", "Mathematics", "Science", "Physics", "Chemistry",
    "Biology", "History", "Geography", "English", "Computer Science",
    "Economics", "Psychology", "Philosophy", "Law", "Medicine",
    "Engineering", "Business", "Art", "Music", "Literature"
]

SUBJECT_COLORS = {
    "Mathematics": "linear-gradient(135deg,#667eea,#764ba2)",
    "Science": "linear-gradient(135deg,#11998e,#38ef7d)",
    "Physics": "linear-gradient(135deg,#4facfe,#00f2fe)",
    "Chemistry": "linear-gradient(135deg,#f093fb,#f5576c)",
    "Biology": "linear-gradient(135deg,#43e97b,#38f9d7)",
    "History": "linear-gradient(135deg,#fda085,#f6d365)",
    "Geography": "linear-gradient(135deg,#30cfd0,#330867)",
    "English": "linear-gradient(135deg,#a18cd1,#fbc2eb)",
    "Computer Science": "linear-gradient(135deg,#0f0c29,#302b63)",
    "Economics": "linear-gradient(135deg,#f7971e,#ffd200)",
    "General": "linear-gradient(135deg,#667eea,#764ba2)",
}

# ── Helper functions ──────────────────────────────────────────────────────
def home_button():
    col1, _ = st.columns([1, 6])
    with col1:
        if st.button("🏠 Home", key=f"home_{page}_{id(st.session_state)}",
                    use_container_width=True):
            st.query_params["page"] = "🏠 Home"
            st.rerun()

def get_subject_color(subject):
    return SUBJECT_COLORS.get(subject, "linear-gradient(135deg,#667eea,#764ba2)")

# ── Session State ─────────────────────────────────────────────────────────
defaults = {
    "doc_text": "", "doc_name": "", "doc_id": None,
    "doc_subject": "General",
    "quiz_questions": [], "quiz_answers": [],
    "quiz_submitted": False, "quiz_score": 0, "quiz_id": None,
    "quiz_type": "MCQ", "quiz_difficulty": "Medium",
    "tf_questions": [], "tf_answers": [], "tf_submitted": False, "tf_score": 0,
    "fb_questions": [], "fb_answers": [], "fb_submitted": False, "fb_score": 0,
    "flashcards": [], "fc_index": 0, "fc_flipped": False, "fc_confidence": [],
    "chat_history": [],
    "selected_lang": "English",
    "timer_active": False, "timer_start": None,
    "timer_duration": 600, "timer_expired": False,
    "study_content": None,
    "youtube_results": [],
    "selected_subject_filter": "All",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="nav-brand">🎓 EduContent AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-sub">Smart Study Assistant</div>', unsafe_allow_html=True)
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
    <div style="background:linear-gradient(135deg,rgba(102,126,234,0.3),rgba(118,75,162,0.3));
                border-radius:16px;padding:14px;margin-bottom:10px;text-align:center;
                border:1px solid rgba(255,255,255,0.2)">
        <div style="font-size:1.6em;font-weight:900">⚡ {total_xp} XP</div>
        <div style="font-size:0.85em;opacity:0.85;margin-top:4px">
            Level {level} · 🔥 {streak} day streak
        </div>
        <div style="background:rgba(255,255,255,0.2);border-radius:8px;
                    height:6px;margin-top:10px;overflow:hidden">
            <div style="background:linear-gradient(90deg,#667eea,#f093fb);
                        height:6px;width:{min((total_xp%100), 100)}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    pages = [
        "🏠 Home", "📤 Upload Document", "📝 Generate Quiz",
        "🃏 Flashcards", "📚 Study Content", "🎥 Video Resources",
        "📅 Study Schedule", "💬 Chat with Doc", "📊 Analytics"
    ]
    default_page = st.query_params.get("page", "🏠 Home")
    default_idx = pages.index(default_page) if default_page in pages else 0
    page = st.radio("Navigation", pages, index=default_idx,
                    label_visibility="collapsed")

    st.divider()
    if st.session_state["doc_name"]:
        color = get_subject_color(st.session_state.get("doc_subject","General"))
        st.markdown(f"""
        <div class="doc-loaded">
            <div style="font-size:0.65em;font-weight:900;letter-spacing:2px;
                        text-transform:uppercase;margin-bottom:4px;opacity:0.8">
                ✅ Document Loaded
            </div>
            <div style="font-weight:800;font-size:0.9em">
                {st.session_state["doc_name"][:25]}
            </div>
            <div style="font-size:0.75em;opacity:0.75;margin-top:4px">
                📚 {st.session_state.get("doc_subject","General")} ·
                {len(st.session_state["doc_text"]):,} chars
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="doc-not-loaded">
            <div style="font-size:0.65em;font-weight:900;letter-spacing:2px;
                        text-transform:uppercase;margin-bottom:4px">⚠️ No Document</div>
            <div style="font-size:0.8em;opacity:0.75">Upload a document first</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    if st.button("🏠 Go to Home", use_container_width=True, type="primary"):
        st.query_params["page"] = "🏠 Home"
        st.rerun()
    if st.button("🗑️ Clear Everything", use_container_width=True):
        for k, v in defaults.items():
            st.session_state[k] = v
        st.query_params.clear()
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# HOME
# ═══════════════════════════════════════════════════════════════════════════
if page == "🏠 Home":
    st.markdown('<div class="hero-title">🎓 EduContent AI<br>Smart Study Assistant</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Upload any document → AI generates personalized quizzes, flashcards, study notes, schedules & video resources ✨</div>',
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    cards_data = [
        ("📤", "Upload Docs", "PDF, TXT, DOCX with subject tagging",
         "linear-gradient(135deg,#667eea,#764ba2)", "📤 Upload Document"),
        ("📝", "Smart Quiz", "MCQ, T/F, Fill Blanks + Difficulty levels",
         "linear-gradient(135deg,#f093fb,#f5576c)", "📝 Generate Quiz"),
        ("🃏", "Flashcards", "Confidence rating + XP rewards",
         "linear-gradient(135deg,#4facfe,#00f2fe)", "🃏 Flashcards"),
        ("🎥", "Video Resources", "YouTube + Khan Academy links",
         "linear-gradient(135deg,#ff0000,#ff6b6b)", "🎥 Video Resources"),
        ("📅", "Study Schedule", "AI recommended study plan",
         "linear-gradient(135deg,#43e97b,#38f9d7)", "📅 Study Schedule"),
        ("📊", "Analytics", "Performance charts + subject stats",
         "linear-gradient(135deg,#fda085,#f6d365)", "📊 Analytics"),
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
            if st.button(f"Open {title}", key=f"nav_{title}",
                        use_container_width=True, type="primary"):
                st.query_params["page"] = target
                st.rerun()

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🚀 How It Works")
        for num, icon, text, color in [
            ("1","📤","Upload PDF, TXT or DOCX with subject tag","#667eea"),
            ("2","📚","Get AI study notes, summary and mind map","#f093fb"),
            ("3","📝","Take quiz: MCQ, True/False or Fill Blanks","#f5576c"),
            ("4","🎥","Watch related YouTube & Khan Academy videos","#ff0000"),
            ("5","📅","Follow your personalized study schedule","#43e97b"),
            ("6","📊","Track performance with beautiful charts","#fda085"),
        ]:
            st.markdown(f"""
            <div class="step-card">
                <div class="step-number" style="background:{color}">{num}</div>
                <div style="font-size:1.3em">{icon}</div>
                <div style="font-weight:700;color:#1a1a2e">{text}</div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 🏆 Your Stats")
        total_xp = get_total_xp()
        streak = get_streak_count()
        results = get_quiz_results()
        level = total_xp // 100 + 1

        st.markdown(f"""
        <div class="xp-card">
            <div class="xp-number">⚡ {total_xp} XP</div>
            <div class="xp-label">Level {level} Scholar · 🔥 {streak} Day Streak</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(min((total_xp % 100) / 100, 1.0))
        st.caption(f"{total_xp % 100}/100 XP to Level {level+1}")
        st.write("")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="streak-card">
                <div style="font-size:2em;font-weight:900">🔥 {streak}</div>
                <div style="font-size:0.8em;opacity:0.85">Day Streak</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#4facfe,#00f2fe);
                        border-radius:20px;padding:20px;text-align:center;color:white;
                        box-shadow:0 8px 25px rgba(79,172,254,0.3)">
                <div style="font-size:2em;font-weight:900">📝 {len(results)}</div>
                <div style="font-size:0.8em;opacity:0.85">Quizzes</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            avg = sum(r[1]/r[2]*100 for r in results)/len(results) if results else 0
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#43e97b,#38f9d7);
                        border-radius:20px;padding:20px;text-align:center;color:white;
                        box-shadow:0 8px 25px rgba(67,233,123,0.3)">
                <div style="font-size:2em;font-weight:900">{avg:.0f}%</div>
                <div style="font-size:0.8em;opacity:0.85">Avg Score</div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        st.markdown("### 📚 Subject Performance")
        subject_perf = get_subject_performance()
        if subject_perf:
            for subj, avg_score, attempts in subject_perf[:5]:
                color = get_subject_color(subj)
                st.markdown(f"""
                <div style="background:white;border-radius:14px;padding:12px 16px;
                            margin:6px 0;box-shadow:0 4px 15px rgba(102,126,234,0.1)">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <span style="font-weight:800">{subj}</span>
                        <span style="font-weight:900;color:#667eea">{avg_score:.0f}%</span>
                    </div>
                    <div style="background:#f0f0f0;border-radius:8px;height:6px;margin-top:8px">
                        <div style="background:{color};height:6px;border-radius:8px;
                                    width:{min(avg_score,100)}%"></div>
                    </div>
                    <div style="color:#6b7280;font-size:0.78em;margin-top:4px">
                        {attempts} quiz attempts
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Take quizzes to see subject performance!")

# ═══════════════════════════════════════════════════════════════════════════
# UPLOAD — with subject selection
# ═══════════════════════════════════════════════════════════════════════════
elif page == "📤 Upload Document":
    home_button()
    st.markdown('<div class="hero-title">📤 Upload Document</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Upload PDF, TXT or DOCX and tag it with a subject</div>',
                unsafe_allow_html=True)
    st.divider()

    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded = st.file_uploader("Drop file here", type=["pdf","txt","docx"],
                                    label_visibility="collapsed")
    with col2:
        selected_subject = st.selectbox("📚 Subject", SUBJECTS, index=0)

    if uploaded:
        with st.spinner("⚙️ Processing your document..."):
            try:
                text = process_file(uploaded)
                chunks = chunk_text(text)
                st.session_state["doc_text"] = text
                st.session_state["doc_name"] = uploaded.name
                st.session_state["doc_subject"] = selected_subject
                st.session_state["study_content"] = None
                doc_id = save_document(uploaded.name, text, selected_subject)
                st.session_state["doc_id"] = doc_id

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("📝 Characters", f"{len(text):,}")
                col2.metric("💬 Words", f"{len(text.split()):,}")
                col3.metric("🧩 Chunks", len(chunks))
                col4.metric("📚 Subject", selected_subject)

                color = get_subject_color(selected_subject)
                st.markdown(f"""
                <div style="background:{color};border-radius:16px;padding:16px 20px;
                            color:white;font-weight:800;font-size:1.1em;margin:12px 0">
                    ✅ '{uploaded.name}' loaded as {selected_subject}!
                </div>
                """, unsafe_allow_html=True)

                with st.expander("👀 Preview content"):
                    st.code(text[:1000], language=None)

                st.markdown("### 🚀 What would you like to do?")
                c1, c2, c3, c4, c5 = st.columns(5)
                with c1:
                    if st.button("📚 Study Notes", use_container_width=True, type="primary"):
                        st.query_params["page"] = "📚 Study Content"
                        st.rerun()
                with c2:
                    if st.button("📝 Quiz", use_container_width=True, type="primary"):
                        st.query_params["page"] = "📝 Generate Quiz"
                        st.rerun()
                with c3:
                    if st.button("🃏 Flashcards", use_container_width=True, type="primary"):
                        st.query_params["page"] = "🃏 Flashcards"
                        st.rerun()
                with c4:
                    if st.button("🎥 Videos", use_container_width=True, type="primary"):
                        st.query_params["page"] = "🎥 Video Resources"
                        st.rerun()
                with c5:
                    if st.button("💬 Chat", use_container_width=True, type="primary"):
                        st.query_params["page"] = "💬 Chat with Doc"
                        st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")
    else:
        st.markdown("### 📂 Supported Formats")
        col1, col2, col3 = st.columns(3)
        for col, icon, title, desc, color in zip(
            [col1, col2, col3],
            ["📄","📝","📘"],
            ["PDF Files","TXT Files","DOCX Files"],
            ["Textbooks, papers, articles",
             "Notes, transcripts, content",
             "Word documents, assignments"],
            ["linear-gradient(135deg,#667eea,#764ba2)",
             "linear-gradient(135deg,#f093fb,#f5576c)",
             "linear-gradient(135deg,#43e97b,#38f9d7)"]
        ):
            with col:
                st.markdown(f"""
                <div class="feature-card" style="--card-color:{color}">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-title">{title}</div>
                    <div class="feature-desc">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()
        st.markdown("### 📚 Available Subjects")
        cols = st.columns(5)
        for i, subj in enumerate(SUBJECTS[1:11]):
            with cols[i % 5]:
                color = get_subject_color(subj)
                st.markdown(f"""
                <div class="subject-card" style="background:{color};font-size:0.85em">
                    {subj}
                </div>
                """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# VIDEO RESOURCES — YouTube + Khan Academy
# ═══════════════════════════════════════════════════════════════════════════
elif page == "🎥 Video Resources":
    home_button()
    st.markdown('<div class="hero-title">🎥 Video Resources</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">YouTube educational videos + Khan Academy resources for your topic</div>',
                unsafe_allow_html=True)
    st.divider()

    col1, col2 = st.columns([3, 1])
    with col1:
        search_topic = st.text_input(
            "Search topic",
            value=st.session_state.get("doc_subject","") if st.session_state.get("doc_subject","") != "General" else "",
            placeholder="e.g. Photosynthesis, Machine Learning, World War 2...",
            label_visibility="collapsed"
        )
    with col2:
        search_btn = st.button("🔍 Search", type="primary", use_container_width=True)

    if search_btn and search_topic:
        with st.spinner("🔍 Finding best educational resources..."):
            videos = search_youtube_videos(search_topic)
            st.session_state["youtube_results"] = videos

    if st.session_state["doc_text"] and not search_topic:
        st.info(f"💡 Tip: Search for **{st.session_state.get('doc_subject','your topic')}** to find related videos!")

    st.divider()
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("### 🎬 YouTube Educational Videos")
        videos = st.session_state.get("youtube_results", [])
        if videos:
            for v in videos:
                st.markdown(f"""
                <div class="youtube-card">
                    <div style="display:flex;align-items:flex-start;gap:12px">
                        <div style="font-size:2em">▶️</div>
                        <div style="flex:1">
                            <div style="font-weight:800;color:#1a1a2e;font-size:1em">
                                {v["title"][:60]}
                            </div>
                            <div style="color:#ff0000;font-size:0.8em;font-weight:700;margin-top:2px">
                                📺 {v["channel"]}
                            </div>
                            <div style="color:#6b7280;font-size:0.82em;margin-top:4px">
                                {v["description"]}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"▶️ Watch Video", key=f"yt_{v['video_id']}_{v['title'][:10]}",
                            use_container_width=True):
                    st.markdown(f"[🔗 Open: {v['title'][:40]}]({v['url']})")
                    st.write(f"**Link:** {v['url']}")
        else:
            st.info("🔍 Search for a topic above to find educational videos!")
            st.markdown("### 🌟 Popular Topics")
            topics = ["Machine Learning","Photosynthesis","World War 2",
                     "Algebra","Python Programming","Human Anatomy",
                     "Climate Change","French Revolution"]
            cols = st.columns(4)
            for i, topic in enumerate(topics):
                with cols[i % 4]:
                    if st.button(topic, key=f"topic_{topic}", use_container_width=True):
                        with st.spinner(f"Finding {topic} videos..."):
                            videos = search_youtube_videos(topic)
                            st.session_state["youtube_results"] = videos
                        st.rerun()

    with col2:
        st.markdown("### 🟢 Khan Academy")
        if search_topic:
            khan = get_khan_academy_link(search_topic)
            st.markdown(f"""
            <div class="khan-card">
                <div style="font-size:1.5em;margin-bottom:8px">📗</div>
                <div style="font-weight:800;font-size:1.1em">Khan Academy</div>
                <div style="font-size:0.85em;opacity:0.9;margin-top:6px">
                    Free lessons on {search_topic}
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"[🔗 Open Khan Academy]({khan['url']})")

        st.divider()
        st.markdown("### 📚 Quick Links")
        resources = [
            ("🟢","Khan Academy","https://www.khanacademy.org","Free lessons"),
            ("🔴","YouTube EDU","https://www.youtube.com/education","Video tutorials"),
            ("🔵","Coursera","https://www.coursera.org","Online courses"),
            ("🟠","edX","https://www.edx.org","University courses"),
            ("🟣","MIT OCW","https://ocw.mit.edu","Free MIT courses"),
        ]
        for emoji, name, url, desc in resources:
            st.markdown(f"""
            <div style="background:white;border-radius:12px;padding:12px 16px;
                        margin:6px 0;box-shadow:0 3px 12px rgba(102,126,234,0.1)">
                <div style="font-weight:800">{emoji} {name}</div>
                <div style="color:#6b7280;font-size:0.8em">{desc}</div>
                <a href="{url}" target="_blank" style="font-size:0.78em;color:#667eea">
                    🔗 Visit →
                </a>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# STUDY SCHEDULE
# ═══════════════════════════════════════════════════════════════════════════
elif page == "📅 Study Schedule":
    home_button()
    st.markdown('<div class="hero-title">📅 Study Schedule</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">AI-recommended personalized study plan based on your weak areas</div>',
                unsafe_allow_html=True)
    st.divider()

    subject_perf = get_subject_performance()
    schedule = get_study_schedule()

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 🤖 Generate Study Schedule")

        if st.button("⚡ Generate Personalized Schedule", type="primary",
                    use_container_width=True):
            weak_subjects = []
            if subject_perf:
                weak_subjects = [s for s, avg, _ in subject_perf if avg < 70]
            if not weak_subjects:
                weak_subjects = get_all_subjects() or ["General"]

            today = date.today()
            schedule_items = []
            for i, subj in enumerate(weak_subjects[:7]):
                study_date = today + timedelta(days=i)
                duration = 45 if subj in [s for s,avg,_ in subject_perf if avg < 50] else 30
                save_study_schedule(subj, study_date.isoformat(), duration)
                schedule_items.append((subj, study_date, duration))

            st.success(f"✅ Created {len(schedule_items)} day study plan!")
            st.rerun()

        st.divider()
        st.markdown("### 📋 Your Study Plan")
        schedule = get_study_schedule()
        if schedule:
            for item in schedule:
                sid, subj, rec_date, duration, completed = item
                color = get_subject_color(subj)
                status_icon = "✅" if completed else "📖"
                today_str = date.today().isoformat()
                is_today = rec_date == today_str
                border_color = "#28a745" if completed else "#667eea" if is_today else "#dee2e6"

                st.markdown(f"""
                <div style="background:white;border-radius:16px;padding:16px 20px;
                            margin:8px 0;box-shadow:0 4px 15px rgba(102,126,234,0.1);
                            border-left:6px solid {border_color}">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <div>
                            <span style="font-size:1.2em">{status_icon}</span>
                            <b style="margin-left:8px;color:#1a1a2e">{subj}</b>
                            {'<span style="background:#667eea;color:white;border-radius:8px;padding:2px 8px;font-size:0.75em;margin-left:8px">TODAY</span>' if is_today else ''}
                        </div>
                        <div style="text-align:right">
                            <div style="font-weight:800;color:#667eea">⏱️ {duration} mins</div>
                            <div style="color:#6b7280;font-size:0.8em">📅 {rec_date}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if not completed:
                    if st.button(f"✅ Mark Done", key=f"done_{sid}",
                                use_container_width=False):
                        complete_schedule_item(sid)
                        st.rerun()
        else:
            st.info("Click 'Generate Personalized Schedule' to create your study plan!")

    with col2:
        st.markdown("### 💡 Study Tips")
        tips = [
            ("🧠","Spaced Repetition","Study a topic, then review after 1 day, 3 days, then 1 week"),
            ("⏱️","Pomodoro Method","Study for 25 minutes, then take a 5 minute break"),
            ("📝","Active Recall","Test yourself instead of just re-reading notes"),
            ("🌙","Sleep Well","Your brain consolidates memory during sleep"),
            ("🎯","Focus on Weak Areas","Spend more time on subjects where you score below 70%"),
        ]
        for icon, title, desc in tips:
            st.markdown(f"""
            <div style="background:white;border-radius:16px;padding:14px 18px;
                        margin:8px 0;box-shadow:0 4px 15px rgba(102,126,234,0.08)">
                <div style="font-size:1.4em">{icon}</div>
                <div style="font-weight:800;color:#1a1a2e;margin-top:4px">{title}</div>
                <div style="color:#6b7280;font-size:0.82em;margin-top:4px">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

        if subject_perf:
            st.divider()
            st.markdown("### 🎯 Weak Areas")
            weak = [(s,avg) for s,avg,_ in subject_perf if avg < 70]
            if weak:
                for subj, avg in weak:
                    color = "#dc3545" if avg < 50 else "#ffc107"
                    st.markdown(f"""
                    <div style="background:white;border-radius:12px;padding:12px 16px;
                                margin:6px 0;border-left:4px solid {color}">
                        <b>{subj}</b>: <span style="color:{color};font-weight:800">{avg:.0f}%</span>
                        <div style="color:#6b7280;font-size:0.8em">Needs more practice</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("🎉 No weak areas! Keep it up!")

# ═══════════════════════════════════════════════════════════════════════════
# ANALYTICS — Performance charts
# ═══════════════════════════════════════════════════════════════════════════
elif page == "📊 Analytics":
    home_button()
    st.markdown('<div class="hero-title">📊 Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Track your learning performance with beautiful charts</div>',
                unsafe_allow_html=True)
    st.divider()

    total_xp = get_total_xp()
    streak = get_streak_count()
    results = get_quiz_results()
    level = total_xp // 100 + 1
    conf_stats = get_flashcard_confidence_stats()
    subject_perf = get_subject_performance()

    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="xp-card"><div class="xp-number">⚡ {total_xp}</div><div class="xp-label">Total XP · Level {level}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="streak-card"><div class="xp-number">🔥 {streak}</div><div class="xp-label">Day Streak</div></div>', unsafe_allow_html=True)
    with col3:
        avg = sum(r[1]/r[2]*100 for r in results)/len(results) if results else 0
        st.markdown(f'<div class="stat-card"><div class="stat-number">{avg:.0f}%</div><div class="stat-label">Avg Score</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len(results)}</div><div class="stat-label">Quizzes Taken</div></div>', unsafe_allow_html=True)

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        # Quiz score trend chart
        st.markdown("### 📈 Quiz Score Trend")
        if results:
            dates = [r[0][:10] for r in results[:10]][::-1]
            scores = [r[1]/r[2]*100 for r in results[:10]][::-1]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates, y=scores,
                mode='lines+markers',
                line=dict(color='#667eea', width=3),
                marker=dict(size=10, color='#764ba2',
                           line=dict(color='white', width=2)),
                fill='tozeroy',
                fillcolor='rgba(102,126,234,0.1)',
                name='Score %'
            ))
            fig.add_hline(y=70, line_dash="dash",
                         line_color="#28a745", annotation_text="Target 70%")
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                yaxis=dict(range=[0,100], title='Score %'),
                xaxis=dict(title='Date'),
                margin=dict(l=20,r=20,t=20,b=20),
                showlegend=False,
                height=280
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Take quizzes to see your score trend!")

        # Subject performance bar chart
        st.markdown("### 📚 Subject Performance")
        if subject_perf:
            subjects = [r[0] for r in subject_perf]
            avgs = [r[1] for r in subject_perf]
            colors_list = ['#667eea','#f093fb','#f5576c','#fda085',
                          '#43e97b','#4facfe','#11998e']
            fig2 = go.Figure(go.Bar(
                x=subjects, y=avgs,
                marker=dict(
                    color=colors_list[:len(subjects)],
                    line=dict(color='white', width=2)
                ),
                text=[f'{a:.0f}%' for a in avgs],
                textposition='outside',
            ))
            fig2.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                yaxis=dict(range=[0,110], title='Average Score %'),
                margin=dict(l=20,r=20,t=20,b=20),
                showlegend=False,
                height=280
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Take subject quizzes to see performance!")

    with col2:
        # XP streak chart
        st.markdown("### ⚡ XP Earned per Day")
        streak_data = get_study_streak()
        if streak_data:
            dates = [r[0] for r in streak_data[:14]][::-1]
            xps = [r[1] for r in streak_data[:14]][::-1]
            fig3 = go.Figure(go.Bar(
                x=dates, y=xps,
                marker=dict(
                    color=xps,
                    colorscale='Viridis',
                    line=dict(color='white', width=1)
                ),
                text=xps,
                textposition='outside',
            ))
            fig3.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                yaxis=dict(title='XP Earned'),
                margin=dict(l=20,r=20,t=20,b=40),
                showlegend=False,
                height=280
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Start studying to see XP history!")

        # Flashcard confidence pie chart
        st.markdown("### 🃏 Flashcard Confidence")
        if conf_stats:
            labels = list(conf_stats.keys())
            values = list(conf_stats.values())
            colors_pie = ['#28a745','#ffc107','#dc3545']
            fig4 = go.Figure(go.Pie(
                labels=labels, values=values,
                marker=dict(colors=colors_pie,
                           line=dict(color='white', width=3)),
                hole=0.5,
                textinfo='label+percent',
                textfont=dict(size=13, family='Nunito')
            ))
            fig4.update_layout(
                margin=dict(l=20,r=20,t=20,b=20),
                showlegend=True,
                height=280
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Review flashcards to see confidence stats!")

        # Quiz type breakdown
        st.markdown("### 📋 Quiz Type Breakdown")
        if results:
            type_counts = {}
            for r in results:
                qtype = r[4] if len(r) > 4 else "MCQ"
                type_counts[qtype] = type_counts.get(qtype, 0) + 1

            fig5 = go.Figure(go.Bar(
                x=list(type_counts.keys()),
                y=list(type_counts.values()),
                marker=dict(
                    color=['#667eea','#f093fb','#43e97b'],
                    line=dict(color='white', width=2)
                ),
                text=list(type_counts.values()),
                textposition='outside'
            ))
            fig5.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                yaxis=dict(title='Count'),
                margin=dict(l=20,r=20,t=20,b=20),
                showlegend=False,
                height=240
            )
            st.plotly_chart(fig5, use_container_width=True)

    st.divider()
    st.markdown("### 📝 Recent Quiz History")
    if results:
        for r in results[:10]:
            pct = r[1]/r[2]*100
            color = "#28a745" if pct >= 70 else "#ffc107" if pct >= 50 else "#dc3545"
            emoji = "🏆" if pct >= 80 else "👍" if pct >= 60 else "📚"
            qtype = r[4] if len(r) > 4 else "MCQ"
            diff = r[5] if len(r) > 5 else "Medium"
            subj = r[6] if len(r) > 6 else "General"
            st.markdown(f"""
            <div style='background:white;border-radius:16px;padding:16px 22px;margin:8px 0;
                        box-shadow:0 4px 20px rgba(102,126,234,0.1);
                        border-left:6px solid {color}'>
                <div style='display:flex;justify-content:space-between;align-items:center'>
                    <div>
                        <span style='font-size:1.4em'>{emoji}</span>
                        <b style='color:#1a1a2e;margin-left:8px'>{r[3][:25]}</b>
                        <span style='background:#f0f4ff;border-radius:8px;padding:2px 10px;
                                    font-size:0.75em;margin-left:8px;color:#667eea;
                                    font-weight:700'>{qtype}</span>
                        <span style='background:#fff0f7;border-radius:8px;padding:2px 10px;
                                    font-size:0.75em;margin-left:4px;color:#f5576c;
                                    font-weight:700'>{diff}</span>
                        <span style='background:#f0fff4;border-radius:8px;padding:2px 10px;
                                    font-size:0.75em;margin-left:4px;color:#28a745;
                                    font-weight:700'>{subj}</span>
                    </div>
                    <b style='color:{color};font-size:1.3em'>{pct:.0f}%</b>
                </div>
                <div style='color:#6b7280;font-size:0.8em;margin-top:6px'>
                    📅 {r[0][:16]} · ✅ {r[1]}/{r[2]} correct
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Take quizzes to see your history here!")

# ═══════════════════════════════════════════════════════════════════════════
# STUDY CONTENT
# ═══════════════════════════════════════════════════════════════════════════
elif page == "📚 Study Content":
    home_button()
    st.markdown('<div class="hero-title">📚 Study Content</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">AI generates summary, key points, mind map and exam tips</div>',
                unsafe_allow_html=True)
    st.divider()

    if not st.session_state["doc_text"]:
        st.warning("⚠️ Please upload a document first!")
        if st.button("📤 Go to Upload", type="primary"):
            st.query_params["page"] = "📤 Upload Document"
            st.rerun()
        st.stop()

    if st.button("⚡ Generate Study Content", type="primary", use_container_width=True):
        with st.spinner("🤖 AI is analyzing your document..."):
            try:
                content = generate_study_content(st.session_state["doc_text"])
                st.session_state["study_content"] = content
                st.success("✅ Study content ready!")
            except Exception as e:
                st.error(f"❌ Error: {e}")

    if st.session_state["study_content"]:
        content = st.session_state["study_content"]
        st.divider()

        if "one_liner" in content:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#667eea,#764ba2,#f093fb);
                        border-radius:20px;padding:22px 28px;color:white;
                        font-size:1.25em;font-weight:800;text-align:center;
                        box-shadow:0 10px 40px rgba(102,126,234,0.3);margin-bottom:20px">
                💡 {content["one_liner"]}
            </div>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📖 Summary")
            st.markdown(f"""
            <div class="content-card" style="--accent:#667eea">
                {content.get("summary","")}
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### 🎯 Key Points")
            for i, point in enumerate(content.get("key_points",[]), 1):
                st.markdown(f"""
                <div style="background:white;border-radius:14px;padding:14px 18px;
                            margin:8px 0;box-shadow:0 4px 15px rgba(102,126,234,0.1);
                            border-left:5px solid #667eea">
                    <b style="color:#667eea">{i}.</b> {point}
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown("### 📝 Exam Tips")
            for tip in content.get("exam_tips",[]):
                st.markdown(f"""
                <div style="background:white;border-radius:14px;padding:14px 18px;
                            margin:8px 0;box-shadow:0 4px 15px rgba(102,126,234,0.1);
                            border-left:5px solid #f093fb">
                    ✅ {tip}
                </div>
                """, unsafe_allow_html=True)

            st.markdown("### 📖 Key Terms")
            for term in content.get("difficult_terms",[]):
                st.markdown(f"""
                <div style="background:white;border-radius:14px;padding:14px 18px;
                            margin:8px 0;box-shadow:0 4px 15px rgba(102,126,234,0.1);
                            border-left:5px solid #43e97b">
                    <b style="color:#11998e">{term.get("term","")}</b>:
                    {term.get("definition","")}
                </div>
                """, unsafe_allow_html=True)

        st.markdown("### 🗺️ Mind Map")
        mind_map = content.get("mind_map",{})
        for main_topic, subtopics in mind_map.items():
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#667eea,#764ba2);
                        border-radius:16px;padding:16px 22px;color:white;
                        font-weight:900;font-size:1.15em;margin:10px 0">
                🧠 {main_topic}
            </div>
            """, unsafe_allow_html=True)
            cols = st.columns(min(len(subtopics), 4))
            for i, sub in enumerate(subtopics):
                with cols[i % 4]:
                    st.markdown(f"""
                    <div style="background:white;border-radius:12px;padding:12px 16px;
                                margin:4px 0;box-shadow:0 4px 15px rgba(102,126,234,0.1);
                                border-left:4px solid #667eea;font-size:0.9em">
                        → {sub}
                    </div>
                    """, unsafe_allow_html=True)

        st.divider()
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("📝 Take Quiz", use_container_width=True, type="primary"):
                st.query_params["page"] = "📝 Generate Quiz"
                st.rerun()
        with c2:
            if st.button("🎥 Find Videos", use_container_width=True, type="primary"):
                st.query_params["page"] = "🎥 Video Resources"
                st.rerun()
        with c3:
            if st.button("📅 Study Schedule", use_container_width=True, type="primary"):
                st.query_params["page"] = "📅 Study Schedule"
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# QUIZ
# ═══════════════════════════════════════════════════════════════════════════
elif page == "📝 Generate Quiz":
    home_button()
    st.markdown('<div class="hero-title">📝 Quiz Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Choose quiz type, difficulty and subject</div>',
                unsafe_allow_html=True)
    st.divider()

    if not st.session_state["doc_text"]:
        st.warning("⚠️ Please upload a document first!")
        if st.button("📤 Go to Upload", type="primary"):
            st.query_params["page"] = "📤 Upload Document"
            st.rerun()
        st.stop()

    st.markdown("### 📋 Select Quiz Type")
    t1, t2, t3 = st.columns(3)
    for col, qtype, icon, desc in zip(
        [t1, t2, t3],
        ["MCQ","True/False","Fill Blanks"],
        ["🔘","✅","✏️"],
        ["Multiple Choice","True or False","Complete the sentence"]
    ):
        with col:
            selected = st.session_state["quiz_type"] == qtype
            st.markdown(f"""
            <div style="background:white;border-radius:20px;padding:22px;
                        text-align:center;box-shadow:0 6px 24px rgba(102,126,234,0.12);
                        border:3px solid {'#667eea' if selected else 'transparent'};
                        transition:all 0.3s">
                <div style="font-size:2.5em">{icon}</div>
                <div style="font-weight:900;margin-top:8px;font-size:1.05em">{qtype}</div>
                <div style="color:#6b7280;font-size:0.85em;margin-top:4px">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(
                f"{'✅ Selected' if selected else 'Select'}",
                key=f"sel_{qtype}", use_container_width=True,
                type="primary" if selected else "secondary"
            ):
                st.session_state["quiz_type"] = qtype
                st.rerun()

    st.divider()
    st.markdown("### ⚙️ Quiz Settings")
    col1, col2, col3, col4, col5 = st.columns([2,2,2,2,1])
    with col1:
        num_q = st.slider("Questions", 3, 15, 5)
    with col2:
        difficulty = st.selectbox("🎯 Difficulty", ["Easy","Medium","Hard"], index=1)
        st.session_state["quiz_difficulty"] = difficulty
    with col3:
        quiz_subject = st.selectbox("📚 Subject",
            [st.session_state.get("doc_subject","General")] +
            [s for s in SUBJECTS if s != st.session_state.get("doc_subject","General")],
            index=0
        )
    with col4:
        timer_mins = st.selectbox("⏱️ Timer",
            ["No Timer","5 mins","10 mins","15 mins","20 mins","30 mins"])
    with col5:
        st.write("")
        st.write("")
        gen = st.button("⚡ Go!", type="primary", use_container_width=True)

    badge_cls = {"Easy":"badge-easy","Medium":"badge-medium","Hard":"badge-hard"}
    st.markdown(
        f'<span class="{badge_cls[difficulty]}">🎯 {difficulty}</span> &nbsp;'
        f'<span style="color:#6b7280;font-size:0.9em">Type: {st.session_state["quiz_type"]} · Subject: {quiz_subject}</span>',
        unsafe_allow_html=True
    )

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

                quiz_id = save_quiz(st.session_state["doc_id"] or 1, [], quiz_subject)
                st.session_state["quiz_id"] = quiz_id
                st.session_state["quiz_subject"] = quiz_subject

                if timer_mins != "No Timer":
                    mins = int(timer_mins.split()[0])
                    st.session_state["timer_duration"] = mins * 60
                    st.session_state["timer_active"] = True
                    st.session_state["timer_start"] = time.time()
                    st.session_state["timer_expired"] = False
                else:
                    st.session_state["timer_active"] = False
                    st.session_state["timer_expired"] = False

                st.success(f"✅ {num_q} {qtype} questions ({difficulty}) ready!")
            except Exception as e:
                st.error(f"❌ {e}")

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
            timer_ph.markdown(
                f'<div class="{cls}">⏱️ {m:02d}:{s:02d}</div>',
                unsafe_allow_html=True
            )
            time.sleep(1)
            st.rerun()

    if st.session_state.get("timer_expired"):
        st.error("⏰ Time's Up!")

    st.divider()

    def show_score(score, total, qtype, diff):
        pct = score/total*100
        subj = st.session_state.get("quiz_subject","General")
        save_quiz_result(st.session_state["quiz_id"] or 1,
                        score, total, qtype, diff, subj)
        xp = score * 10
        st.markdown(f"""
        <div class="score-display">
            <div class="score-number">{pct:.0f}%</div>
            <div class="score-label">
                🎯 {score}/{total} correct · {diff} · {subj} · +{xp} XP!
            </div>
        </div>
        """, unsafe_allow_html=True)
        if pct >= 80:
            st.balloons()
        st.write("")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🏠 Home", use_container_width=True,
                        type="primary", key="score_home"):
                st.query_params["page"] = "🏠 Home"
                st.rerun()
        with c2:
            if st.button("📊 Analytics", use_container_width=True,
                        key="score_analytics"):
                st.query_params["page"] = "📊 Analytics"
                st.rerun()
        with c3:
            if st.button("🎥 Watch Videos", use_container_width=True,
                        key="score_videos"):
                st.query_params["page"] = "🎥 Video Resources"
                st.rerun()

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
                <div style="display:flex;justify-content:space-between;margin-bottom:8px">
                    <div class="quiz-number">Q{i+1} of {len(questions)}</div>
                    <span class="{badge_cls.get(diff,'badge-medium')}">{diff}</span>
                </div>
                <div class="quiz-question">{q["question"]}</div>
            </div>
            """, unsafe_allow_html=True)
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

    elif st.session_state["quiz_type"] == "True/False" and st.session_state["tf_questions"]:
        questions = st.session_state["tf_questions"]
        diff = st.session_state["quiz_difficulty"]
        for i, q in enumerate(questions):
            submitted = st.session_state["tf_submitted"]
            chosen = st.session_state["tf_answers"][i]
            correct = q["answer"]
            st.markdown(f"""
            <div class="quiz-card" style="border-left-color:#11998e">
                <div style="display:flex;justify-content:space-between;margin-bottom:8px">
                    <div class="quiz-number">Statement {i+1}</div>
                    <span class="{badge_cls.get(diff,'badge-medium')}">{diff}</span>
                </div>
                <div class="quiz-question">{q["question"]}</div>
            </div>
            """, unsafe_allow_html=True)
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

    elif st.session_state["quiz_type"] == "Fill Blanks" and st.session_state["fb_questions"]:
        questions = st.session_state["fb_questions"]
        diff = st.session_state["quiz_difficulty"]
        for i, q in enumerate(questions):
            submitted = st.session_state["fb_submitted"]
            correct = q["answer"]
            st.markdown(f"""
            <div class="quiz-card" style="border-left-color:#f093fb">
                <div style="display:flex;justify-content:space-between;margin-bottom:8px">
                    <div class="quiz-number">Q{i+1}</div>
                    <span class="{badge_cls.get(diff,'badge-medium')}">{diff}</span>
                </div>
                <div class="quiz-question">{q["question"]}</div>
            </div>
            """, unsafe_allow_html=True)
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
                    st.markdown(f'<div class="badge-wrong">❌ Answer: {correct}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="explanation-box">💡 {q.get("explanation","")}</div>', unsafe_allow_html=True)
            st.write("")

        if not st.session_state["fb_submitted"]:
            if st.button("✅ Submit Fill Blanks", type="primary", use_container_width=True):
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
            st.query_params["page"] = "📤 Upload Document"
            st.rerun()
        st.stop()

    col1, col2 = st.columns([3,1])
    with col1:
        num_cards = st.slider("Number of flashcards", 5, 20, 8)
    with col2:
        st.write("")
        gen = st.button("⚡ Generate", type="primary", use_container_width=True)

    if gen:
        with st.spinner("🤖 Creating smart flashcards..."):
            try:
                cards = generate_flashcards(st.session_state["doc_text"], num_cards)
                if TTS_AVAILABLE and st.session_state["selected_lang"] != "English":
                    lang_code = LANGUAGE_CODES[st.session_state["selected_lang"]]
                    cards = translate_flashcards(cards, lang_code)
                save_flashcards(st.session_state["doc_id"] or 1, cards)
                st.session_state["flashcards"] = cards
                st.session_state["fc_index"] = 0
                st.session_state["fc_flipped"] = False
                st.session_state["fc_confidence"] = [None]*len(cards)
                st.success(f"✅ {len(cards)} smart flashcards ready!")
            except Exception as e:
                st.error(f"❌ Error: {e}")

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
                lang_code = LANGUAGE_CODES[st.session_state["selected_lang"]]
                af = text_to_speech(card["front"], lang_code)
                if af:
                    st.markdown(get_audio_html(af), unsafe_allow_html=True)

            if st.session_state["fc_flipped"]:
                st.markdown(f'<div class="fc-back">✅ {card["back"]}</div>', unsafe_allow_html=True)
                if TTS_AVAILABLE:
                    ab = text_to_speech(card["back"], lang_code)
                    if ab:
                        st.markdown(get_audio_html(ab), unsafe_allow_html=True)

                st.divider()
                st.markdown("**How well did you know this?**")
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("😎 Know it!\n+15 XP", use_container_width=True,
                                key="conf_know"):
                        st.session_state["fc_confidence"][idx] = "Know it"
                        save_flashcard_confidence(card["front"], "Know it")
                        if idx < len(cards)-1:
                            st.session_state["fc_index"] += 1
                            st.session_state["fc_flipped"] = False
                        st.rerun()
                with c2:
                    if st.button("🤔 Almost\n+8 XP", use_container_width=True,
                                key="conf_almost"):
                        st.session_state["fc_confidence"][idx] = "Almost"
                        save_flashcard_confidence(card["front"], "Almost")
                        if idx < len(cards)-1:
                            st.session_state["fc_index"] += 1
                            st.session_state["fc_flipped"] = False
                        st.rerun()
                with c3:
                    if st.button("😅 No idea\n+3 XP", use_container_width=True,
                                key="conf_noidea"):
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
            st.markdown("### 📊 Confidence Summary")
            stats = {}
            for c in confidence_list:
                if c:
                    stats[c] = stats.get(c, 0) + 1
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="conf-know">😎 Know it<br><b style="font-size:1.8em">{stats.get("Know it",0)}</b></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="conf-almost">🤔 Almost<br><b style="font-size:1.8em">{stats.get("Almost",0)}</b></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="conf-noidea">😅 No idea<br><b style="font-size:1.8em">{stats.get("No idea",0)}</b></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# CHAT
# ═══════════════════════════════════════════════════════════════════════════
elif page == "💬 Chat with Doc":
    home_button()
    st.markdown('<div class="hero-title">💬 Chat with Doc</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Ask anything — AI answers from your document only</div>',
                unsafe_allow_html=True)
    st.divider()

    if not st.session_state["doc_text"]:
        st.warning("⚠️ Please upload a document first!")
        if st.button("📤 Go to Upload", type="primary"):
            st.query_params["page"] = "📤 Upload Document"
            st.rerun()
        st.stop()

    for h in st.session_state["chat_history"]:
        st.markdown(f'<div class="chat-user"><div class="chat-label">🧑 You</div>{h["user"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-ai"><div class="chat-label">🤖 AI Assistant</div>{h["assistant"]}</div>', unsafe_allow_html=True)
        if TTS_AVAILABLE:
            lang_code = LANGUAGE_CODES[st.session_state["selected_lang"]]
            audio = text_to_speech(h["assistant"], lang_code)
            if audio:
                st.markdown(get_audio_html(audio), unsafe_allow_html=True)

    question = st.chat_input("Ask anything about your document...")
    if question:
        with st.spinner("🤔 Thinking..."):
            try:
                answer = chat_with_doc(st.session_state["doc_text"], question,
                                      st.session_state["chat_history"])
                if TTS_AVAILABLE and st.session_state["selected_lang"] != "English":
                    lang_code = LANGUAGE_CODES[st.session_state["selected_lang"]]
                    answer = translate_text(answer, lang_code)
                st.session_state["chat_history"].append(
                    {"user": question, "assistant": answer}
                )
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")

    if st.session_state["chat_history"]:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state["chat_history"] = []
            st.rerun()