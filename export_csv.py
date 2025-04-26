import pandas as pd
import sqlite3

def export_catalog_csv():
    conn = sqlite3.connect('library.db')
    query = '''
    SELECT 
        books.title AS Назва,
        books.year AS Рік,
        types.name AS Вид,
        storage.shelf AS Шафа,
        storage.position AS Полиця,
        GROUP_CONCAT(DISTINCT authors.name) AS Автори,
        GROUP_CONCAT(DISTINCT genres.name) AS Жанри
    FROM books
    LEFT JOIN types ON books.type_id = types.id
    LEFT JOIN storage ON books.storage_id = storage.id
    LEFT JOIN book_authors ON books.id = book_authors.book_id
    LEFT JOIN authors ON book_authors.author_id = authors.id
    LEFT JOIN book_genres ON books.id = book_genres.book_id
    LEFT JOIN genres ON book_genres.genre_id = genres.id
    GROUP BY books.id
    '''
    df = pd.read_sql(query, conn)
    df.to_csv('library_catalog.csv', index=False, encoding='utf-8-sig')
    conn.close()
