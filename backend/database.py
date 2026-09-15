"""SQLite database setup and table definitions."""

import sqlite3
from pathlib import Path
from backend.config import DATABASE_PATH


def get_db_path() -> str:
    """Get the database file path."""
    return DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    """Get a synchronous SQLite connection."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Initialize all database tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'viewer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    """)

    # Audit logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            username TEXT,
            endpoint TEXT NOT NULL,
            method TEXT NOT NULL,
            request_body TEXT,
            response_body TEXT,
            status_code INTEGER,
            duration_ms REAL,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Predictions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_id TEXT UNIQUE NOT NULL,
            user_id TEXT,
            request_data TEXT NOT NULL,
            prediction_result TEXT,
            model_version TEXT DEFAULT 'v1',
            duration_ms REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Review queue table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS review_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_id TEXT NOT NULL,
            fraud_score REAL NOT NULL,
            decision_tier TEXT NOT NULL DEFAULT 'manual_review',
            status TEXT NOT NULL DEFAULT 'pending',
            analyst_id TEXT,
            analyst_decision TEXT,
            analyst_notes TEXT,
            request_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TIMESTAMP
        )
    """)

    # Monitoring metrics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monitoring_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_created ON predictions(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_pid ON predictions(prediction_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_status ON review_queue(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_monitoring_model ON monitoring_metrics(model_name, metric_name)")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
