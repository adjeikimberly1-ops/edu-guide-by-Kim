import sqlite3
import json
from datetime import datetime, date
from pathlib import Path

# ---------------------------------------------------------------------------
# Database setup — stored in the project root
# ---------------------------------------------------------------------------
DB_PATH = Path(__file__).parent.parent / "eduguide_progress.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create all tables if they don't exist yet."""
    conn = get_connection()
    cursor = conn.cursor()

    # Topics studied
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topics_studied (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            studied_at TEXT NOT NULL
        )
    """)

    # Quiz scores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            score INTEGER,
            total INTEGER,
            level TEXT,
            taken_at TEXT NOT NULL
        )
    """)

    # Roadmaps generated
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roadmaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Daily streaks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS streaks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_date TEXT NOT NULL UNIQUE
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Write helpers
# ---------------------------------------------------------------------------
def log_topic(topic: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO topics_studied (topic, studied_at) VALUES (?, ?)",
        (topic.strip().lower(), datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    _log_streak()


def log_quiz_score(topic: str, score: int, total: int, level: str = "adaptive"):
    conn = get_connection()
    conn.execute(
        "INSERT INTO quiz_scores (topic, score, total, level, taken_at) VALUES (?, ?, ?, ?, ?)",
        (topic.strip().lower(), score, total, level, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    _log_streak()


def log_roadmap(goal: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO roadmaps (goal, created_at) VALUES (?, ?)",
        (goal.strip(), datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    _log_streak()


def _log_streak():
    """Record today's date for streak tracking (ignores duplicates)."""
    today = date.today().isoformat()
    conn = get_connection()
    conn.execute(
        "INSERT OR IGNORE INTO streaks (activity_date) VALUES (?)", (today,)
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Read helpers
# ---------------------------------------------------------------------------
def get_progress_summary() -> dict:
    conn = get_connection()
    cursor = conn.cursor()

    # Topics
    cursor.execute("SELECT topic, studied_at FROM topics_studied ORDER BY studied_at DESC LIMIT 10")
    topics = [{"topic": r[0], "studied_at": r[1]} for r in cursor.fetchall()]

    # Quiz scores
    cursor.execute("SELECT topic, score, total, level, taken_at FROM quiz_scores ORDER BY taken_at DESC LIMIT 10")
    quizzes = [{"topic": r[0], "score": r[1], "total": r[2], "level": r[3], "taken_at": r[4]} for r in cursor.fetchall()]

    # Roadmaps
    cursor.execute("SELECT goal, created_at FROM roadmaps ORDER BY created_at DESC LIMIT 10")
    roadmaps = [{"goal": r[0], "created_at": r[1]} for r in cursor.fetchall()]

    # Streak — count consecutive days ending today
    cursor.execute("SELECT activity_date FROM streaks ORDER BY activity_date DESC")
    dates = [r[0] for r in cursor.fetchall()]
    streak = _calculate_streak(dates)

    conn.close()

    return {
        "topics": topics,
        "quizzes": quizzes,
        "roadmaps": roadmaps,
        "streak_days": streak,
        "total_topics": len(topics),
        "total_quizzes": len(quizzes),
        "total_roadmaps": len(roadmaps),
    }


def _calculate_streak(dates: list) -> int:
    """Count consecutive day streak from today backwards."""
    if not dates:
        return 0
    streak = 0
    check = date.today()
    for d in dates:
        if d == check.isoformat():
            streak += 1
            check = date.fromordinal(check.toordinal() - 1)
        else:
            break
    return streak


# Initialise DB on import
init_db()
