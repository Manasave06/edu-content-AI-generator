import json
import re
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

load_dotenv()

def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

def parse_json(raw: str) -> list:
    clean = re.sub(r"```json|```", "", raw, flags=re.MULTILINE).strip()
    return json.loads(clean)

def generate_quiz(text: str, num_questions: int, difficulty: str = "Medium") -> list:
    """Generate MCQ questions with difficulty level."""
    llm = get_llm()

    difficulty_guide = {
        "Easy": "basic recall questions, straightforward definitions, simple facts",
        "Medium": "application questions, cause-effect relationships, comparisons",
        "Hard": "analysis questions, complex mechanisms, multi-step reasoning, critical thinking"
    }

    prompt = f"""
You are an expert educator creating {difficulty.upper()} level exam questions for students.

DIFFICULTY: {difficulty}
DIFFICULTY GUIDE: {difficulty_guide[difficulty]}

YOUR TASK: Generate exactly {num_questions} {difficulty} level multiple-choice questions.

STRICTLY FORBIDDEN:
- Email addresses, phone numbers, contact information
- Author names, researcher names
- Institution or college names
- Dates of publication or submission
- Journal names, article titles, page numbers
- Any document metadata

ONLY ASK ABOUT:
- Scientific concepts and definitions
- Processes and mechanisms
- Causes and effects
- Classifications and types
- Applications and treatments
- Key findings and conclusions
- Important terminology

For {difficulty} level:
{"- Keep questions simple and direct" if difficulty == "Easy" else ""}
{"- Ask about understanding and application" if difficulty == "Medium" else ""}
{"- Ask about analysis, synthesis and evaluation" if difficulty == "Hard" else ""}

Return ONLY a valid JSON array with exactly {num_questions} objects:
- "question": question string
- "options": list of exactly 4 answer strings
- "answer": correct option (must match one in options exactly)
- "explanation": why this answer is correct
- "difficulty": "{difficulty}"

Text:
{text[:3000]}

Return ONLY the JSON array. No extra text. No markdown.
"""
    response = llm.invoke([
        SystemMessage(content="""You are a strict exam question generator.
Only create questions about subject concepts, not document metadata.
Output only valid JSON arrays."""),
        HumanMessage(content=prompt)
    ])
    return parse_json(response.content.strip())

def generate_true_false(text: str, num_questions: int, difficulty: str = "Medium") -> list:
    """Generate True/False questions."""
    llm = get_llm()
    prompt = f"""
You are an expert educator creating {difficulty} level True/False questions for students.

Generate exactly {num_questions} True/False questions from the text.

STRICTLY FORBIDDEN:
- Email addresses, contact info, author names
- Institution names, dates of publication
- Any document metadata

ONLY ASK ABOUT subject concepts, processes, definitions, facts.

Return ONLY a valid JSON array:
- "question": a clear statement that is either true or false
- "answer": exactly "True" or "False"
- "explanation": why the statement is true or false
- "difficulty": "{difficulty}"

Text:
{text[:3000]}

Return ONLY the JSON array. No extra text. No markdown.
"""
    response = llm.invoke([
        SystemMessage(content="You are a True/False question generator. Output only valid JSON arrays."),
        HumanMessage(content=prompt)
    ])
    return parse_json(response.content.strip())

def generate_fill_blanks(text: str, num_questions: int, difficulty: str = "Medium") -> list:
    """Generate Fill in the Blank questions."""
    llm = get_llm()
    prompt = f"""
You are an expert educator creating {difficulty} level Fill-in-the-Blank questions for students.

Generate exactly {num_questions} fill-in-the-blank questions from the text.

STRICTLY FORBIDDEN:
- Email addresses, contact info, author names
- Institution names, dates of publication
- Any document metadata

ONLY focus on subject concepts, key terms, processes, definitions.

Return ONLY a valid JSON array:
- "question": sentence with _____ where the answer goes
- "answer": the correct word or phrase that fills the blank
- "hint": a helpful hint for the student
- "explanation": brief explanation of the answer
- "difficulty": "{difficulty}"

Text:
{text[:3000]}

Return ONLY the JSON array. No extra text. No markdown.
"""
    response = llm.invoke([
        SystemMessage(content="You are a fill-in-the-blank question generator. Output only valid JSON arrays."),
        HumanMessage(content=prompt)
    ])
    return parse_json(response.content.strip())

def generate_flashcards(text: str, num_cards: int) -> list:
    """Generate flashcards from text."""
    llm = get_llm()
    prompt = f"""
You are an expert educator. Generate exactly {num_cards} flashcards from the text below.

Return ONLY a valid JSON array. Each object must have:
- "front": a concise question or key term
- "back": a clear complete answer or definition

Only include educationally valuable content.
Do NOT include emails, author names, dates, or any document metadata.

Text:
{text[:3000]}

Return ONLY the JSON array. No extra text. No markdown.
"""
    response = llm.invoke([
        SystemMessage(content="You are a flashcard generator. Output only valid JSON arrays."),
        HumanMessage(content=prompt)
    ])
    return parse_json(response.content.strip())

def chat_with_doc(text: str, question: str, history: list) -> str:
    """Answer questions about the document."""
    llm = get_llm()
    messages = [
        SystemMessage(content=f"""You are a helpful study assistant.
Answer ONLY based on the document below.
If the answer is not in the document, say: 'I could not find that in the document.'

Document:
{text[:4000]}""")
    ]
    for h in history[-3:]:
        messages.append(HumanMessage(content=h["user"]))
        messages.append(AIMessage(content=h["assistant"]))
    messages.append(HumanMessage(content=question))
    response = llm.invoke(messages)
    return response.content