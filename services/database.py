import sqlite3
from pathlib import Path


# Database location
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "datatrust.db"


def get_connection():
    """
    Create and return a connection to the SQLite database.
    """

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=10
    )

    # Enable WAL mode to reduce database locking problems
    connection.execute("PRAGMA journal_mode=WAL")

    # Allows columns to be accessed by name
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """
    Create all required database tables if they don't already exist.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # ---------------------------------
        # DATASETS TABLE
        # ---------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_records INTEGER,
                quality_score REAL
            )
        """)

        # ---------------------------------
        # RECORDS TABLE
        # ---------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_id INTEGER NOT NULL,
                customer_id TEXT,
                name TEXT,
                email TEXT,
                phone TEXT,
                city TEXT,
                latitude REAL,
                longitude REAL,

                FOREIGN KEY (dataset_id)
                REFERENCES datasets(id)
            )
        """)

        # ---------------------------------
        # ISSUES TABLE
        # ---------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_id INTEGER NOT NULL,
                record_id INTEGER,
                issue_type TEXT NOT NULL,
                description TEXT,

                FOREIGN KEY (dataset_id)
                REFERENCES datasets(id),

                FOREIGN KEY (record_id)
                REFERENCES records(id)
            )
        """)

        connection.commit()

    finally:

        connection.close()