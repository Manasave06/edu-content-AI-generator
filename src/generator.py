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
    llm = get_llm()
    difficulty_instructions = {
        "Easy": """
EASY LEVEL RULES:
- Ask ONLY basic definitions and simple facts
- Questions start with: What is, Which is, Define
- Answer directly stated in text
- Wrong options obviously incorrect
""",
        "Medium": """
MEDIUM LEVEL RULES:
- Ask HOW things work and WHY things happen
- Questions start with: How does, Why is, What happens when
- Requires understanding not just memorization
""",
        "Hard": """
HARD LEVEL RULES:
- Ask ANALYSIS, COMPARISON, EVALUATION
- Questions start with: Analyze, Compare, Evaluate
- All 4 options seem plausible
- Challenge even students who studied deeply
"""
    }

    prompt = f"""
You are an expert university professor creating a {difficulty.upper()} level exam.

{difficulty_instructions[difficulty]}

TASK: Generate EXACTLY {num_questions} questions at {difficulty} level.

CRITICAL RULES:
- NEVER ask about: emails, phone numbers, author names, institution names,
  dates of publication, journal names, page numbers, contact details
- ONLY ask about: concepts, mechanisms, processes, classifications,
  applications, effects, definitions, comparisons

Return ONLY a valid JSON array with {num_questions} objects:
- "question": the question string
- "options": list of exactly 4 answer strings
- "answer": correct option (must exactly match one item in options)
- "explanation": detailed explanation of why this is correct
- "difficulty": "{difficulty}"

Text:
{text[:3000]}

Return ONLY the JSON array. No extra text. No markdown.
"""
    response = llm.invoke([
        SystemMessage(content=f"""You are a strict {difficulty} level exam question generator.
Easy = definitions only. Medium = understanding/application. Hard = analysis/critical thinking.
Never mix difficulty levels. Never ask about document metadata.
Output only valid JSON arrays."""),
        HumanMessage(content=prompt)
    ])
    return parse_json(response.content.strip())


def generate_true_false(text: str, num_questions: int, difficulty: str = "Medium") -> list:
    llm = get_llm()
    difficulty_instructions = {
        "Easy": "Simple factual statements directly from text. Obviously true or false.",
        "Medium": "Statements about processes and relationships. Requires understanding. Include tricky statements.",
        "Hard": "Complex statements combining multiple concepts. Subtle errors requiring deep knowledge to catch."
    }

    prompt = f"""
You are an expert professor creating {difficulty.upper()} level True/False questions.

Difficulty guide: {difficulty_instructions[difficulty]}

Generate EXACTLY {num_questions} True/False statements at {difficulty} level.

RULES:
- Follow the {difficulty} level rules strictly
- Mix of True and False answers roughly 50/50
- NEVER ask about emails, authors, institutions, dates or document metadata
- Each statement must test a DIFFERENT concept

Return ONLY a valid JSON array:
- "question": a clear statement that is true or false
- "answer": exactly "True" or "False"
- "explanation": why the statement is true or false
- "difficulty": "{difficulty}"

Text:
{text[:3000]}

Return ONLY the JSON array. No extra text. No markdown.
"""
    response = llm.invoke([
        SystemMessage(content=f"You are a {difficulty} level True/False generator. Output only valid JSON arrays."),
        HumanMessage(content=prompt)
    ])
    return parse_json(response.content.strip())


def generate_fill_blanks(text: str, num_questions: int, difficulty: str = "Medium") -> list:
    llm = get_llm()
    difficulty_instructions = {
        "Easy": "Blank is a KEY TERM directly from text. Very obvious. One word answer.",
        "Medium": "Blank is a CONCEPT or PROCESS name. Requires understanding. One or two word answer.",
        "Hard": "Blank is a SPECIFIC TECHNICAL TERM. Multiple words could fit but only one is correct."
    }

    prompt = f"""
You are an expert professor creating {difficulty.upper()} level Fill-in-the-Blank questions.

Difficulty guide: {difficulty_instructions[difficulty]}

Generate EXACTLY {num_questions} fill-in-the-blank questions at {difficulty} level.

RULES:
- Use _____ to indicate the blank
- NEVER ask about emails, authors, institutions, dates or document metadata
- Each question must test a DIFFERENT concept

Return ONLY a valid JSON array:
- "question": sentence with _____ for the blank
- "answer": correct word or phrase
- "hint": helpful hint for the student
- "explanation": why this is the correct answer
- "difficulty": "{difficulty}"

Text:
{text[:3000]}

Return ONLY the JSON array. No extra text. No markdown.
"""
    response = llm.invoke([
        SystemMessage(content=f"You are a {difficulty} level fill-in-the-blank generator. Output only valid JSON arrays."),
        HumanMessage(content=prompt)
    ])
    return parse_json(response.content.strip())


def generate_flashcards(text: str, num_cards: int) -> list:
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


def generate_study_content(text: str) -> dict:
    llm = get_llm()
    prompt = f"""
You are an expert educator. Analyze the text and generate comprehensive study content.

Return ONLY a valid JSON object with these exact keys:
- "summary": A clear 3-4 sentence summary of the main topic
- "key_points": List of 6-8 most important points to remember
- "mind_map": Dictionary with main topic as key and list of subtopics as value
- "exam_tips": List of 4-5 tips for answering exam questions on this topic
- "difficult_terms": List of objects with "term" and "definition" for 5 hard words
- "one_liner": One powerful sentence that captures the entire topic

Text:
{text[:3000]}

Return ONLY the JSON object. No extra text. No markdown.
"""
    response = llm.invoke([
        SystemMessage(content="You are a study content generator. Output only valid JSON."),
        HumanMessage(content=prompt)
    ])
    raw = response.content.strip()
    clean = re.sub(r"```json|```", "", raw, flags=re.MULTILINE).strip()
    return json.loads(clean)


def chat_with_doc(text: str, question: str, history: list) -> str:
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