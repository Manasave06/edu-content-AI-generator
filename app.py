import streamlit as st
import sys
import os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from processor import process_file, chunk_text
from generator import (
    generate_quiz, generate_flashcards, chat_with_doc,
    generate_true_false, generate_fill_blanks
)
from database import (
    init_db, save_document, save_quiz,
    save_flashcards, save_quiz_result,
    get_all_documents, get_quiz_results
)

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
    transition: all 0.2s !important;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.25) !important;
}

.hero-title {
    font-size: 3.2em;
    font-weight: 900;
    background: linear-gradient(135deg, #667eea, #f093fb, #f5576c);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin-bottom: 6px;
}

.hero-sub {
    color: #6b7280;
    font-size: 1.15em;
    font-weight: 600;
    margin-bottom: 28px;
}

.feature-card {
    background: white;
    border-radius: 20px;
    padding: 28px 24px;
    margin: 8px 0;
    box-shadow: 0 4px 20px rgba(102,126,234,0.12);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    text-align: center;
}

.feature-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 5px;
    background: var(--card-color, linear-gradient(90deg, #667eea, #764ba2));
}

.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(102,126,234,0.2);
}

.feature-icon { font-size: 2.8em; margin-bottom: 12px; }
.feature-title { font-size: 1.2em; font-weight: 800; color: #1a1a2e; }
.feature-desc { font-size: 0.9em; color: #6b7280; margin-top: 6px; line-height: 1.5; }

/* Difficulty badges */
.badge-easy {
    background: linear-gradient(135deg, #d4edda, #c3e6cb);
    border: 2px solid #28a745;
    border-radius: 20px;
    padding: 4px 14px;
    color: #155724;
    font-weight: 800;
    font-size: 0.85em;
    display: inline-block;
}

.badge-medium {
    background: linear-gradient(135deg, #fff3cd, #ffeeba);
    border: 2px solid #ffc107;
    border-radius: 20px;
    padding: 4px 14px;
    color: #856404;
    font-weight: 800;
    font-size: 0.85em;
    display: inline-block;
}

.badge-hard {
    background: linear-gradient(135deg, #f8d7da, #f5c6cb);
    border: 2px solid #dc3545;
    border-radius: 20px;
    padding: 4px 14px;
    color: #721c24;
    font-weight: 800;
    font-size: 0.85em;
    display: inline-block;
}

/* Quiz type tabs */
.quiz-type-card {
    background: white;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 3px 15px rgba(102,126,234,0.1);
    border: 3px solid transparent;
    cursor: pointer;
    transition: all 0.2s;
}

.quiz-type-card:hover {
    border-color: #667eea;
    transform: translateY(-2px);
}

.quiz-type-icon { font-size: 2em; margin-bottom: 8px; }
.quiz-type-title { font-weight: 800; color: #1a1a2e; font-size: 1em; }
.quiz-type-desc { color: #6b7280; font-size: 0.8em; margin-top: 4px; }

.quiz-card {
    background: white;
    border-radius: 16px;
    padding: 22px 26px;
    margin: 14px 0;
    box-shadow: 0 2px 15px rgba(102,126,234,0.1);
    border-left: 5px solid #667eea;
}

.quiz-number {
    font-family: 'Fira Code', monospace;
    font-size: 0.72em;
    color: #667eea;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.quiz-question {
    font-size: 1.1em;
    font-weight: 700;
    color: #1a1a2e;
    line-height: 1.5;
}

.badge-correct {
    background: linear-gradient(135deg, #d4edda, #c3e6cb);
    border: 2px solid #28a745;
    border-radius: 10px;
    padding: 10px 18px;
    color: #155724;
    font-weight: 800;
    display: inline-block;
    margin: 6px 0;
}

.badge-wrong {
    background: linear-gradient(135deg, #f8d7da, #f5c6cb);
    border: 2px solid #dc3545;
    border-radius: 10px;
    padding: 10px 18px;
    color: #721c24;
    font-weight: 800;
    display: inline-block;
    margin: 6px 0;
}

.explanation-box {
    background: linear-gradient(135deg, #e8f4fd, #d1ecf1);
    border-left: 4px solid #17a2b8;
    border-radius: 0 10px 10px 0;
    padding: 12px 16px;
    color: #0c5460;
    font-size: 0.92em;
    margin-top: 10px;
    font-weight: 600;
}

.hint-box {
    background: linear-gradient(135deg, #fff3cd, #ffeeba);
    border-left: 4px solid #ffc107;
    border-radius: 0 10px 10px 0;
    padding: 10px 14px;
    color: #856404;
    font-size: 0.88em;
    margin-top: 6px;
    font-weight: 600;
}

.score-display {
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 24px;
    padding: 40px;
    text-align: center;
    box-shadow: 0 10px 40px rgba(102,126,234,0.35);
}

.score-number {
    font-size: 5em;
    font-weight: 900;
    color: white;
    line-height: 1;
}

.score-label {
    color: rgba(255,255,255,0.8);
    font-size: 1.1em;
    font-weight: 600;
    margin-top: 10px;
}

.fc-front {
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 24px;
    padding: 45px 35px;
    text-align: center;
    font-size: 1.4em;
    font-weight: 800;
    color: white;
    min-height: 180px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 15px 50px rgba(102,126,234,0.3);
}

.fc-back {
    background: linear-gradient(135deg, #11998e, #38ef7d);
    border-radius: 24px;
    padding: 45px 35px;
    text-align: center;
    font-size: 1.1em;
    font-weight: 700;
    color: white;
    min-height: 180px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 15px 50px rgba(17,153,142,0.25);
    margin-top: 16px;
}

.chat-user {
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 20px 20px 6px 20px;
    padding: 16px 20px;
    margin: 12px 0;
    color: white;
    box-shadow: 0 4px 15px rgba(102,126,234,0.25);
}

.chat-ai {
    background: white;
    border: 2px solid #e8e8ff;
    border-radius: 20px 20px 20px 6px;
    padding: 16px 20px;
    margin: 12px 0;
    color: #1a1a2e;
    box-shadow: 0 4px 15px rgba(0,0,0,0.06);
}

.chat-label {
    font-size: 0.72em;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 6px;
    opacity: 0.75;
}

.stat-card {
    background: white;
    border-radius: 20px;
    padding: 28px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(102,126,234,0.1);
}

.stat-number {
    font-size: 3em;
    font-weight: 900;
    background: linear-gradient(135deg, #667eea, #f093fb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stat-label {
    color: #6b7280;
    font-size: 0.9em;
    font-weight: 700;
    margin-top: 6px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.doc-loaded {
    background: linear-gradient(135deg, rgba(255,255,255,0.25), rgba(255,255,255,0.15));
    border: 2px solid rgba(255,255,255,0.4);
    border-radius: 14px;
    padding: 14px 16px;
    margin: 8px 0;
}

.doc-not-loaded {
    background: rgba(0,0,0,0.15);
    border: 2px solid rgba(255,255,255,0.2);
    border-radius: 14px;
    padding: 14px 16px;
    margin: 8px 0;
}

.stProgress > div > div {
    background: linear-gradient(90deg, #667eea, #f093fb) !important;
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
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
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
    border: none !important;
}

hr { border-color: rgba(102,126,234,0.15) !important; }

.nav-brand { font-size: 1.5em; font-weight: 900; color: white; }
.nav-sub { font-size: 0.85em; color: rgba(255,255,255,0.7); font-weight: 600; }

.step-card {
    background: white;
    border-radius: 16px;
    padding: 20px;
    margin: 8px 0;
    box-shadow: 0 3px 15px rgba(102,126,234,0.1);
    display: flex;
    align-items: center;
    gap: 16px;
}

.step-number {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    width: 40px; height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 1.1em;
    flex-shrink: 0;
}

.timer-box {
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 16px;
    padding: 16px 24px;
    text-align: center;
    color: white;
    margin: 12px 0;
    font-size: 1.5em;
    font-weight: 900;
    font-family: 'Fira Code', monospace;
}

.timer-warning {
    background: linear-gradient(135deg, #f5576c, #f093fb);
    border-radius: 16px;
    padding: 16px 24px;
    text-align: center;
    color: white;
    margin: 12px 0;
    font-size: 1.5em;
    font-weight: 900;
    font-family: 'Fira Code', monospace;
}

.fill-blank-input {
    background: white;
    border: 3px solid #667eea;
    border-radius: 12px;
    padding: 10px 16px;
    font-size: 1em;
    font-weight: 700;
    width: 100%;
    margin: 8px 0;
}
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────
defaults = {
    "doc_text": "", "doc_name": "", "doc_id": None,
    "quiz_questions": [], "quiz_answers": [],
    "quiz_submitted": False, "quiz_score": 0, "quiz_id": None,
    "quiz_type": "MCQ",
    "quiz_difficulty": "Medium",
    "tf_questions": [], "tf_answers": [], "tf_submitted": False, "tf_score": 0,
    "fb_questions": [], "fb_answers": [], "fb_submitted": False, "fb_score": 0,
    "flashcards": [], "fc_index": 0, "fc_flipped": False,
    "chat_history": [],
    "selected_lang": "English",
    "timer_active": False,
    "timer_start": None,
    "timer_duration": 600,
    "timer_expired": False,
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
        lang_name = st.selectbox(
            "Language", list(LANGUAGE_CODES.keys()),
            index=0, label_visibility="collapsed"
        )
        st.session_state["selected_lang"] = lang_name
        st.divider()

    pages = [
        "🏠 Home", "📤 Upload Document",
        "📝 Generate Quiz", "🃏 Flashcards",
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
            <div style="font-size:0.7em;font-weight:800;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px">✅ Loaded</div>
            <div style="font-weight:700;font-size:0.95em">{st.session_state["doc_name"]}</div>
            <div style="font-size:0.8em;opacity:0.8;margin-top:2px">{len(st.session_state["doc_text"]):,} characters</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="doc-not-loaded">
            <div style="font-size:0.7em;font-weight:800;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px">⚠️ No Document</div>
            <div style="font-size:0.85em;opacity:0.8">Upload a document first</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    if st.button("🗑️ Clear Everything", use_container_width=True):
        for k, v in defaults.items():
            st.session_state[k] = v
        st.query_params.clear()
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# HOME
# ═══════════════════════════════════════════════════════════════════════════
if page == "🏠 Home":
    st.markdown('<div class="hero-title">Learn Smarter,<br>Not Harder! 🚀</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Upload any document → Quizzes, Flashcards & AI Chat instantly ✨</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    cards_data = [
        ("📤", "Upload Docs", "PDF or TXT files", "linear-gradient(90deg,#667eea,#764ba2)", "📤 Upload Document"),
        ("📝", "AI Quizzes", "MCQ, True/False, Fill blanks", "linear-gradient(90deg,#f093fb,#f5576c)", "📝 Generate Quiz"),
        ("🃏", "Flashcards", "Flip-card study", "linear-gradient(90deg,#4facfe,#00f2fe)", "🃏 Flashcards"),
        ("💬", "AI Chat", "Ask your document anything", "linear-gradient(90deg,#11998e,#38ef7d)", "💬 Chat with Doc"),
    ]
    for col, (icon, title, desc, color, target) in zip([col1,col2,col3,col4], cards_data):
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
        st.markdown("### 📖 How to get started")
        for num, icon, text in [
            ("1","📤","Upload your PDF or TXT document"),
            ("2","🎯","Choose difficulty: Easy, Medium, Hard"),
            ("3","📝","Pick quiz type: MCQ, True/False, Fill Blanks"),
            ("4","📊","Track your progress and improve!")
        ]:
            st.markdown(f"""
            <div class="step-card">
                <div class="step-number">{num}</div>
                <div style="font-size:1.4em">{icon}</div>
                <div style="font-weight:700;color:#1a1a2e">{text}</div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 🎯 Difficulty Levels")
        for level, color, desc in [
            ("🟢 Easy", "#28a745", "Basic recall & simple definitions"),
            ("🟡 Medium", "#ffc107", "Application & cause-effect"),
            ("🔴 Hard", "#dc3545", "Analysis & critical thinking"),
        ]:
            st.markdown(f"""
            <div style="background:white;border-radius:14px;padding:16px 20px;
                        margin:8px 0;box-shadow:0 3px 15px rgba(102,126,234,0.1);
                        border-left:5px solid {color}">
                <div style="font-weight:800;font-size:1.1em">{level}</div>
                <div style="color:#6b7280;font-size:0.9em;margin-top:4px">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### 📝 Quiz Formats")
        for fmt, icon, desc in [
            ("MCQ", "🔘", "Multiple choice questions"),
            ("True/False", "✅", "True or false statements"),
            ("Fill Blanks", "✏️", "Fill in the missing word"),
        ]:
            st.markdown(f"""
            <div style="background:white;border-radius:14px;padding:14px 20px;
                        margin:6px 0;box-shadow:0 3px 15px rgba(102,126,234,0.1)">
                <span style="font-size:1.2em">{icon}</span>
                <b style="margin-left:8px">{fmt}</b>
                <span style="color:#6b7280;font-size:0.88em;margin-left:8px">{desc}</span>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# UPLOAD
# ═══════════════════════════════════════════════════════════════════════════
elif page == "📤 Upload Document":
    st.markdown('<div class="hero-title">📤 Upload Document</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Supports PDF and TXT files up to 200MB</div>', unsafe_allow_html=True)
    st.divider()

    uploaded = st.file_uploader("Drop file here", type=["pdf","txt"],
                                label_visibility="collapsed")
    if uploaded:
        with st.spinner("⚙️ Processing..."):
            try:
                text = process_file(uploaded)
                chunks = chunk_text(text)
                st.session_state["doc_text"] = text
                st.session_state["doc_name"] = uploaded.name
                doc_id = save_document(uploaded.name, text)
                st.session_state["doc_id"] = doc_id

                col1, col2, col3 = st.columns(3)
                col1.metric("📝 Characters", f"{len(text):,}")
                col2.metric("💬 Words", f"{len(text.split()):,}")
                col3.metric("🧩 Chunks", len(chunks))

                with st.expander("👀 Preview content"):
                    st.code(text[:1000], language=None)
                st.success(f"✅ '{uploaded.name}' loaded!")

                st.markdown("### What would you like to do?")
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("📝 Generate Quiz", use_container_width=True, type="primary"):
                        st.query_params["page"] = "📝 Generate Quiz"
                        st.rerun()
                with c2:
                    if st.button("🃏 Flashcards", use_container_width=True, type="primary"):
                        st.query_params["page"] = "🃏 Flashcards"
                        st.rerun()
                with c3:
                    if st.button("💬 Chat with Doc", use_container_width=True, type="primary"):
                        st.query_params["page"] = "💬 Chat with Doc"
                        st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="feature-card" style="--card-color:linear-gradient(90deg,#667eea,#764ba2)">
                <div class="feature-icon">📄</div>
                <div class="feature-title">PDF Files</div>
                <div class="feature-desc">Textbooks, notes, research papers, articles</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="feature-card" style="--card-color:linear-gradient(90deg,#f093fb,#f5576c)">
                <div class="feature-icon">📝</div>
                <div class="feature-title">Text Files</div>
                <div class="feature-desc">Plain .txt files, notes, transcripts</div>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# QUIZ — with MCQ + True/False + Fill Blanks + Difficulty
# ═══════════════════════════════════════════════════════════════════════════
elif page == "📝 Generate Quiz":
    st.markdown('<div class="hero-title">📝 Quiz Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Choose your quiz type and difficulty level</div>', unsafe_allow_html=True)
    st.divider()

    if not st.session_state["doc_text"]:
        st.warning("⚠️ Please upload a document first!")
        if st.button("📤 Go to Upload", type="primary"):
            st.query_params["page"] = "📤 Upload Document"
            st.rerun()
        st.stop()

    # ── Quiz Type Selection ───────────────────────────────────────────────
    st.markdown("### 📋 Select Quiz Type")
    t1, t2, t3 = st.columns(3)
    with t1:
        st.markdown("""
        <div class="quiz-type-card">
            <div class="quiz-type-icon">🔘</div>
            <div class="quiz-type-title">MCQ</div>
            <div class="quiz-type-desc">Multiple Choice Questions</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Select MCQ", use_container_width=True,
                    type="primary" if st.session_state["quiz_type"]=="MCQ" else "secondary",
                    key="sel_mcq"):
            st.session_state["quiz_type"] = "MCQ"
            st.rerun()

    with t2:
        st.markdown("""
        <div class="quiz-type-card">
            <div class="quiz-type-icon">✅</div>
            <div class="quiz-type-title">True / False</div>
            <div class="quiz-type-desc">True or False Statements</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Select True/False", use_container_width=True,
                    type="primary" if st.session_state["quiz_type"]=="True/False" else "secondary",
                    key="sel_tf"):
            st.session_state["quiz_type"] = "True/False"
            st.rerun()

    with t3:
        st.markdown("""
        <div class="quiz-type-card">
            <div class="quiz-type-icon">✏️</div>
            <div class="quiz-type-title">Fill in Blanks</div>
            <div class="quiz-type-desc">Complete the sentence</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Select Fill Blanks", use_container_width=True,
                    type="primary" if st.session_state["quiz_type"]=="Fill Blanks" else "secondary",
                    key="sel_fb"):
            st.session_state["quiz_type"] = "Fill Blanks"
            st.rerun()

    st.markdown(f"**Selected:** `{st.session_state['quiz_type']}`")
    st.divider()

    # ── Settings ──────────────────────────────────────────────────────────
    st.markdown("### ⚙️ Quiz Settings")
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    with col1:
        num_q = st.slider("Number of questions", 3, 15, 5)
    with col2:
        difficulty = st.selectbox(
            "🎯 Difficulty",
            ["Easy", "Medium", "Hard"],
            index=1
        )
        st.session_state["quiz_difficulty"] = difficulty
    with col3:
        timer_mins = st.selectbox(
            "⏱️ Timer",
            ["No Timer", "5 mins", "10 mins", "15 mins", "20 mins", "30 mins"]
        )
    with col4:
        st.write("")
        st.write("")
        gen = st.button("⚡ Generate", type="primary", use_container_width=True)

    # Difficulty badge
    badge_class = {"Easy": "badge-easy", "Medium": "badge-medium", "Hard": "badge-hard"}
    st.markdown(f'<span class="{badge_class[difficulty]}">🎯 {difficulty} Level</span>',
                unsafe_allow_html=True)

    if gen:
        with st.spinner(f"🤖 Generating {st.session_state['quiz_type']} quiz ({difficulty})..."):
            try:
                qtype = st.session_state["quiz_type"]

                if qtype == "MCQ":
                    questions = generate_quiz(
                        st.session_state["doc_text"], num_q, difficulty
                    )
                    st.session_state["quiz_questions"] = questions
                    st.session_state["quiz_answers"] = [None] * len(questions)
                    st.session_state["quiz_submitted"] = False
                    st.session_state["quiz_score"] = 0

                elif qtype == "True/False":
                    questions = generate_true_false(
                        st.session_state["doc_text"], num_q, difficulty
                    )
                    st.session_state["tf_questions"] = questions
                    st.session_state["tf_answers"] = [None] * len(questions)
                    st.session_state["tf_submitted"] = False
                    st.session_state["tf_score"] = 0

                elif qtype == "Fill Blanks":
                    questions = generate_fill_blanks(
                        st.session_state["doc_text"], num_q, difficulty
                    )
                    st.session_state["fb_questions"] = questions
                    st.session_state["fb_answers"] = [""] * len(questions)
                    st.session_state["fb_submitted"] = False
                    st.session_state["fb_score"] = 0

                quiz_id = save_quiz(st.session_state["doc_id"] or 1,
                                   st.session_state.get("quiz_questions", []))
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

                st.success(f"✅ {num_q} {qtype} questions ({difficulty}) ready!")
            except Exception as e:
                st.error(f"❌ Failed: {e}")

    # ── Timer ─────────────────────────────────────────────────────────────
    timer_placeholder = st.empty()
    if st.session_state["timer_active"] and not st.session_state.get("quiz_submitted") \
       and not st.session_state.get("tf_submitted") \
       and not st.session_state.get("fb_submitted"):
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
            mins_left = int(remaining // 60)
            secs_left = int(remaining % 60)
            time_str = f"{mins_left:02d}:{secs_left:02d}"
            if remaining <= 60:
                timer_placeholder.markdown(
                    f'<div class="timer-warning">⚠️ Hurry Up! ⏱️ {time_str}</div>',
                    unsafe_allow_html=True)
            else:
                timer_placeholder.markdown(
                    f'<div class="timer-box">⏱️ Time Remaining: {time_str}</div>',
                    unsafe_allow_html=True)
            time.sleep(1)
            st.rerun()

    if st.session_state.get("timer_expired"):
        st.error("⏰ Time's Up! Quiz Auto-Submitted!")

    st.divider()

    # ════════════════════════════════════════════════════════════════════
    # MCQ Questions
    # ════════════════════════════════════════════════════════════════════
    if st.session_state["quiz_type"] == "MCQ" and st.session_state["quiz_questions"]:
        questions = st.session_state["quiz_questions"]
        diff = st.session_state.get("quiz_difficulty", "Medium")
        badge_cls = {"Easy":"badge-easy","Medium":"badge-medium","Hard":"badge-hard"}

        for i, q in enumerate(questions):
            submitted = st.session_state["quiz_submitted"]
            chosen = st.session_state["quiz_answers"][i]
            correct = q["answer"]

            st.markdown(f"""
            <div class="quiz-card">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <div class="quiz-number">Question {i+1} of {len(questions)}</div>
                    <span class="{badge_cls.get(diff,'badge-medium')}">{diff}</span>
                </div>
                <div class="quiz-question">{q["question"]}</div>
            </div>
            """, unsafe_allow_html=True)

            if TTS_AVAILABLE:
                if st.button("🔊", key=f"tts_q{i}", help="Listen"):
                    audio = text_to_speech(q["question"],
                                          LANGUAGE_CODES[st.session_state["selected_lang"]])
                    if audio:
                        st.markdown(get_audio_html(audio, autoplay=True), unsafe_allow_html=True)

            sel = st.radio(f"Q{i+1}", q["options"], index=None,
                          key=f"q{i}", label_visibility="collapsed")
            if sel:
                st.session_state["quiz_answers"][i] = sel

            if submitted:
                if chosen == correct:
                    st.markdown('<div class="badge-correct">✅ Correct!</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="badge-wrong">❌ Correct: {correct}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="explanation-box">💡 {q.get("explanation","")}</div>', unsafe_allow_html=True)
            st.write("")

        st.divider()
        if not st.session_state["quiz_submitted"]:
            if st.button("✅ Submit MCQ", type="primary", use_container_width=True):
                answers = st.session_state["quiz_answers"]
                score = sum(1 for i,q in enumerate(questions) if answers[i]==q["answer"])
                st.session_state["quiz_score"] = score
                st.session_state["quiz_submitted"] = True
                st.session_state["timer_active"] = False
                save_quiz_result(st.session_state["quiz_id"] or 1, score, len(questions))
                if score/len(questions)*100 >= 80:
                    st.balloons()
                st.rerun()
        else:
            pct = st.session_state["quiz_score"]/len(questions)*100
            st.markdown(f"""
            <div class="score-display">
                <div class="score-number">{pct:.0f}%</div>
                <div class="score-label">🎯 {st.session_state["quiz_score"]} out of {len(questions)} correct — {diff} Level</div>
            </div>
            """, unsafe_allow_html=True)
            st.write("")
            if st.button("🔄 Retake", use_container_width=True):
                st.session_state["quiz_answers"] = [None]*len(questions)
                st.session_state["quiz_submitted"] = False
                st.session_state["timer_expired"] = False
                st.rerun()

    # ════════════════════════════════════════════════════════════════════
    # TRUE/FALSE Questions
    # ════════════════════════════════════════════════════════════════════
    elif st.session_state["quiz_type"] == "True/False" and st.session_state["tf_questions"]:
        questions = st.session_state["tf_questions"]
        diff = st.session_state.get("quiz_difficulty","Medium")
        badge_cls = {"Easy":"badge-easy","Medium":"badge-medium","Hard":"badge-hard"}

        for i, q in enumerate(questions):
            submitted = st.session_state["tf_submitted"]
            chosen = st.session_state["tf_answers"][i]
            correct = q["answer"]

            st.markdown(f"""
            <div class="quiz-card" style="border-left-color:#11998e">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <div class="quiz-number">Statement {i+1} of {len(questions)}</div>
                    <span class="{badge_cls.get(diff,'badge-medium')}">{diff}</span>
                </div>
                <div class="quiz-question">{q["question"]}</div>
            </div>
            """, unsafe_allow_html=True)

            sel = st.radio(f"TF{i+1}", ["True", "False"], index=None,
                          key=f"tf{i}", label_visibility="collapsed",
                          horizontal=True)
            if sel:
                st.session_state["tf_answers"][i] = sel

            if submitted:
                if chosen == correct:
                    st.markdown('<div class="badge-correct">✅ Correct!</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="badge-wrong">❌ Answer: {correct}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="explanation-box">💡 {q.get("explanation","")}</div>', unsafe_allow_html=True)
            st.write("")

        st.divider()
        if not st.session_state["tf_submitted"]:
            if st.button("✅ Submit True/False", type="primary", use_container_width=True):
                answers = st.session_state["tf_answers"]
                score = sum(1 for i,q in enumerate(questions) if answers[i]==q["answer"])
                st.session_state["tf_score"] = score
                st.session_state["tf_submitted"] = True
                st.session_state["timer_active"] = False
                save_quiz_result(st.session_state["quiz_id"] or 1, score, len(questions))
                if score/len(questions)*100 >= 80:
                    st.balloons()
                st.rerun()
        else:
            pct = st.session_state["tf_score"]/len(questions)*100
            st.markdown(f"""
            <div class="score-display">
                <div class="score-number">{pct:.0f}%</div>
                <div class="score-label">✅ {st.session_state["tf_score"]} out of {len(questions)} correct — {diff} Level</div>
            </div>
            """, unsafe_allow_html=True)
            st.write("")
            if st.button("🔄 Retake", use_container_width=True):
                st.session_state["tf_answers"] = [None]*len(questions)
                st.session_state["tf_submitted"] = False
                st.rerun()

    # ════════════════════════════════════════════════════════════════════
    # FILL IN THE BLANKS
    # ════════════════════════════════════════════════════════════════════
    elif st.session_state["quiz_type"] == "Fill Blanks" and st.session_state["fb_questions"]:
        questions = st.session_state["fb_questions"]
        diff = st.session_state.get("quiz_difficulty","Medium")
        badge_cls = {"Easy":"badge-easy","Medium":"badge-medium","Hard":"badge-hard"}

        for i, q in enumerate(questions):
            submitted = st.session_state["fb_submitted"]
            correct = q["answer"]

            st.markdown(f"""
            <div class="quiz-card" style="border-left-color:#f093fb">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <div class="quiz-number">Question {i+1} of {len(questions)}</div>
                    <span class="{badge_cls.get(diff,'badge-medium')}">{diff}</span>
                </div>
                <div class="quiz-question">{q["question"]}</div>
            </div>
            """, unsafe_allow_html=True)

            if not submitted:
                st.markdown(f'<div class="hint-box">💡 Hint: {q.get("hint","")}</div>',
                           unsafe_allow_html=True)
                answer = st.text_input(
                    f"Your answer for Q{i+1}",
                    key=f"fb{i}",
                    placeholder="Type your answer here...",
                    label_visibility="collapsed"
                )
                if answer:
                    st.session_state["fb_answers"][i] = answer
            else:
                user_ans = st.session_state["fb_answers"][i] or ""
                is_correct = user_ans.strip().lower() == correct.strip().lower()
                if is_correct:
                    st.markdown('<div class="badge-correct">✅ Correct!</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="badge-wrong">❌ Answer: {correct}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="explanation-box">💡 {q.get("explanation","")}</div>', unsafe_allow_html=True)
            st.write("")

        st.divider()
        if not st.session_state["fb_submitted"]:
            if st.button("✅ Submit Fill Blanks", type="primary", use_container_width=True):
                answers = st.session_state["fb_answers"]
                score = sum(
                    1 for i,q in enumerate(questions)
                    if (answers[i] or "").strip().lower() == q["answer"].strip().lower()
                )
                st.session_state["fb_score"] = score
                st.session_state["fb_submitted"] = True
                st.session_state["timer_active"] = False
                save_quiz_result(st.session_state["quiz_id"] or 1, score, len(questions))
                if score/len(questions)*100 >= 80:
                    st.balloons()
                st.rerun()
        else:
            pct = st.session_state["fb_score"]/len(questions)*100
            st.markdown(f"""
            <div class="score-display">
                <div class="score-number">{pct:.0f}%</div>
                <div class="score-label">✏️ {st.session_state["fb_score"]} out of {len(questions)} correct — {diff} Level</div>
            </div>
            """, unsafe_allow_html=True)
            st.write("")
            if st.button("🔄 Retake", use_container_width=True):
                st.session_state["fb_answers"] = [""]*len(questions)
                st.session_state["fb_submitted"] = False
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# FLASHCARDS
# ═══════════════════════════════════════════════════════════════════════════
elif page == "🃏 Flashcards":
    st.markdown('<div class="hero-title">🃏 Flashcard Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Flip through AI-generated study cards</div>', unsafe_allow_html=True)
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
        with st.spinner("🤖 Creating flashcards..."):
            try:
                cards = generate_flashcards(st.session_state["doc_text"], num_cards)
                if TTS_AVAILABLE and st.session_state["selected_lang"] != "English":
                    lang_code = LANGUAGE_CODES[st.session_state["selected_lang"]]
                    with st.spinner("🌍 Translating..."):
                        cards = translate_flashcards(cards, lang_code)
                save_flashcards(st.session_state["doc_id"] or 1, cards)
                st.session_state["flashcards"] = cards
                st.session_state["fc_index"] = 0
                st.session_state["fc_flipped"] = False
                st.success(f"✅ {len(cards)} flashcards created!")
            except Exception as e:
                st.error(f"❌ Error: {e}")

    cards = st.session_state["flashcards"]
    if cards:
        st.divider()
        idx = st.session_state["fc_index"]
        card = cards[idx]
        _, col, _ = st.columns([1,3,1])
        with col:
            st.markdown(f"### Card {idx+1} of {len(cards)}")
            st.progress((idx+1)/len(cards))
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
            st.write("")
            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button("⬅️ Prev", use_container_width=True):
                    if idx > 0:
                        st.session_state["fc_index"] -= 1
                        st.session_state["fc_flipped"] = False
                        st.rerun()
            with b2:
                label = "🙈 Hide" if st.session_state["fc_flipped"] else "👁️ Reveal"
                if st.button(label, type="primary", use_container_width=True):
                    st.session_state["fc_flipped"] = not st.session_state["fc_flipped"]
                    st.rerun()
            with b3:
                if st.button("Next ➡️", use_container_width=True):
                    if idx < len(cards)-1:
                        st.session_state["fc_index"] += 1
                        st.session_state["fc_flipped"] = False
                        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# CHAT
# ═══════════════════════════════════════════════════════════════════════════
elif page == "💬 Chat with Doc":
    st.markdown('<div class="hero-title">💬 Chat with Doc</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Ask anything — answers come from your document</div>', unsafe_allow_html=True)
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
    st.markdown('<div class="hero-title">📊 Your Progress</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Track your learning journey</div>', unsafe_allow_html=True)
    st.divider()

    results = get_quiz_results()
    if not results:
        st.info("🎯 Take some quizzes to see your progress here!")
        if st.button("📝 Generate Quiz Now", type="primary"):
            st.query_params["page"] = "📝 Generate Quiz"
            st.rerun()
    else:
        scores = [r[1]/r[2]*100 for r in results]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{len(results)}</div><div class="stat-label">Quizzes Taken</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{sum(scores)/len(scores):.0f}%</div><div class="stat-label">Average Score</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{max(scores):.0f}%</div><div class="stat-label">Best Score</div></div>', unsafe_allow_html=True)

        st.divider()
        st.markdown("### 🏆 Recent Results")
        for r in results:
            pct = r[1]/r[2]*100
            color = "#28a745" if pct >= 70 else "#dc3545"
            emoji = "🏆" if pct >= 80 else "👍" if pct >= 60 else "📚"
            st.markdown(f"""
            <div style='background:white;border-radius:14px;padding:16px 22px;margin:8px 0;
                        box-shadow:0 3px 15px rgba(102,126,234,0.1);border-left:5px solid {color};
                        display:flex;align-items:center;gap:16px'>
                <span style='font-size:1.8em'>{emoji}</span>
                <div style='flex:1'>
                    <div style='font-weight:800;color:#1a1a2e'>{r[3]}</div>
                    <div style='color:#6b7280;font-size:0.85em'>{r[0][:16]}</div>
                </div>
                <div style='text-align:right'>
                    <div style='font-weight:900;font-size:1.4em;color:{color}'>{pct:.0f}%</div>
                    <div style='color:#6b7280;font-size:0.85em'>{r[1]}/{r[2]} correct</div>
                </div>
            </div>
            """, unsafe_allow_html=True)