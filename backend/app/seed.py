import sqlite3

from app.db import transaction

TOTAL_BUDGET = 1000  # lakh, i.e. 10 Cr per team

TEAMS = ["Panjim Pirates", "Margao Mavericks", "Vasco Vikings", "Calangute Chargers"]

# name, skill, base price (lakh)
PLAYERS = [
    ("Aarav Naik", "batting", 200),
    ("Kavya Dessai", "bowling", 150),
    ("Rohan Fernandes", "both", 150),
    ("Ishaan Kamat", "batting", 100),
    ("Sneha Gaonkar", "bowling", 100),
    ("Arjun Nair", "both", 100),
    ("Tanvi Prabhu", "batting", 75),
    ("Kabir D'Souza", "bowling", 75),
    ("Meera Shetye", "both", 50),
    ("Vivaan Sawant", "batting", 50),
    ("Ananya Pereira", "bowling", 50),
    ("Siddharth Borkar", "both", 30),
    ("Riya Rodrigues", "batting", 30),
    ("Neel Parab", "bowling", 20),
    ("Diya Kerkar", "both", 20),
    ("Aditya Menon", "batting", 20),
]


def seed_if_empty(conn: sqlite3.Connection) -> None:
    with transaction(conn):
        if conn.execute("SELECT 1 FROM teams LIMIT 1").fetchone():
            return
        conn.executemany(
            "INSERT INTO teams (name, total_budget, remaining_budget) VALUES (?, ?, ?)",
            [(name, TOTAL_BUDGET, TOTAL_BUDGET) for name in TEAMS],
        )
        conn.executemany("INSERT INTO players (name, skill, base_price) VALUES (?, ?, ?)", PLAYERS)
