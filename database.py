import sqlite3

DB_NAME = 'library.db'

def create_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.executescript("""
        CREATE TABLE IF NOT EXISTS authors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        );

        CREATE TABLE IF NOT EXISTS genres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        );

        CREATE TABLE IF NOT EXISTS types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        );

        CREATE TABLE IF NOT EXISTS storage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shelf TEXT,
            position TEXT
        );

        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            year INTEGER,
            type_id INTEGER,
            storage_id INTEGER,
            FOREIGN KEY (type_id) REFERENCES types(id),
            FOREIGN KEY (storage_id) REFERENCES storage(id)
        );

        CREATE TABLE IF NOT EXISTS book_authors (
            book_id INTEGER,
            author_id INTEGER,
            FOREIGN KEY (book_id) REFERENCES books(id),
            FOREIGN KEY (author_id) REFERENCES authors(id)
        );

        CREATE TABLE IF NOT EXISTS book_genres (
            book_id INTEGER,
            genre_id INTEGER,
            FOREIGN KEY (book_id) REFERENCES books(id),
            FOREIGN KEY (genre_id) REFERENCES genres(id)
        );

        CREATE TABLE IF NOT EXISTS readers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        );

        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            reader_id INTEGER,
            issue_date TEXT,
            return_date TEXT,
            FOREIGN KEY (book_id) REFERENCES books(id),
            FOREIGN KEY (reader_id) REFERENCES readers(id)
        );
        """)

def execute_query(query, params=()):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute(query, params)
        conn.commit()
        return c.fetchall()
