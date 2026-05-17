import io
import json
from datetime import datetime


def export_quiz_results_txt(results: list) -> str:
    """Export quiz results as text."""
    lines = []
    lines.append("=" * 50)
    lines.append("📊 QUIZ RESULTS REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 50)
    lines.append("")

    if not results:
        lines.append("No quiz results found.")
        return "\n".join(lines)

    scores = [r[1]/r[2]*100 for r in results]
    lines.append(f"Total Quizzes: {len(results)}")
    lines.append(f"Average Score: {sum(scores)/len(scores):.1f}%")
    lines.append(f"Best Score: {max(scores):.1f}%")
    lines.append("")
    lines.append("-" * 50)
    lines.append("RECENT RESULTS:")
    lines.append("-" * 50)

    for r in results:
        pct = r[1]/r[2]*100
        qtype = r[4] if len(r) > 4 else "MCQ"
        diff = r[5] if len(r) > 5 else "Medium"
        lines.append(f"📄 {r[3]}")
        lines.append(f"   Type: {qtype} | Difficulty: {diff}")
        lines.append(f"   Score: {r[1]}/{r[2]} ({pct:.1f}%)")
        lines.append(f"   Date: {r[0][:16]}")
        lines.append("")

    return "\n".join(lines)


def export_flashcards_txt(cards: list, doc_name: str) -> str:
    """Export flashcards as text."""
    lines = []
    lines.append("=" * 50)
    lines.append("🃏 FLASHCARDS")
    lines.append(f"Document: {doc_name}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Total Cards: {len(cards)}")
    lines.append("=" * 50)
    lines.append("")

    for i, card in enumerate(cards, 1):
        lines.append(f"Card {i}:")
        lines.append(f"Q: {card.get('front', '')}")
        lines.append(f"A: {card.get('back', '')}")
        lines.append("-" * 30)

    return "\n".join(lines)


def export_study_notes_txt(content: dict, doc_name: str) -> str:
    """Export study notes as text."""
    lines = []
    lines.append("=" * 50)
    lines.append("📚 STUDY NOTES")
    lines.append(f"Document: {doc_name}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 50)
    lines.append("")

    if content.get("one_liner"):
        lines.append(f"💡 KEY INSIGHT: {content['one_liner']}")
        lines.append("")

    if content.get("summary"):
        lines.append("📖 SUMMARY:")
        lines.append("-" * 30)
        lines.append(content["summary"])
        lines.append("")

    if content.get("key_points"):
        lines.append("🎯 KEY POINTS:")
        lines.append("-" * 30)
        for i, point in enumerate(content["key_points"], 1):
            lines.append(f"{i}. {point}")
        lines.append("")

    if content.get("exam_tips"):
        lines.append("📝 EXAM TIPS:")
        lines.append("-" * 30)
        for tip in content["exam_tips"]:
            lines.append(f"✅ {tip}")
        lines.append("")

    if content.get("difficult_terms"):
        lines.append("📖 KEY TERMS:")
        lines.append("-" * 30)
        for term in content["difficult_terms"]:
            lines.append(f"• {term.get('term','')}: {term.get('definition','')}")
        lines.append("")

    return "\n".join(lines)


def export_quiz_questions_txt(questions: list, doc_name: str,
                               quiz_type: str, difficulty: str) -> str:
    """Export quiz questions as text."""
    lines = []
    lines.append("=" * 50)
    lines.append(f"📝 {quiz_type.upper()} QUIZ")
    lines.append(f"Document: {doc_name}")
    lines.append(f"Difficulty: {difficulty}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 50)
    lines.append("")

    for i, q in enumerate(questions, 1):
        lines.append(f"Q{i}. {q.get('question', '')}")

        if quiz_type == "MCQ" and q.get("options"):
            for j, opt in enumerate(q["options"]):
                lines.append(f"   {chr(65+j)}) {opt}")

        lines.append(f"Answer: {q.get('answer', '')}")
        if q.get("explanation"):
            lines.append(f"Explanation: {q['explanation']}")
        lines.append("")

    return "\n".join(lines)


def validate_document_text(text: str) -> tuple:
    """Validate document text before processing."""
    errors = []
    warnings = []

    if not text or len(text.strip()) == 0:
        errors.append("❌ Document appears to be empty")

    if len(text) < 100:
        errors.append("❌ Document is too short. Minimum 100 characters required")

    if len(text) > 500000:
        warnings.append("⚠️ Document is very large. Only first 3000 characters will be used for AI")

    if len(text.split()) < 20:
        errors.append("❌ Document has too few words. Minimum 20 words required")

    non_printable = sum(1 for c in text if not c.isprintable() and c not in '\n\r\t')
    if non_printable > len(text) * 0.1:
        warnings.append("⚠️ Document may contain formatting issues or binary content")

    return errors, warnings