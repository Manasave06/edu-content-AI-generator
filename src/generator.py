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

def generate_quiz(text: str, num_questions: int) -> list:
    llm = get_llm()
    prompt = f"""
You are an expert educator creating exam questions for students.

YOUR TASK: Generate exactly {num_questions} high-quality exam questions.

STRICTLY FORBIDDEN - NEVER ask about:
- Email addresses or contact information
- Author names or researcher names
- Institution or college names
- Dates of publication or submission
- Journal names or article titles
- Page numbers or volume numbers
- Phone numbers or addresses
- Funding sources or acknowledgements
- Any metadata about the document itself

ONLY ASK ABOUT:
- Scientific concepts and definitions
- Biological/chemical/medical processes
- How something works or functions
- Causes and effects
- Classification and types
- Treatment methods or applications
- Key findings and conclusions
- Important terminology
- Mechanisms and pathways

Each question MUST test actual subject knowledge.

Return ONLY a valid JSON array with exactly {num_questions} objects.
Each object must have:
- "question": exam-worthy question string
- "options": list of exactly 4 answer strings
- "answer": correct option (must exactly match one item in options)
- "explanation": why this answer is correct

Text:
{text[:3000]}

Return ONLY the JSON array. No extra text. No markdown.
"""
    response = llm.invoke([
        SystemMessage(content="""You are a strict exam question generator for students.
You ONLY create questions about subject concepts, processes, definitions and mechanisms.
You NEVER create questions about emails, authors, dates, institutions or document metadata.
Output only valid JSON arrays."""),
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