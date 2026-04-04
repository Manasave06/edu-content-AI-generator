import json
import re
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

load_dotenv()

def get_llm():
    """Initialize Groq LLM."""
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

def parse_json(raw: str) -> list:
    """Safely parse JSON from LLM response."""
    clean = re.sub(r"```json|```", "", raw, flags=re.MULTILINE).strip()
    return json.loads(clean)

def generate_quiz(text: str, num_questions: int) -> list:
    """Generate multiple choice questions from text."""
    llm = get_llm()
    prompt = f"""
You are an expert educator. Generate exactly {num_questions} multiple-choice questions from the text below.

Return ONLY a valid JSON array. Each object must have:
- "question": the question string
- "options": list of exactly 4 answer strings
- "answer": the correct option (must exactly match one item in options)
- "explanation": brief explanation of the correct answer

Text:
{text[:3000]}

Return ONLY the JSON array. No extra text. No markdown.
"""
    response = llm.invoke([
        SystemMessage(content="You are a quiz generator. Output only valid JSON arrays."),
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