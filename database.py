import sqlite3
import json
from datetime import datetime

DB_PATH = "study_assistant.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            uploaded_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER,
            questions TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (document_id) REFERENCES documents(id)
        );

        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER,
            cards TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (document_id) REFERENCES documents(id)
        );

        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER,
            score INTEGER,
            total INTEGER,
            taken_at TEXT NOT NULL,
            FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
        );
    """)
    conn.commit()
    conn.close()

def save_document(name: str, content: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO documents (name, content, uploaded_at) VALUES (?, ?, ?)",
        (name, content, datetime.now().isoformat())
    )
    doc_id = cur.lastrowid
    conn.commit()
    conn.close()
    return doc_id

def save_quiz(document_id: int, questions: list) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO quizzes (document_id, questions, created_at) VALUES (?, ?, ?)",
        (document_id, json.dumps(questions), datetime.now().isoformat())
    )
    quiz_id = cur.lastrowid
    conn.commit()
    conn.close()
    return quiz_id

def save_flashcards(document_id: int, cards: list) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO flashcards (document_id, cards, created_at) VALUES (?, ?, ?)",
        (document_id, json.dumps(cards), datetime.now().isoformat())
    )
    card_id = cur.lastrowid
    conn.commit()
    conn.close()
    return card_id

def save_quiz_result(quiz_id: int, score: int, total: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO quiz_results (quiz_id, score, total, taken_at) VALUES (?, ?, ?, ?)",
        (quiz_id, score, total, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_all_documents():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, name, uploaded_at FROM documents ORDER BY uploaded_at DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_quiz_results():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT qr.taken_at, qr.score, qr.total, d.name
        FROM quiz_results qr
        JOIN quizzes q ON qr.quiz_id = q.id
        JOIN documents d ON q.document_id = d.id
        ORDER BY qr.taken_at DESC
        LIMIT 10
    """)
    rows = cur.fetchall()
    conn.close()
    return rows