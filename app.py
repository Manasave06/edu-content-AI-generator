import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from processor import process_file, chunk_text
from generator import generate_quiz, generate_flashcards, chat_with_doc
from database import (
    init_db, save_document, save_quiz,
    save_flashcards, save_quiz_result,
    get_all_documents, get_quiz_results
)

init_db()

st.set_page_config(
    page_title="EduContent AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Fira+Code:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1425 50%, #0a1628 100%);
    color: #e2e8f0;
}

/* Animated background dots */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image: radial-gradient(circle at 1px 1px, rgba(99,179,237,0.08) 1px, transparent 0);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1425 0%, #111827 100%) !important;
    border-right: 1px solid rgba(99,179,237,0.15) !important;
}

section[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }

/* Glowing title */
.hero-title {
    font-family: 'Outfit', sans-serif;
    font-size: 3em;
    font-weight: 800;
    background: linear-gradient(135deg, #63b3ed, #76e4f7, #b794f4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0;
    line-height: 1.2;
}

.hero-sub {
    color: #718096;
    font-size: 1.1em;
    font-weight: 300;
    margin-top: 4px;
    margin-bottom: 24px;
}

/* Feature cards */
.feature-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.04), rgba(255,255,255,0.01));
    border: 1px solid rgba(99,179,237,0.2);
    border-radius: 16px;
    padding: 24px;
    margin: 10px 0;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.feature-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 3px;
    background: linear-gradient(90deg, #63b3ed, #b794f4);
}

.feature-card:hover {
    border-color: rgba(99,179,237,0.5);
    transform: translateY(-2px);
}

.feature-icon {
    font-size: 2.5em;
    margin-bottom: 12px;
}

.feature-title {
    font-size: 1.2em;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 6px;
}

.feature-desc {
    font-size: 0.9em;
    color: #718096;
    line-height: 1.5;
}

/* Quiz cards */
.quiz-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(99,179,237,0.2);
    border-radius: 14px;
    padding: 20px 24px;
    margin: 16px 0;
    position: relative;
}

.quiz-number {
    font-family: 'Fira Code', monospace;
    font-size: 0.75em;
    color: #63b3ed;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.quiz-question {
    font-size: 1.1em;
    font-weight: 600;
    color: #e2e8f0;
    line-height: 1.5;
}

/* Flashcards */
.fc-front {
    background: linear-gradient(135deg, #1a365d, #2a4a7f);
    border: 1px solid rgba(99,179,237,0.3);
    border-radius: 20px;
    padding: 40px 30px;
    text-align: center;
    font-size: 1.3em;
    font-weight: 700;
    color: #bee3f8;
    min-height: 160px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 20px 60px rgba(99,179,237,0.15);
}

.fc-back {
    background: linear-gradient(135deg, #1a3a2a, #22543d);
    border: 1px solid rgba(72,187,120,0.3);
    border-radius: 20px;
    padding: 40px 30px;
    text-align: center;
    font-size: 1em;
    color: #9ae6b4;
    min-height: 160px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 20px 60px rgba(72,187,120,0.1);
    margin-top: 12px;
}

/* Result badges */
.badge-correct {
    background: linear-gradient(135deg, #22543d, #276749);
    border: 1px solid #48bb78;
    border-radius: 8px;
    padding: 8px 16px;
    color: #9ae6b4;
    font-weight: 700;
    font-size: 0.95em;
    display: inline-block;
    margin: 4px 0;
}

.badge-wrong {
    background: linear-gradient(135deg, #742a2a, #9b2c2c);
    border: 1px solid #fc8181;
    border-radius: 8px;
    padding: 8px 16px;
    color: #fed7d7;
    font-weight: 700;
    font-size: 0.95em;
    display: inline-block;
    margin: 4px 0;
}

.explanation-box {
    background: rgba(183,148,244,0.08);
    border-left: 3px solid #b794f4;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    color: #d6bcfa;
    font-size: 0.9em;
    margin-top: 8px;
}

/* Chat bubbles */
.chat-user {
    background: linear-gradient(135deg, rgba(99,179,237,0.12), rgba(99,179,237,0.06));
    border: 1px solid rgba(99,179,237,0.25);
    border-radius: 16px 16px 4px 16px;
    padding: 14px 18px;
    margin: 10px 0;
    color: #bee3f8;
}

.chat-ai {
    background: linear-gradient(135deg, rgba(72,187,120,0.1), rgba(72,187,120,0.05));
    border: 1px solid rgba(72,187,120,0.2);
    border-radius: 16px 16px 16px 4px;
    padding: 14px 18px;
    margin: 10px 0;
    color: #9ae6b4;
}

.chat-label {
    font-family: 'Fira Code', monospace;
    font-size: 0.7em;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 6px;
    opacity: 0.7;
}

/* Score display */
.score-display {
    background: linear-gradient(135deg, #1a365d, #2a4a7f);
    border: 1px solid rgba(99,179,237,0.4);
    border-radius: 20px;
    padding: 30px;
    text-align: center;
}

.score-number {
    font-family: 'Outfit', sans-serif;
    font-size: 4em;
    font-weight: 800;
    background: linear-gradient(135deg, #63b3ed, #b794f4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}

.score-label {
    color: #718096;
    font-size: 0.95em;
    margin-top: 8px;
}

/* Stat cards */
.stat-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 24px;
    text-align: center;
}

.stat-number {
    font-size: 2.5em;
    font-weight: 800;
    background: linear-gradient(135deg, #63b3ed, #76e4f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stat-label {
    color: #718096;
    font-size: 0.85em;
    margin-top: 4px;
}

/* Sidebar nav */
.nav-brand {
    font-family: 'Outfit', sans-serif;
    font-size: 1.4em;
    font-weight: 800;
    background: linear-gradient(135deg, #63b3ed, #b794f4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.doc-loaded {
    background: linear-gradient(135deg, rgba(72,187,120,0.1), rgba(72,187,120,0.05));
    border: 1px solid rgba(72,187,120,0.3);
    border-radius: 12px;
    padding: 14px;
    margin: 8px 0;
}

.doc-not-loaded {
    background: linear-gradient(135deg, rgba(245,101,101,0.1), rgba(245,101,101,0.05));
    border: 1px solid rgba(245,101,101,0.3);
    border-radius: 12px;
    padding: 14px;
    margin: 8px 0;
}

/* Progress bar custom */
.stProgress > div > div {
    background: linear-gradient(90deg, #63b3ed, #b794f4) !important;
    border-radius: 10px !important;
}

/* Buttons */
.stButton > button {
    border-radius: 10px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3182ce, #553c9a) !important;
    border: none !important;
    color: white !important;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(99,179,237,0.3) !important;
}

/* Upload area */
.stFileUploader {
    border-radius: 16px !important;
}

/* Metrics */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    padding: 16px !important;
}

/* Divider */
hr {
    border-color: rgba(255,255,255,0.08) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session State ────────────────────────────────────────────────────────────
defaults = {
    "doc_text": "",
    "doc_name": "",
    "doc_id": None,
    "quiz_questions": [],
    "quiz_answers": [],
    "quiz_submitted": False,
    "quiz_score": 0,
    "quiz_id": None,
    "flashcards": [],
    "fc_index": 0,
    "fc_flipped": False,
    "chat_history": []
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="nav-brand">🎓 EduContent AI</div>', unsafe_allow_html=True)
    st.caption("Powered by Groq · LLaMA3")
    st.divider()

    page = st.radio("Navigation", [
        "🏠 Home",
        "📤 Upload Document",
        "📝 Generate Quiz",
        "🃏 Flashcards",
        "💬 Chat with Doc",
        "📊 Progress"
    ], label_visibility="collapsed")

    st.divider()

    if st.session_state["doc_name"]:
        st.markdown(f"""
        <div class="doc-loaded">
            <div style="font-size:0.7em;color:#48bb78;font-weight:700;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px">✓ Document Loaded</div>
            <div style="font-weight:600;color:#9ae6b4;font-size:0.95em">{st.session_state["doc_name"]}</div>
            <div style="color:#68d391;font-size:0.8em;margin-top:2px">{len(st.session_state["doc_text"]):,} characters</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="doc-not-loaded">
            <div style="font-size:0.7em;color:#fc8181;font-weight:700;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px">⚠ No Document</div>
            <div style="color:#feb2b2;font-size:0.85em">Upload a document to begin</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    if st.button("🗑️ Clear Everything", use_container_width=True):
        for k, v in defaults.items():
            st.session_state[k] = v
        st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# PAGE: Home
# ════════════════════════════════════════════════════════════════════════════
if page == "🏠 Home":
    st.markdown('<div class="hero-title">Learn Smarter,<br>Not Harder.</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Upload any document → Get quizzes, flashcards & AI chat instantly</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📤</div>
            <div class="feature-title">Upload Docs</div>
            <div class="feature-desc">PDF or TXT files up to 200MB supported</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📝</div>
            <div class="feature-title">AI Quizzes</div>
            <div class="feature-desc">Auto-generate multiple choice questions</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🃏</div>
            <div class="feature-title">Flashcards</div>
            <div class="feature-desc">Create study cards from any content</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💬</div>
            <div class="feature-title">AI Chat</div>
            <div class="feature-desc">Ask questions about your document</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🚀 Get Started")
    st.info("👈 Click **Upload Document** in the sidebar to begin!")

# ════════════════════════════════════════════════════════════════════════════
# PAGE: Upload
# ════════════════════════════════════════════════════════════════════════════
elif page == "📤 Upload Document":
    st.markdown('<div class="hero-title">📤 Upload Document</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Supports PDF and TXT files</div>', unsafe_allow_html=True)
    st.divider()

    uploaded = st.file_uploader(
        "Drop your file here",
        type=["pdf", "txt"],
        label_visibility="collapsed"
    )

    if uploaded:
        with st.spinner("⚙️ Processing your document..."):
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

                st.divider()
                with st.expander("👀 Preview content"):
                    st.code(text[:1000], language=None)

                st.success(f"✅ '{uploaded.name}' loaded successfully! Choose an option from the sidebar.")
            except Exception as e:
                st.error(f"❌ Error: {e}")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📄</div>
                <div class="feature-title">PDF Files</div>
                <div class="feature-desc">Upload textbooks, notes, research papers, articles — any PDF document works perfectly.</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📝</div>
                <div class="feature-title">Text Files</div>
                <div class="feature-desc">Plain .txt files, notes, transcripts, lecture content — all supported instantly.</div>
            </div>
            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE: Quiz
# ════════════════════════════════════════════════════════════════════════════
elif page == "📝 Generate Quiz":
    st.markdown('<div class="hero-title">📝 Quiz Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">AI-powered questions from your document</div>', unsafe_allow_html=True)
    st.divider()

    if not st.session_state["doc_text"]:
        st.warning("⚠️ Please upload a document first!")
        st.stop()

    col1, col2 = st.columns([3, 1])
    with col1:
        num_q = st.slider("Number of questions", 3, 15, 5)
    with col2:
        st.write("")
        gen = st.button("⚡ Generate Quiz", type="primary", use_container_width=True)

    if gen:
        with st.spinner("🤖 AI is crafting your quiz..."):
            try:
                questions = generate_quiz(st.session_state["doc_text"], num_q)
                quiz_id = save_quiz(st.session_state["doc_id"] or 1, questions)
                st.session_state["quiz_questions"] = questions
                st.session_state["quiz_id"] = quiz_id
                st.session_state["quiz_answers"] = [None] * len(questions)
                st.session_state["quiz_submitted"] = False
                st.session_state["quiz_score"] = 0
                st.success(f"✅ {len(questions)} questions generated!")
            except Exception as e:
                st.error(f"❌ Failed: {e}")

    questions = st.session_state["quiz_questions"]
    if questions:
        st.divider()
        for i, q in enumerate(questions):
            submitted = st.session_state["quiz_submitted"]
            chosen = st.session_state["quiz_answers"][i]
            correct = q["answer"]

            st.markdown(f"""
            <div class="quiz-card">
                <div class="quiz-number">Question {i+1} of {len(questions)}</div>
                <div class="quiz-question">{q["question"]}</div>
            </div>
            """, unsafe_allow_html=True)

            sel = st.radio(
                f"Answer for Q{i+1}",
                q["options"],
                index=None,
                key=f"q{i}",
                label_visibility="collapsed"
            )
            if sel:
                st.session_state["quiz_answers"][i] = sel

            if submitted:
                if chosen == correct:
                    st.markdown('<div class="badge-correct">✓ Correct!</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="badge-wrong">✗ Correct: {correct}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="explanation-box">💡 {q.get("explanation", "")}</div>', unsafe_allow_html=True)

            st.write("")

        st.divider()
        if not st.session_state["quiz_submitted"]:
            if st.button("✅ Submit Answers", type="primary", use_container_width=True):
                answers = st.session_state["quiz_answers"]
                score = sum(1 for i, q in enumerate(questions) if answers[i] == q["answer"])
                st.session_state["quiz_score"] = score
                st.session_state["quiz_submitted"] = True
                save_quiz_result(st.session_state["quiz_id"] or 1, score, len(questions))
                pct = score / len(questions) * 100
                if pct >= 80:
                    st.balloons()
                st.rerun()
        else:
            pct = st.session_state["quiz_score"] / len(questions) * 100
            st.markdown(f"""
            <div class="score-display">
                <div class="score-number">{pct:.0f}%</div>
                <div class="score-label">{st.session_state["quiz_score"]} out of {len(questions)} correct</div>
            </div>
            """, unsafe_allow_html=True)
            st.write("")
            if st.button("🔄 Retake Quiz", use_container_width=True):
                st.session_state["quiz_answers"] = [None] * len(questions)
                st.session_state["quiz_submitted"] = False
                st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# PAGE: Flashcards
# ════════════════════════════════════════════════════════════════════════════
elif page == "🃏 Flashcards":
    st.markdown('<div class="hero-title">🃏 Flashcard Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Flip through AI-generated study cards</div>', unsafe_allow_html=True)
    st.divider()

    if not st.session_state["doc_text"]:
        st.warning("⚠️ Please upload a document first!")
        st.stop()

    col1, col2 = st.columns([3, 1])
    with col1:
        num_cards = st.slider("Number of flashcards", 5, 20, 8)
    with col2:
        st.write("")
        gen = st.button("⚡ Generate Cards", type="primary", use_container_width=True)

    if gen:
        with st.spinner("🤖 Creating your flashcards..."):
            try:
                cards = generate_flashcards(st.session_state["doc_text"], num_cards)
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

        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.markdown(f"**Card {idx+1} of {len(cards)}**")
            st.progress((idx + 1) / len(cards))
            st.write("")

            st.markdown(f'<div class="fc-front">❓ {card["front"]}</div>', unsafe_allow_html=True)

            if st.session_state["fc_flipped"]:
                st.markdown(f'<div class="fc-back">✅ {card["back"]}</div>', unsafe_allow_html=True)

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
                if st.button(label, use_container_width=True, type="primary"):
                    st.session_state["fc_flipped"] = not st.session_state["fc_flipped"]
                    st.rerun()
            with b3:
                if st.button("Next ➡️", use_container_width=True):
                    if idx < len(cards) - 1:
                        st.session_state["fc_index"] += 1
                        st.session_state["fc_flipped"] = False
                        st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# PAGE: Chat
# ════════════════════════════════════════════════════════════════════════════
elif page == "💬 Chat with Doc":
    st.markdown('<div class="hero-title">💬 Chat with Doc</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Ask anything — answers come from your document</div>', unsafe_allow_html=True)
    st.divider()

    if not st.session_state["doc_text"]:
        st.warning("⚠️ Please upload a document first!")
        st.stop()

    for h in st.session_state["chat_history"]:
        st.markdown(f"""
        <div class="chat-user">
            <div class="chat-label">🧑 You</div>
            {h["user"]}
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="chat-ai">
            <div class="chat-label">🤖 AI</div>
            {h["assistant"]}
        </div>
        """, unsafe_allow_html=True)

    question = st.chat_input("Ask anything about your document...")
    if question:
        with st.spinner("🤔 Thinking..."):
            try:
                answer = chat_with_doc(
                    st.session_state["doc_text"],
                    question,
                    st.session_state["chat_history"]
                )
                st.session_state["chat_history"].append({
                    "user": question,
                    "assistant": answer
                })
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")

    if st.session_state["chat_history"]:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state["chat_history"] = []
            st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# PAGE: Progress
# ════════════════════════════════════════════════════════════════════════════
elif page == "📊 Progress":
    st.markdown('<div class="hero-title">📊 Progress</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Track your learning journey</div>', unsafe_allow_html=True)
    st.divider()

    results = get_quiz_results()
    if not results:
        st.info("🎯 Take some quizzes to see your progress here!")
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
        st.markdown("### Recent Results")
        for r in results:
            pct = r[1]/r[2]*100
            color = "#48bb78" if pct >= 70 else "#fc8181"
            st.markdown(f"""
            <div style='background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);
                        border-radius:12px;padding:16px 20px;margin:8px 0;
                        border-left:4px solid {color}'>
                <span style='color:#e2e8f0;font-weight:600'>{r[3]}</span>
                &nbsp;&nbsp;
                <span style='color:#718096;font-size:0.9em'>{r[1]}/{r[2]} correct</span>
                &nbsp;&nbsp;
                <span style='color:{color};font-weight:700'>{pct:.0f}%</span>
                &nbsp;&nbsp;
                <span style='color:#4a5568;font-size:0.8em'>{r[0][:16]}</span>
            </div>
            """, unsafe_allow_html=True)