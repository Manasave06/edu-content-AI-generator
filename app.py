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
    page_title="EduContent AI Generator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Sora:wght@300;400;600&display=swap');

html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
h1, h2, h3 { font-family: 'JetBrains Mono', monospace; }
.stApp { background: #0d1117; color: #c9d1d9; }

.card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 18px 22px;
    margin: 10px 0;
}
.card-blue   { border-left: 4px solid #58a6ff; }
.card-green  { border-left: 4px solid #3fb950; }
.card-purple { border-left: 4px solid #bc8cff; }
.card-red    { border-left: 4px solid #f85149; }

.fc-front {
    background: linear-gradient(135deg, #1f4068, #1b262c);
    border-radius: 12px; padding: 30px;
    text-align: center; font-size: 1.2em;
    font-weight: 600; color: #58a6ff;
    min-height: 130px;
    display: flex; align-items: center; justify-content: center;
}
.fc-back {
    background: linear-gradient(135deg, #1a3a2a, #162820);
    border-radius: 12px; padding: 30px;
    text-align: center; font-size: 1em;
    color: #3fb950; min-height: 130px;
    display: flex; align-items: center; justify-content: center;
}
.correct { color: #3fb950; font-weight: 700; font-size: 1.1em; }
.wrong   { color: #f85149; font-weight: 700; font-size: 1.1em; }
.chat-user {
    background: #1c2128; border-left: 3px solid #58a6ff;
    border-radius: 8px; padding: 10px 14px; margin: 6px 0;
}
.chat-ai {
    background: #161b22; border-left: 3px solid #3fb950;
    border-radius: 8px; padding: 10px 14px; margin: 6px 0;
}
</style>
""", unsafe_allow_html=True)

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

with st.sidebar:
    st.markdown("## 🎓 EduContent AI")
    st.caption("Groq · LLaMA3 · Free & Fast")
    st.divider()

    page = st.radio("Navigation", [
        "📤 Upload Document",
        "📝 Generate Quiz",
        "🃏 Flashcards",
        "💬 Chat with Doc",
        "📊 Progress"
    ], label_visibility="collapsed")

    st.divider()
    if st.session_state["doc_name"]:
        st.markdown(
            f'<div class="card card-green">📄 <b>{st.session_state["doc_name"]}</b><br>'
            f'<small>{len(st.session_state["doc_text"]):,} characters loaded</small></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="card card-red">⚠️ No document loaded</div>',
            unsafe_allow_html=True
        )

    st.divider()
    if st.button("🗑️ Clear Everything", use_container_width=True):
        for k, v in defaults.items():
            st.session_state[k] = v
        st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Upload
# ════════════════════════════════════════════════════════════════════════════
if page == "📤 Upload Document":
    st.title("📤 Upload Your Document")
    st.caption("Supports PDF and TXT files")
    st.divider()

    uploaded = st.file_uploader(
        "Drop your file here",
        type=["pdf", "txt"],
        label_visibility="collapsed"
    )

    if uploaded:
        with st.spinner("⚙️ Reading document..."):
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
                with st.expander("👀 Preview first 1000 characters"):
                    st.code(text[:1000], language=None)

                st.success(f"✅ '{uploaded.name}' loaded! Use the sidebar to generate Quiz or Flashcards.")

            except Exception as e:
                st.error(f"❌ Error: {e}")
    else:
        st.markdown("""
        <div class="card card-blue">
        <h4>🚀 How it works</h4>
        <p>1️⃣ Upload a PDF or TXT file</p>
        <p>2️⃣ AI reads and understands the content</p>
        <p>3️⃣ Generate Quizzes, Flashcards or Chat about it</p>
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Quiz
# ════════════════════════════════════════════════════════════════════════════
elif page == "📝 Generate Quiz":
    st.title("📝 Quiz Generator")
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
        with st.spinner("🤖 AI is writing your quiz..."):
            try:
                questions = generate_quiz(st.session_state["doc_text"], num_q)
                quiz_id = save_quiz(st.session_state["doc_id"] or 1, questions)
                st.session_state["quiz_questions"] = questions
                st.session_state["quiz_id"] = quiz_id
                st.session_state["quiz_answers"] = [None] * len(questions)
                st.session_state["quiz_submitted"] = False
                st.session_state["quiz_score"] = 0
                st.success(f"✅ {len(questions)} questions ready!")
            except Exception as e:
                st.error(f"❌ Failed: {e}")

    questions = st.session_state["quiz_questions"]
    if questions:
        st.divider()
        for i, q in enumerate(questions):
            submitted = st.session_state["quiz_submitted"]
            chosen = st.session_state["quiz_answers"][i]
            correct = q["answer"]

            st.markdown(
                f'<div class="card card-blue"><b>Q{i+1}. {q["question"]}</b></div>',
                unsafe_allow_html=True
            )

            sel = st.radio(
                f"Select answer for question {i+1}",
                q["options"],
                index=None,
                key=f"q{i}",
                label_visibility="collapsed"
            )
            if sel:
                st.session_state["quiz_answers"][i] = sel

            if submitted:
                if chosen == correct:
                    st.markdown('<span class="correct">✓ Correct!</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="wrong">✗ Correct answer: {correct}</span>', unsafe_allow_html=True)
                st.caption(f"💡 {q.get('explanation', '')}")

            st.write("")

        st.divider()
        if not st.session_state["quiz_submitted"]:
            if st.button("✅ Submit Answers", type="primary", use_container_width=True):
                answers = st.session_state["quiz_answers"]
                score = sum(
                    1 for i, q in enumerate(questions)
                    if answers[i] == q["answer"]
                )
                st.session_state["quiz_score"] = score
                st.session_state["quiz_submitted"] = True
                save_quiz_result(st.session_state["quiz_id"] or 1, score, len(questions))
                pct = score / len(questions) * 100
                st.success(f"🎯 Score: {score}/{len(questions)} ({pct:.0f}%)")
                if pct >= 80:
                    st.balloons()
                st.rerun()
        else:
            pct = st.session_state["quiz_score"] / len(questions) * 100
            color = "card-green" if pct >= 60 else "card-red"
            st.markdown(
                f'<div class="card {color}" style="text-align:center;font-size:1.3em">'
                f'🎯 Score: <b>{st.session_state["quiz_score"]}/{len(questions)}</b> ({pct:.0f}%)</div>',
                unsafe_allow_html=True
            )
            if st.button("🔄 Retake Quiz", use_container_width=True):
                st.session_state["quiz_answers"] = [None] * len(questions)
                st.session_state["quiz_submitted"] = False
                st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# PAGE 3 — Flashcards
# ════════════════════════════════════════════════════════════════════════════
elif page == "🃏 Flashcards":
    st.title("🃏 Flashcard Studio")
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
        with st.spinner("🤖 Creating flashcards..."):
            try:
                cards = generate_flashcards(st.session_state["doc_text"], num_cards)
                save_flashcards(st.session_state["doc_id"] or 1, cards)
                st.session_state["flashcards"] = cards
                st.session_state["fc_index"] = 0
                st.session_state["fc_flipped"] = False
                st.success(f"✅ {len(cards)} flashcards ready!")
            except Exception as e:
                st.error(f"❌ Error: {e}")

    cards = st.session_state["flashcards"]
    if cards:
        st.divider()
        idx = st.session_state["fc_index"]
        card = cards[idx]

        st.markdown(f"**Card {idx+1} of {len(cards)}**")
        st.progress((idx + 1) / len(cards))
        st.write("")

        if not st.session_state["fc_flipped"]:
            st.markdown(
                f'<div class="fc-front">❓ {card["front"]}</div>',
                unsafe_allow_html=True
            )
            st.write("")
            if st.button("👁️ Show Answer", use_container_width=True):
                st.session_state["fc_flipped"] = True
                st.rerun()
        else:
            st.markdown(
                f'<div class="fc-front">❓ {card["front"]}</div>',
                unsafe_allow_html=True
            )
            st.write("")
            st.markdown(
                f'<div class="fc-back">✅ {card["back"]}</div>',
                unsafe_allow_html=True
            )

        st.write("")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("⬅️ Previous", use_container_width=True):
                if idx > 0:
                    st.session_state["fc_index"] -= 1
                    st.session_state["fc_flipped"] = False
                    st.rerun()
        with c2:
            if st.button("🔁 Flip", use_container_width=True):
                st.session_state["fc_flipped"] = not st.session_state["fc_flipped"]
                st.rerun()
        with c3:
            if st.button("Next ➡️", use_container_width=True):
                if idx < len(cards) - 1:
                    st.session_state["fc_index"] += 1
                    st.session_state["fc_flipped"] = False
                    st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# PAGE 4 — Chat
# ════════════════════════════════════════════════════════════════════════════
elif page == "💬 Chat with Doc":
    st.title("💬 Chat with Your Document")
    st.caption("Answers come only from your uploaded document")
    st.divider()

    if not st.session_state["doc_text"]:
        st.warning("⚠️ Please upload a document first!")
        st.stop()

    for h in st.session_state["chat_history"]:
        st.markdown(
            f'<div class="chat-user">🧑 <b>You:</b> {h["user"]}</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div class="chat-ai">🤖 <b>AI:</b> {h["assistant"]}</div>',
            unsafe_allow_html=True
        )

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
# PAGE 5 — Progress
# ════════════════════════════════════════════════════════════════════════════
elif page == "📊 Progress":
    st.title("📊 Progress Dashboard")
    st.divider()

    results = get_quiz_results()
    if not results:
        st.info("Take some quizzes to see your progress here!")
    else:
        scores = [r[1]/r[2]*100 for r in results]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f'<div class="card card-blue" style="text-align:center"><h2>{len(results)}</h2><p>Quizzes Taken</p></div>',
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f'<div class="card card-green" style="text-align:center"><h2>{sum(scores)/len(scores):.0f}%</h2><p>Average Score</p></div>',
                unsafe_allow_html=True
            )
        with col3:
            st.markdown(
                f'<div class="card card-purple" style="text-align:center"><h2>{max(scores):.0f}%</h2><p>Best Score</p></div>',
                unsafe_allow_html=True
            )

        st.divider()
        st.subheader("Recent Quiz History")
        for r in results:
            pct = r[1]/r[2]*100
            color = "#3fb950" if pct >= 70 else "#f85149"
            st.markdown(f"""
            <div style='background:#1a1f2e;border-radius:8px;padding:12px;margin:8px 0;
                        border-left:4px solid {color}'>
                📄 <b>{r[3]}</b> &nbsp;·&nbsp;
                {r[1]}/{r[2]} correct &nbsp;·&nbsp;
                <b style='color:{color}'>{pct:.0f}%</b> &nbsp;·&nbsp;
                <small>{r[0][:16]}</small>
            </div>""", unsafe_allow_html=True)