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
    from translator import translate_text, translate_quiz, translate_flashcards
    TTS_AVAILABLE = True
except:
    TTS_AVAILABLE = False
    LANGUAGE_CODES = {"English": "en"}

# ── YouTube API Import with fallback ──────────────────────────────────────
try:
    from youtube_api import (
        search_youtube_videos, get_educational_links,
        get_subject_category, get_performance_insights,
        get_study_schedule
    )
    YOUTUBE_AVAILABLE = True
except Exception as e:
    YOUTUBE_AVAILABLE = False
    def search_youtube_videos(query, max_results=6): return []
    def get_educational_links(topic): return []
    def get_subject_category(text): return "📚 General Studies"
    def get_performance_insights(results): return {}
    def get_study_schedule(topics, hours=2): return []

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
    font-size: 3em;
    font-weight: 900;
    background: linear-gradient(135deg, #667eea, #f093fb, #f5576c);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin-bottom: 6px;
}

.hero-sub { color: #6b7280; font-size: 1.1em; font-weight: 600; margin-bottom: 24px; }

.feature-card {
    background: white;
    border-radius: 20px;
    padding: 24px;
    margin: 8px 0;
    box-shadow: 0 4px 20px rgba(102,126,234,0.12);
    position: relative;
    overflow: hidden;
    text-align: center;
    transition: all 0.3s ease;
}
.feature-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 5px;
    background: var(--card-color, linear-gradient(90deg,#667eea,#764ba2));
}
.feature-card:hover { transform: translateY(-4px); }
.feature-icon { font-size: 2.5em; margin-bottom: 10px; }
.feature-title { font-size: 1.1em; font-weight: 800; color: #1a1a2e; }
.feature-desc { font-size: 0.88em; color: #6b7280; margin-top: 4px; }

.xp-card {
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 20px; padding: 20px;
    text-align: center; color: white;
}
.xp-number { font-size: 2.5em; font-weight: 900; }
.xp-label { font-size: 0.85em; opacity: 0.85; margin-top: 4px; }

.streak-card {
    background: linear-gradient(135deg, #f5576c, #f093fb);
    border-radius: 20px; padding: 20px;
    text-align: center; color: white;
}

.content-card {
    background: white; border-radius: 16px;
    padding: 20px 24px; margin: 10px 0;
    box-shadow: 0 3px 15px rgba(102,126,234,0.1);
    border-left: 5px solid var(--accent, #667eea);
}

.quiz-card {
    background: white; border-radius: 16px;
    padding: 22px 26px; margin: 14px 0;
    box-shadow: 0 2px 15px rgba(102,126,234,0.1);
    border-left: 5px solid #667eea;
}
.quiz-number {
    font-family: 'Fira Code', monospace;
    font-size: 0.72em; color: #667eea;
    font-weight: 600; letter-spacing: 2px;
    text-transform: uppercase; margin-bottom: 8px;
}
.quiz-question { font-size: 1.1em; font-weight: 700; color: #1a1a2e; line-height: 1.5; }

.badge-correct {
    background: linear-gradient(135deg,#d4edda,#c3e6cb);
    border: 2px solid #28a745; border-radius: 10px;
    padding: 10px 18px; color: #155724;
    font-weight: 800; display: inline-block; margin: 6px 0;
}
.badge-wrong {
    background: linear-gradient(135deg,#f8d7da,#f5c6cb);
    border: 2px solid #dc3545; border-radius: 10px;
    padding: 10px 18px; color: #721c24;
    font-weight: 800; display: inline-block; margin: 6px 0;
}
.explanation-box {
    background: linear-gradient(135deg,#e8f4fd,#d1ecf1);
    border-left: 4px solid #17a2b8;
    border-radius: 0 10px 10px 0;
    padding: 12px 16px; color: #0c5460;
    font-size: 0.92em; margin-top: 10px; font-weight: 600;
}
.hint-box {
    background: linear-gradient(135deg,#fff3cd,#ffeeba);
    border-left: 4px solid #ffc107;
    border-radius: 0 10px 10px 0;
    padding: 10px 14px; color: #856404;
    font-size: 0.88em; margin-top: 6px; font-weight: 600;
}
.score-display {
    background: linear-gradient(135deg,#667eea,#764ba2);
    border-radius: 24px; padding: 40px;
    text-align: center;
    box-shadow: 0 10px 40px rgba(102,126,234,0.35);
}
.score-number { font-size: 5em; font-weight: 900; color: white; line-height: 1; }
.score-label { color: rgba(255,255,255,0.8); font-size: 1.1em; font-weight: 600; margin-top: 10px; }

.fc-front {
    background: linear-gradient(135deg,#667eea,#764ba2);
    border-radius: 24px; padding: 45px 35px;
    text-align: center; font-size: 1.4em; font-weight: 800;
    color: white; min-height: 180px;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 15px 50px rgba(102,126,234,0.3);
}
.fc-back {
    background: linear-gradient(135deg,#11998e,#38ef7d);
    border-radius: 24px; padding: 45px 35px;
    text-align: center; font-size: 1.1em; font-weight: 700;
    color: white; min-height: 180px;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 15px 50px rgba(17,153,142,0.25); margin-top: 16px;
}

.conf-know {
    background: linear-gradient(135deg,#28a745,#20c997);
    border-radius: 14px; padding: 14px;
    text-align: center; color: white; font-weight: 800;
}
.conf-almost {
    background: linear-gradient(135deg,#ffc107,#fd7e14);
    border-radius: 14px; padding: 14px;
    text-align: center; color: white; font-weight: 800;
}
.conf-noidea {
    background: linear-gradient(135deg,#dc3545,#c82333);
    border-radius: 14px; padding: 14px;
    text-align: center; color: white; font-weight: 800;
}

.chat-user {
    background: linear-gradient(135deg,#667eea,#764ba2);
    border-radius: 20px 20px 6px 20px;
    padding: 16px 20px; margin: 12px 0; color: white;
}
.chat-ai {
    background: white; border: 2px solid #e8e8ff;
    border-radius: 20px 20px 20px 6px;
    padding: 16px 20px; margin: 12px 0; color: #1a1a2e;
}
.chat-label {
    font-size: 0.72em; font-weight: 800;
    letter-spacing: 2px; text-transform: uppercase;
    margin-bottom: 6px; opacity: 0.75;
}

.stat-card {
    background: white; border-radius: 20px;
    padding: 28px; text-align: center;
    box-shadow: 0 4px 20px rgba(102,126,234,0.1);
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

.doc-loaded {
    background: rgba(255,255,255,0.2);
    border: 2px solid rgba(255,255,255,0.4);
    border-radius: 14px; padding: 14px; margin: 8px 0;
}
.doc-not-loaded {
    background: rgba(0,0,0,0.15);
    border: 2px solid rgba(255,255,255,0.2);
    border-radius: 14px; padding: 14px; margin: 8px 0;
}

.badge-easy {
    background: linear-gradient(135deg,#d4edda,#c3e6cb);
    border: 2px solid #28a745; border-radius: 20px;
    padding: 4px 14px; color: #155724;
    font-weight: 800; font-size: 0.85em; display: inline-block;
}
.badge-medium {
    background: linear-gradient(135deg,#fff3cd,#ffeeba);
    border: 2px solid #ffc107; border-radius: 20px;
    padding: 4px 14px; color: #856404;
    font-weight: 800; font-size: 0.85em; display: inline-block;
}
.badge-hard {
    background: linear-gradient(135deg,#f8d7da,#f5c6cb);
    border: 2px solid #dc3545; border-radius: 20px;
    padding: 4px 14px; color: #721c24;
    font-weight: 800; font-size: 0.85em; display: inline-block;
}

.timer-box {
    background: linear-gradient(135deg,#667eea,#764ba2);
    border-radius: 16px; padding: 16px 24px;
    text-align: center; color: white; margin: 12px 0;
    font-size: 1.5em; font-weight: 900;
    font-family: 'Fira Code', monospace;
}
.timer-warning {
    background: linear-gradient(135deg,#f5576c,#f093fb);
    border-radius: 16px; padding: 16px 24px;
    text-align: center; color: white; margin: 12px 0;
    font-size: 1.5em; font-weight: 900;
    font-family: 'Fira Code', monospace;
}

.step-card {
    background: white; border-radius: 16px;
    padding: 18px 20px; margin: 8px 0;
    box-shadow: 0 3px 15px rgba(102,126,234,0.1);
    display: flex; align-items: center; gap: 14px;
}
.step-number {
    background: linear-gradient(135deg,#667eea,#764ba2);
    color: white; width: 38px; height: 38px;
    border-radius: 50%; display: flex;
    align-items: center; justify-content: center;
    font-weight: 900; font-size: 1em; flex-shrink: 0;
}

.nav-brand { font-size: 1.5em; font-weight: 900; color: white; }
.nav-sub { font-size: 0.85em; color: rgba(255,255,255,0.7); font-weight: 600; }

.stProgress > div > div {
    background: linear-gradient(90deg,#667eea,#f093fb) !important;
    border-radius: 10px !important;
}
.stButton > button {
    border-radius: 12px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1em !important;
    transition: all 0.2s ease !important;
    border: none !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg,#667eea,#764ba2) !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(102,126,234,0.4) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(102,126,234,0.5) !important;
}
[data-testid="metric-container"] {
    background: white !important;
    border-radius: 16px !important;
    padding: 20px !important;
    box-shadow: 0 4px 15px rgba(102,126,234,0.1) !important;
}
hr { border-color: rgba(102,126,234,0.15) !important; }
</style>
""", unsafe_allow_html=True)

# ── Helper: Home Button ───────────────────────────────────────────────────
def home_button():
    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("🏠 Home", key=f"home_{page}", use_container_width=True):
            st.query_params["page"] = "🏠 Home"
            st.rerun()

# ── Session State ─────────────────────────────────────────────────────────
defaults = {
    "doc_text": "", "doc_name": "", "doc_id": None,
    "quiz_questions": [], "quiz_answers": [],
    "quiz_submitted": False, "quiz_score": 0, "quiz_id": None,
    "quiz_type": "MCQ", "quiz_difficulty": "Medium",
    "tf_questions": [], "tf_answers": [], "tf_submitted": False, "tf_score": 0,
    "fb_questions": [], "fb_answers": [], "fb_submitted": False, "fb_score": 0,
    "flashcards": [], "fc_index": 0, "fc_flipped": False,
    "fc_confidence": [],
    "chat_history": [],
    "selected_lang": "English",
    "timer_active": False, "timer_start": None,
    "timer_duration": 600, "timer_expired": False,
    "study_content": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

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
    default_page = st.query_params.get("page", "🏠 Home")
    default_idx = pages.index(default_page) if default_page in pages else 0
    page = st.radio("Navigation", pages, index=default_idx,
                    label_visibility="collapsed")

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
    st.markdown('<div class="hero-title">Learn Smarter,<br>Not Harder! 🚀</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Upload any document → AI generates quizzes, flashcards, study notes & more ✨</div>',
                unsafe_allow_html=True)

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    cards_data = [
        ("📤", "Upload", "PDF, TXT, DOCX", "linear-gradient(90deg,#667eea,#764ba2)", "📤 Upload Document"),
        ("📝", "Quiz", "MCQ, T/F, Fill Blanks", "linear-gradient(90deg,#f093fb,#f5576c)", "📝 Generate Quiz"),
        ("🃏", "Flashcards", "Smart confidence", "linear-gradient(90deg,#4facfe,#00f2fe)", "🃏 Flashcards"),
        ("📚", "Study Notes", "AI summary+mind map", "linear-gradient(90deg,#43e97b,#38f9d7)", "📚 Study Content"),
        ("🎥", "Resources", "YouTube+Study sites", "linear-gradient(90deg,#ff512f,#dd2476)", "🎥 Resources"),
        ("📊", "Progress", "XP+streaks+stats", "linear-gradient(90deg,#fa709a,#fee140)", "📊 Progress"),
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
            if st.button("Open", key=f"nav_{title}",
                        use_container_width=True, type="primary"):
                st.query_params["page"] = target
                st.rerun()

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🚀 How it works")
        for num, icon, text in [
            ("1", "📤", "Upload PDF, TXT or DOCX file"),
            ("2", "📚", "Get AI study notes instantly"),
            ("3", "📝", "Take quiz with difficulty levels"),
            ("4", "🃏", "Review flashcards with confidence"),
            ("5", "🎥", "Find YouTube videos and resources"),
            ("6", "📊", "Track XP streaks and progress"),
        ]:
            st.markdown(f"""
            <div class="step-card">
                <div class="step-number">{num}</div>
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
            <div class="xp-label">Level {level} Scholar</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress((total_xp % 100) / 100)
        st.caption(f"{total_xp % 100}/100 XP to Level {level+1}")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="streak-card">
                <div style="font-size:2em;font-weight:900">🔥 {streak}</div>
                <div style="font-size:0.85em;opacity:0.85">Day Streak</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#4facfe,#00f2fe);
                        border-radius:20px;padding:20px;text-align:center;color:white">
                <div style="font-size:2em;font-weight:900">📝 {len(results)}</div>
                <div style="font-size:0.85em;opacity:0.85">Quizzes Done</div>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# UPLOAD
# ═══════════════════════════════════════════════════════════════════════════
elif page == "📤 Upload Document":
    home_button()
    st.markdown('<div class="hero-title">📤 Upload Document</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Supports PDF, TXT and DOCX files</div>', unsafe_allow_html=True)
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="feature-card" style="--card-color:linear-gradient(90deg,#667eea,#764ba2)">
            <div class="feature-icon">📄</div>
            <div class="feature-title">PDF Files</div>
            <div class="feature-desc">Textbooks, papers, articles</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feature-card" style="--card-color:linear-gradient(90deg,#f093fb,#f5576c)">
            <div class="feature-icon">📝</div>
            <div class="feature-title">TXT Files</div>
            <div class="feature-desc">Notes, transcripts, content</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="feature-card" style="--card-color:linear-gradient(90deg,#43e97b,#38f9d7)">
            <div class="feature-icon">📘</div>
            <div class="feature-title">DOCX Files</div>
            <div class="feature-desc">Word documents, assignments</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    uploaded = st.file_uploader("Drop file here", type=["pdf","txt","docx"],
                                label_visibility="collapsed")

    if uploaded:
        with st.spinner("⚙️ Processing your document..."):
            try:
                text = process_file(uploaded)
                chunks = chunk_text(text)
                st.session_state["doc_text"] = text
                st.session_state["doc_name"] = uploaded.name
                st.session_state["study_content"] = None
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

                with st.expander("👀 Preview content"):
                    st.code(text[:1000], language=None)
                st.success(f"✅ '{uploaded.name}' loaded!")

                st.markdown("### What would you like to do?")
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
                    if st.button("🎥 Resources", use_container_width=True, type="primary"):
                        st.query_params["page"] = "🎥 Resources"
                        st.rerun()
                with c5:
                    if st.button("💬 Chat", use_container_width=True, type="primary"):
                        st.query_params["page"] = "💬 Chat with Doc"
                        st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")

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
            <div style="background:linear-gradient(135deg,#667eea,#764ba2);
                        border-radius:16px;padding:20px 24px;color:white;
                        font-size:1.2em;font-weight:700;text-align:center;margin-bottom:16px">
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
                <div style="background:white;border-radius:12px;padding:12px 16px;
                            margin:6px 0;box-shadow:0 2px 10px rgba(102,126,234,0.1);
                            border-left:4px solid #667eea">
                    <b style="color:#667eea">{i}.</b> {point}
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown("### 📝 Exam Tips")
            for tip in content.get("exam_tips",[]):
                st.markdown(f"""
                <div style="background:white;border-radius:12px;padding:12px 16px;
                            margin:6px 0;box-shadow:0 2px 10px rgba(102,126,234,0.1);
                            border-left:4px solid #f093fb">
                    ✅ {tip}
                </div>
                """, unsafe_allow_html=True)

            st.markdown("### 📖 Key Terms")
            for term in content.get("difficult_terms",[]):
                st.markdown(f"""
                <div style="background:white;border-radius:12px;padding:12px 16px;
                            margin:6px 0;box-shadow:0 2px 10px rgba(102,126,234,0.1);
                            border-left:4px solid #43e97b">
                    <b style="color:#11998e">{term.get("term","")}</b>: {term.get("definition","")}
                </div>
                """, unsafe_allow_html=True)

        st.markdown("### 🗺️ Mind Map")
        mind_map = content.get("mind_map",{})
        for main_topic, subtopics in mind_map.items():
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#667eea,#764ba2);
                        border-radius:14px;padding:14px 20px;color:white;
                        font-weight:800;font-size:1.1em;margin:8px 0">
                🧠 {main_topic}
            </div>
            """, unsafe_allow_html=True)
            cols = st.columns(min(len(subtopics), 3))
            for i, sub in enumerate(subtopics):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div style="background:white;border-radius:10px;padding:10px 14px;
                                margin:4px 0;box-shadow:0 2px 10px rgba(102,126,234,0.1);
                                border-left:3px solid #667eea;font-size:0.9em">
                        → {sub}
                    </div>
                    """, unsafe_allow_html=True)

        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("📝 Take Quiz", use_container_width=True, type="primary"):
                st.query_params["page"] = "📝 Generate Quiz"
                st.rerun()
        with c2:
            if st.button("🃏 Flashcards", use_container_width=True, type="primary"):
                st.query_params["page"] = "🃏 Flashcards"
                st.rerun()
        with c3:
            if st.button("🎥 Resources", use_container_width=True, type="primary"):
                st.query_params["page"] = "🎥 Resources"
                st.rerun()
        with c4:
            if st.button("💬 Chat", use_container_width=True, type="primary"):
                st.query_params["page"] = "💬 Chat with Doc"
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# QUIZ
# ═══════════════════════════════════════════════════════════════════════════
elif page == "📝 Generate Quiz":
    home_button()
    st.markdown('<div class="hero-title">📝 Quiz Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Choose your quiz type and difficulty level</div>',
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
        ["MCQ", "True/False", "Fill Blanks"],
        ["🔘", "✅", "✏️"],
        ["Multiple Choice", "True or False", "Complete the sentence"]
    ):
        with col:
            selected = st.session_state["quiz_type"] == qtype
            st.markdown(f"""
            <div style="background:white;border-radius:16px;padding:20px;
                        text-align:center;box-shadow:0 3px 15px rgba(102,126,234,0.1);
                        border:3px solid {'#667eea' if selected else 'transparent'}">
                <div style="font-size:2em">{icon}</div>
                <div style="font-weight:800;margin-top:6px">{qtype}</div>
                <div style="color:#6b7280;font-size:0.85em">{desc}</div>
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
    st.markdown("### ⚙️ Settings")
    col1, col2, col3, col4 = st.columns([2,2,2,1])
    with col1:
        num_q = st.slider("Questions", 3, 15, 5)
    with col2:
        difficulty = st.selectbox("🎯 Difficulty", ["Easy","Medium","Hard"], index=1)
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

                st.success(f"✅ {num_q} {qtype} questions ready!")
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
        try:
            save_quiz_result(st.session_state["quiz_id"] or 1, score, total, qtype, diff)
        except:
            pass
        xp_earned = score * 10
        st.markdown(f"""
        <div class="score-display">
            <div class="score-number">{pct:.0f}%</div>
            <div class="score-label">🎯 {score}/{total} correct · {diff} · +{xp_earned} XP!</div>
        </div>
        """, unsafe_allow_html=True)
        if pct >= 80:
            st.balloons()
        st.write("")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🏠 Back to Home", use_container_width=True,
                        type="primary", key="score_home"):
                st.query_params["page"] = "🏠 Home"
                st.rerun()
        with c2:
            if st.button("📊 View Progress", use_container_width=True,
                        key="score_progress"):
                st.query_params["page"] = "📊 Progress"
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
                <div style="display:flex;justify-content:space-between">
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
    st.markdown('<div class="hero-sub">Rate your confidence to earn XP and track weak areas</div>',
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
                try:
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
                    if st.button("😎 Know it!\n+15 XP", use_container_width=True, key="conf_know"):
                        st.session_state["fc_confidence"][idx] = "Know it"
                        save_flashcard_confidence(card["front"], "Know it")
                        if idx < len(cards)-1:
                            st.session_state["fc_index"] += 1
                            st.session_state["fc_flipped"] = False
                        st.rerun()
                with c2:
                    if st.button("🤔 Almost\n+8 XP", use_container_width=True, key="conf_almost"):
                        st.session_state["fc_confidence"][idx] = "Almost"
                        save_flashcard_confidence(card["front"], "Almost")
                        if idx < len(cards)-1:
                            st.session_state["fc_index"] += 1
                            st.session_state["fc_flipped"] = False
                        st.rerun()
                with c3:
                    if st.button("😅 No idea\n+3 XP", use_container_width=True, key="conf_noidea"):
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
    st.markdown('<div class="hero-sub">YouTube videos + free educational websites for your topic</div>',
                unsafe_allow_html=True)
    st.divider()

    try:
        if st.session_state["doc_text"]:
            subject = get_subject_category(st.session_state["doc_text"])
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#667eea,#764ba2);
                        border-radius:14px;padding:14px 20px;color:white;
                        font-weight:700;font-size:1.1em;margin-bottom:16px">
                📂 Detected Subject: {subject}
            </div>
            """, unsafe_allow_html=True)
            default_topic = st.session_state["doc_name"].replace(".pdf","").replace(".txt","").replace(".docx","")
        else:
            default_topic = ""
    except:
        default_topic = ""

    topic = st.text_input(
        "🔍 Search topic",
        value=default_topic,
        placeholder="e.g. Machine Learning, Photosynthesis, World War 2...",
        label_visibility="collapsed"
    )

    col1, col2 = st.columns(2)
    with col1:
        search_videos = st.button("🎥 Find YouTube Videos", type="primary", use_container_width=True)
    with col2:
        search_links = st.button("🌐 Find Study Websites", use_container_width=True)

    st.divider()

    if search_videos and topic:
        with st.spinner("🔍 Searching YouTube..."):
            try:
                videos = search_youtube_videos(f"{topic} education tutorial", max_results=6)
            except Exception as e:
                st.error(f"Search error: {e}")
                videos = []

        if videos:
            st.markdown("### 🎥 YouTube Videos")
            col1, col2 = st.columns(2)
            for i, video in enumerate(videos):
                with col1 if i % 2 == 0 else col2:
                    st.markdown(f"""
                    <div style="background:white;border-radius:16px;padding:16px;
                                margin:8px 0;box-shadow:0 3px 15px rgba(102,126,234,0.1);
                                border-left:5px solid #ff0000">
                        <div style="font-weight:800;color:#1a1a2e;font-size:0.95em;
                                    margin-bottom:6px">{video['title']}</div>
                        <div style="color:#6b7280;font-size:0.82em;margin-bottom:8px">
                            📺 {video['channel']} · ⏱️ {video['duration']} · 👁️ {video['views']}
                        </div>
                        <a href="{video['url']}" target="_blank"
                           style="background:linear-gradient(135deg,#ff0000,#cc0000);
                                  color:white;padding:6px 14px;border-radius:8px;
                                  text-decoration:none;font-weight:700;font-size:0.85em">
                            ▶️ Watch on YouTube
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("No videos found. Try a different search term!")

    if search_links and topic:
        st.markdown("### 🌐 Free Educational Websites")
        try:
            links = get_educational_links(topic)
        except Exception as e:
            st.error(f"Links error: {e}")
            links = []

        if links:
            col1, col2, col3 = st.columns(3)
            for i, link in enumerate(links):
                with [col1, col2, col3][i % 3]:
                    st.markdown(f"""
                    <div style="background:white;border-radius:16px;padding:20px;
                                margin:8px 0;box-shadow:0 3px 15px rgba(102,126,234,0.1);
                                border-top:5px solid {link['color']};text-align:center">
                        <div style="font-weight:800;color:#1a1a2e;font-size:1em;
                                    margin-bottom:6px">{link['name']}</div>
                        <div style="color:#6b7280;font-size:0.82em;margin-bottom:12px">
                            {link['desc']}
                        </div>
                        <a href="{link['url']}" target="_blank"
                           style="background:{link['color']};
                                  color:white;padding:8px 16px;border-radius:8px;
                                  text-decoration:none;font-weight:700;font-size:0.85em">
                            🔗 Visit Now
                        </a>
                    </div>
                    """, unsafe_allow_html=True)

    if not topic:
        st.markdown("""
        <div style="background:white;border-radius:16px;padding:30px;
                    text-align:center;box-shadow:0 3px 15px rgba(102,126,234,0.1)">
            <div style="font-size:3em">🎥</div>
            <div style="font-weight:800;font-size:1.2em;margin:10px 0">Search any topic!</div>
            <div style="color:#6b7280">Find free YouTube videos and educational websites instantly</div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# CHAT
# ═══════════════════════════════════════════════════════════════════════════
elif page == "💬 Chat with Doc":
    home_button()
    st.markdown('<div class="hero-title">💬 Chat with Doc</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Ask anything — answers come from your document</div>',
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
        st.markdown(f'<div class="chat-ai"><div class="chat-label">🤖 AI</div>{h["assistant"]}</div>', unsafe_allow_html=True)
        if TTS_AVAILABLE:
            try:
                lang_code = LANGUAGE_CODES[st.session_state["selected_lang"]]
                audio = text_to_speech(h["assistant"], lang_code)
                if audio:
                    st.markdown(get_audio_html(audio), unsafe_allow_html=True)
            except:
                pass

    question = st.chat_input("Ask anything about your document...")
    if question:
        with st.spinner("🤔 Thinking..."):
            try:
                answer = chat_with_doc(st.session_state["doc_text"], question,
                                      st.session_state["chat_history"])
                if TTS_AVAILABLE and st.session_state["selected_lang"] != "English":
                    try:
                        lang_code = LANGUAGE_CODES[st.session_state["selected_lang"]]
                        answer = translate_text(answer, lang_code)
                    except:
                        pass
                st.session_state["chat_history"].append({"user": question, "assistant": answer})
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")

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
    st.markdown('<div class="hero-sub">Track XP, streaks, scores and confidence</div>',
                unsafe_allow_html=True)
    st.divider()

    total_xp = get_total_xp()
    streak = get_streak_count()
    results = get_quiz_results()
    level = total_xp // 100 + 1
    conf_stats = get_flashcard_confidence_stats()

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
    st.markdown(f"### ⚡ Level {level} Progress")
    st.progress((total_xp % 100) / 100)
    st.caption(f"{total_xp % 100}/100 XP to reach Level {level+1}")

    try:
        if results:
            insights = get_performance_insights(results)
            if insights:
                st.divider()
                st.markdown("### 💡 Performance Insights")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"""
                    <div style="background:white;border-radius:14px;padding:16px;
                                text-align:center;box-shadow:0 3px 15px rgba(102,126,234,0.1)">
                        <div style="font-size:0.85em;color:#6b7280">📈 Trend</div>
                        <div style="font-weight:800;font-size:1.1em">{insights.get("trend","")}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                    <div style="background:white;border-radius:14px;padding:16px;
                                text-align:center;box-shadow:0 3px 15px rgba(102,126,234,0.1)">
                        <div style="font-size:0.85em;color:#6b7280">🏆 Best Score</div>
                        <div style="font-weight:800;font-size:1.1em;color:#28a745">{insights.get("best_score",0):.0f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                with c3:
                    st.markdown(f"""
                    <div style="background:white;border-radius:14px;padding:16px;
                                text-align:center;box-shadow:0 3px 15px rgba(102,126,234,0.1)">
                        <div style="font-size:0.85em;color:#6b7280">📊 Average</div>
                        <div style="font-weight:800;font-size:1.1em;color:#667eea">{insights.get("avg_score",0):.0f}%</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("### 📋 Recommendations")
                for rec in insights.get("recommendations", []):
                    st.markdown(f"""
                    <div style="background:white;border-radius:12px;padding:12px 16px;
                                margin:6px 0;box-shadow:0 2px 10px rgba(102,126,234,0.1);
                                border-left:4px solid #667eea">
                        {rec}
                    </div>
                    """, unsafe_allow_html=True)
    except:
        pass

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📝 Recent Quiz Results")
        if not results:
            st.info("No quizzes taken yet!")
            if st.button("📝 Take a Quiz", type="primary"):
                st.query_params["page"] = "📝 Generate Quiz"
                st.rerun()
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
                        <span style='font-size:1.3em'>{emoji}</span>
                        <b style='color:#1a1a2e;margin-left:6px'>{r[3][:20]}</b>
                        <span style='background:#f0f4ff;border-radius:8px;padding:2px 8px;
                                    font-size:0.75em;margin-left:6px;color:#667eea'>{qtype}</span>
                        <span style='background:#fff0f7;border-radius:8px;padding:2px 8px;
                                    font-size:0.75em;margin-left:4px;color:#f5576c'>{diff}</span>
                    </div>
                    <b style='color:{color};font-size:1.2em'>{pct:.0f}%</b>
                </div>
                <div style='color:#6b7280;font-size:0.8em;margin-top:4px'>
                    {r[0][:16]} · {r[1]}/{r[2]} correct
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 🃏 Flashcard Confidence")
        total_cards = sum(conf_stats.values()) if conf_stats else 0
        if total_cards == 0:
            st.info("Review flashcards to see confidence stats!")
        else:
            for label, icon, color in [
                ("Know it","😎","#28a745"),
                ("Almost","🤔","#ffc107"),
                ("No idea","😅","#dc3545")
            ]:
                count = conf_stats.get(label, 0)
                pct = count/total_cards*100 if total_cards > 0 else 0
                st.markdown(f"""
                <div style='background:white;border-radius:12px;padding:14px 18px;
                            margin:8px 0;box-shadow:0 3px 15px rgba(102,126,234,0.1);
                            border-left:5px solid {color}'>
                    <div style='display:flex;justify-content:space-between'>
                        <span>{icon} {label}</span>
                        <b style='color:{color}'>{count} ({pct:.0f}%)</b>
                    </div>
                    <div style='background:#f0f0f0;border-radius:8px;height:8px;margin-top:8px'>
                        <div style='background:{color};height:8px;border-radius:8px;width:{pct}%'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("### 📅 Study Activity")
        streak_data = get_study_streak()
        if streak_data:
            for study_date, xp in streak_data[:7]:
                st.markdown(f"""
                <div style='background:white;border-radius:10px;padding:10px 16px;
                            margin:4px 0;box-shadow:0 2px 10px rgba(102,126,234,0.08);
                            display:flex;justify-content:space-between'>
                    <span style='color:#6b7280'>📅 {study_date}</span>
                    <span style='color:#667eea;font-weight:800'>+{xp} XP</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Start studying to build your streak!")