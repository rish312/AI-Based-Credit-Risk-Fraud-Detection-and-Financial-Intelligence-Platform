"""Seed default users into the database."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db, get_connection
from backend.api.middleware.auth import hash_password


USERS = [
    {"username": "admin", "password": "admin123", "role": "admin"},
    {"username": "loan_officer", "password": "loan123", "role": "loan_officer"},
    {"username": "fraud_analyst", "password": "fraud123", "role": "fraud_analyst"},
    {"username": "compliance", "password": "comp123", "role": "compliance"},
    {"username": "viewer", "password": "viewer123", "role": "viewer"},
]


def seed_users():
    """Create default users with different roles."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    for user in USERS:
        cursor.execute("SELECT id FROM users WHERE username = ?", (user["username"],))
        if cursor.fetchone():
            print(f"  User '{user['username']}' already exists — skipping")
            continue

        pwd_hash = hash_password(user["password"])
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (user["username"], pwd_hash, user["role"]),
        )
        print(f"  ✓ Created user '{user['username']}' with role '{user['role']}'")

    conn.commit()
    conn.close()
    print("\nDone! Default credentials:")
    for u in USERS:
        print(f"  {u['username']} / {u['password']}  (role: {u['role']})")


if __name__ == "__main__":
    seed_users()