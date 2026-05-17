import sqlite3
import json
from datetime import datetime, date, timedelta
import os

# Use absolute path so DB persists
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "study_assistant.db")


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
            quiz_type TEXT DEFAULT 'MCQ',
            difficulty TEXT DEFAULT 'Medium',
            doc_name TEXT DEFAULT '',
            taken_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS flashcard_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_front TEXT NOT NULL,
            confidence TEXT NOT NULL,
            reviewed_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS study_streak (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            study_date TEXT NOT NULL UNIQUE,
            xp_earned INTEGER DEFAULT 0
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


def save_quiz_result(quiz_id: int, score: int, total: int,
                     quiz_type: str = "MCQ", difficulty: str = "Medium",
                     doc_name: str = ""):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Add doc_name column if not exists
    try:
        cur.execute("ALTER TABLE quiz_results ADD COLUMN doc_name TEXT DEFAULT ''")
        conn.commit()
    except:
        pass
    cur.execute(
        """INSERT INTO quiz_results
           (quiz_id, score, total, quiz_type, difficulty, doc_name, taken_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (quiz_id, score, total, quiz_type, difficulty, doc_name,
         datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    xp = score * 10
    add_study_xp(xp)


def save_flashcard_confidence(card_front: str, confidence: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO flashcard_progress (card_front, confidence, reviewed_at) VALUES (?, ?, ?)",
        (card_front, confidence, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    xp_map = {"Know it": 15, "Almost": 8, "No idea": 3}
    add_study_xp(xp_map.get(confidence, 5))


def add_study_xp(xp: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("SELECT id FROM study_streak WHERE study_date = ?", (today,))
    row = cur.fetchone()
    if row:
        cur.execute(
            "UPDATE study_streak SET xp_earned = xp_earned + ? WHERE study_date = ?",
            (xp, today)
        )
    else:
        cur.execute(
            "INSERT INTO study_streak (study_date, xp_earned) VALUES (?, ?)",
            (today, xp)
        )
    conn.commit()
    conn.close()


def get_quiz_results():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT qr.taken_at, qr.score, qr.total,
                   COALESCE(qr.doc_name, d.name, 'Unknown') as doc_name,
                   qr.quiz_type, qr.difficulty
            FROM quiz_results qr
            LEFT JOIN quizzes q ON qr.quiz_id = q.id
            LEFT JOIN documents d ON q.document_id = d.id
            ORDER BY qr.taken_at DESC
            LIMIT 20
        """)
    except:
        cur.execute("""
            SELECT taken_at, score, total, 'Document' as doc_name,
                   quiz_type, difficulty
            FROM quiz_results
            ORDER BY taken_at DESC
            LIMIT 20
        """)
    rows = cur.fetchall()
    conn.close()
    return rows


def get_study_streak():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT study_date, xp_earned FROM study_streak ORDER BY study_date DESC LIMIT 30"
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_total_xp():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT SUM(xp_earned) FROM study_streak")
    row = cur.fetchone()
    conn.close()
    return row[0] or 0


def get_flashcard_confidence_stats():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT confidence, COUNT(*) as count
        FROM flashcard_progress
        GROUP BY confidence
    """)
    rows = cur.fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}


def get_streak_count():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT study_date FROM study_streak ORDER BY study_date DESC")
    dates = [r[0] for r in cur.fetchall()]
    conn.close()
    if not dates:
        return 0
    streak = 0
    today = date.today()
    for i, d in enumerate(dates):
        try:
            study_date = date.fromisoformat(d)
            if study_date == today - timedelta(days=i):
                streak += 1
            else:
                break
        except:
            break
    return streak


def get_all_documents():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, uploaded_at FROM documents ORDER BY uploaded_at DESC"
    )
    rows = cur.fetchall()
    conn.close()
    return rows