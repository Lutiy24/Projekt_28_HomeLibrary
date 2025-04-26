# Проект 28, зробив Олександр Лютий
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database import execute_query
import sqlite3
from export_csv import export_catalog_csv

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Домашня бібліотека")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f0f0")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        # Створення вкладок
        self.create_books_tab()
        self.create_authors_tab()
        self.create_genres_tab()
        self.create_types_tab()
        self.create_storage_tab()
        self.create_readers_tab()
        self.create_issues_tab()
    def create_books_tab(self):
        self.books_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.books_tab, text="Книги")

        self.book_tree = ttk.Treeview(self.books_tab, columns=("ID", "Назва", "Рік", "Вид", "Шафа", "Полиця", "Автори", "Жанри"), show="headings")
        for col in self.book_tree["columns"]:
            self.book_tree.heading(col, text=col)
            self.book_tree.column(col, width=150)


        self.book_tree.pack(expand=True, fill="both", pady=10)

        btn_frame = ttk.Frame(self.books_tab)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Додати книгу", command=self.add_book).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Редагувати книгу", command=self.edit_book).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Видалити книгу", command=self.delete_book).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Оновити список", command=self.load_books).grid(row=0, column=3, padx=5)
        ttk.Button(btn_frame, text="Пошук книги", command=self.search_books).grid(row=0, column=4, padx=5)
        ttk.Button(btn_frame, text="Експорт у CSV", command=export_catalog_csv).grid(row=0, column=5, padx=5)

        self.load_books()

    def load_books(self):
        for i in self.book_tree.get_children():
            self.book_tree.delete(i)
        
        books = execute_query('''
            SELECT 
                books.id, books.title, books.year, 
                types.name AS type_name,
                storage.shelf,
                storage.position,
                (SELECT GROUP_CONCAT(authors.name, ', ') 
                 FROM book_authors 
                 JOIN authors ON book_authors.author_id = authors.id 
                 WHERE book_authors.book_id = books.id) AS authors,
                (SELECT GROUP_CONCAT(genres.name, ', ') 
                 FROM book_genres 
                 JOIN genres ON book_genres.genre_id = genres.id 
                 WHERE book_genres.book_id = books.id) AS genres
            FROM books
            LEFT JOIN types ON books.type_id = types.id
            LEFT JOIN storage ON books.storage_id = storage.id
        ''')
        
        for book in books:
            self.book_tree.insert("", "end", values=book)

    def add_book(self):
        self.book_window()

    def edit_book(self):
        selected = self.book_tree.selection()
        if not selected:
            messagebox.showerror("Помилка", "Оберіть книгу для редагування.")
            return
        book_id = self.book_tree.item(selected[0])['values'][0]
        self.book_window(book_id)

    def delete_book(self):
        selected = self.book_tree.selection()
        if not selected:
            messagebox.showerror("Помилка", "Оберіть книгу для видалення.")
            return
        book_id = self.book_tree.item(selected[0])['values'][0]
        execute_query('DELETE FROM books WHERE id = ?', (book_id,))
        execute_query('DELETE FROM book_authors WHERE book_id = ?', (book_id,))
        execute_query('DELETE FROM book_genres WHERE book_id = ?', (book_id,))
        self.load_books()
        messagebox.showinfo("Успіх", "Книгу видалено.")

    def book_window(self, book_id=None):
        win = tk.Toplevel(self.root)
        win.title("Додавання / Редагування книги")
        win.geometry("500x700")
        win.configure(bg="#f0f0f0")

        frame = ttk.Frame(win, padding=20)
        frame.pack(expand=True, fill="both")

        # Назва книги
        ttk.Label(frame, text="Назва книги:", font=('Arial', 12, 'bold')).pack(anchor="w", pady=(10, 0))
        title_entry = ttk.Entry(frame, font=('Arial', 11))
        title_entry.pack(fill="x", pady=5)

        # Рік видання
        ttk.Label(frame, text="Рік:", font=('Arial', 12, 'bold')).pack(anchor="w", pady=(10, 0))
        year_entry = ttk.Entry(frame, font=('Arial', 11))
        year_entry.pack(fill="x", pady=5)

        # Вид книги (Combobox)
        ttk.Label(frame, text="Вид книги:", font=('Arial', 12, 'bold')).pack(anchor="w", pady=(10, 0))
        types = execute_query('SELECT id, name FROM types')
        type_data = [(t[0], t[1]) for t in types]
        type_combobox = ttk.Combobox(frame, values=[f"{t_id}: {t_name}" for t_id, t_name in type_data], state="readonly", font=('Arial', 11))
        type_combobox.pack(fill="x", pady=5)


        # Місце зберігання (Combobox)
        ttk.Label(frame, text="Місце зберігання:", font=('Arial', 12, 'bold')).pack(anchor="w", pady=(10, 0))
        storages = execute_query('SELECT id, shelf, position FROM storage')
        storage_data = [(s[0], f"Шафа {s[1]}, Полиця {s[2]}") for s in storages]
        storage_combobox = ttk.Combobox(frame, values=[f"{s_id}: {s_desc}" for s_id, s_desc in storage_data], state="readonly", font=('Arial', 11))
        storage_combobox.pack(fill="x", pady=5)


        # Автори
        ttk.Label(frame, text="Автори:", font=('Arial', 12, 'bold')).pack(anchor="w", pady=(15, 5))
        authors = execute_query('SELECT id, name FROM authors')
        author_data = [(a[0], a[1]) for a in authors]
        authors_listbox = tk.Listbox(frame, selectmode=tk.MULTIPLE, exportselection=False, height=6, font=('Arial', 10))
        for a_id, a_name in author_data:
            authors_listbox.insert(tk.END, f"{a_id}: {a_name}")
        authors_listbox.pack(fill="both", pady=5)

        # Жанри
        ttk.Label(frame, text="Жанри:", font=('Arial', 12, 'bold')).pack(anchor="w", pady=(15, 5))
        genres = execute_query('SELECT id, name FROM genres')
        genre_data = [(g[0], g[1]) for g in genres]
        genres_listbox = tk.Listbox(frame, selectmode=tk.MULTIPLE, exportselection=False, height=6, font=('Arial', 10))
        for g_id, g_name in genre_data:
            genres_listbox.insert(tk.END, f"{g_id}: {g_name}")
        genres_listbox.pack(fill="both", pady=5)

    # Функція збереження
        def save():
            title = title_entry.get()
            year = year_entry.get()

            selected_type = type_combobox.get()
            if selected_type:
               type_id = int(selected_type.split(":")[0])
            else:
                type_id = None

            selected_storage = storage_combobox.get()
            if selected_storage:
                storage_id = int(selected_storage.split(":")[0])
            else:
                storage_id = None

            selected_authors_indices = authors_listbox.curselection()
            selected_author_ids = [author_data[i][0] for i in selected_authors_indices]

            selected_genres_indices = genres_listbox.curselection()
            selected_genre_ids = [genre_data[i][0] for i in selected_genres_indices]

            if not title or not year.isdigit():
                messagebox.showerror("Помилка", "Заповніть всі текстові поля правильно.")
                return

            if not selected_genre_ids:
                messagebox.showerror("Помилка", "Оберіть хоча б один жанр.")
                return

            if book_id:
                # Оновлення існуючої книги
                execute_query('UPDATE books SET title=?, year=?, type_id=?, storage_id=? WHERE id=?',
                             (title, int(year), type_id, storage_id, book_id))

                execute_query('DELETE FROM book_authors WHERE book_id=?', (book_id,))
                for author_id in selected_author_ids:
                    execute_query('INSERT INTO book_authors (book_id, author_id) VALUES (?, ?)', (book_id, author_id))

                execute_query('DELETE FROM book_genres WHERE book_id=?', (book_id,))
                for genre_id in selected_genre_ids:
                    execute_query('INSERT INTO book_genres (book_id, genre_id) VALUES (?, ?)', (book_id, genre_id))
            else:
                # Додавання нової книги з авторами та жанрами в одному з'єднанні
                conn = sqlite3.connect('library.db')
                c = conn.cursor()
                c.execute('INSERT INTO books (title, year, type_id, storage_id) VALUES (?,?,?,?)',
                         (title, int(year), type_id, storage_id))
                new_book_id = c.lastrowid
 
                for author_id in selected_author_ids:
                    c.execute('INSERT INTO book_authors (book_id, author_id) VALUES (?, ?)', (new_book_id, author_id))
                for genre_id in selected_genre_ids:
                    c.execute('INSERT INTO book_genres (book_id, genre_id) VALUES (?, ?)', (new_book_id, genre_id))

                conn.commit()
                conn.close()

            self.load_books()
            win.destroy()

        # Кнопка збереження
        ttk.Button(frame, text="Зберегти книгу", command=save, style="Accent.TButton").pack(pady=20)

    def search_books(self):
        keyword = simpledialog.askstring("Пошук", "Введіть назву або частину назви книги:")
        if keyword:
            for i in self.book_tree.get_children():
                self.book_tree.delete(i)
            books = execute_query('''
                SELECT books.id, books.title, books.year, types.name, storage.shelf, storage.position
                FROM books
                LEFT JOIN types ON books.type_id = types.id
                LEFT JOIN storage ON books.storage_id = storage.id
                WHERE books.title LIKE ?
            ''', (f'%{keyword}%',))
            for book in books:
                self.book_tree.insert("", "end", values=book)
    def create_authors_tab(self):
        self.authors_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.authors_tab, text="Автори")

        self.author_tree = ttk.Treeview(self.authors_tab, columns=("ID", "Ім'я"), show="headings")
        for col in self.author_tree["columns"]:
            self.author_tree.heading(col, text=col)
            self.author_tree.column(col, width=200)
        self.author_tree.pack(expand=True, fill="both", pady=10)

        btn_frame = ttk.Frame(self.authors_tab)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Додати автора", command=self.add_author).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Редагувати автора", command=self.edit_author).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Видалити автора", command=self.delete_author).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Оновити список", command=self.load_authors).grid(row=0, column=3, padx=5)

        self.load_authors()

    def load_authors(self):
        for i in self.author_tree.get_children():
            self.author_tree.delete(i)
        authors = execute_query('SELECT * FROM authors')
        for author in authors:
            self.author_tree.insert("", "end", values=author)

    def add_author(self):
        name = simpledialog.askstring("Додати автора", "Введіть ім'я автора:")
        if name:
            execute_query('INSERT INTO authors (name) VALUES (?)', (name,))
            self.load_authors()

    def edit_author(self):
        selected = self.author_tree.selection()
        if not selected:
            messagebox.showerror("Помилка", "Оберіть автора для редагування.")
            return
        author_id = self.author_tree.item(selected[0])['values'][0]
        name = simpledialog.askstring("Редагувати автора", "Введіть нове ім'я автора:")
        if name:
            execute_query('UPDATE authors SET name = ? WHERE id = ?', (name, author_id))
            self.load_authors()

    def delete_author(self):
        selected = self.author_tree.selection()
        if not selected:
            messagebox.showerror("Помилка", "Оберіть автора для видалення.")
            return
        author_id = self.author_tree.item(selected[0])['values'][0]
        execute_query('DELETE FROM authors WHERE id = ?', (author_id,))
        self.load_authors()
    def create_genres_tab(self):
        self.genres_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.genres_tab, text="Жанри")

        self.genre_tree = ttk.Treeview(self.genres_tab, columns=("ID", "Назва"), show="headings")
        for col in self.genre_tree["columns"]:
            self.genre_tree.heading(col, text=col)
            self.genre_tree.column(col, width=200)
        self.genre_tree.pack(expand=True, fill="both", pady=10)

        btn_frame = ttk.Frame(self.genres_tab)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Додати жанр", command=self.add_genre).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Редагувати жанр", command=self.edit_genre).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Видалити жанр", command=self.delete_genre).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Оновити список", command=self.load_genres).grid(row=0, column=3, padx=5)

        self.load_genres()

    def load_genres(self):
        for i in self.genre_tree.get_children():
            self.genre_tree.delete(i)
        genres = execute_query('SELECT * FROM genres')
        for genre in genres:
            self.genre_tree.insert("", "end", values=genre)

    def add_genre(self):
        name = simpledialog.askstring("Додати жанр", "Введіть назву жанру:")
        if name:
            execute_query('INSERT INTO genres (name) VALUES (?)', (name,))
            self.load_genres()

    def edit_genre(self):
        selected = self.genre_tree.selection()
        if not selected:
            messagebox.showerror("Помилка", "Оберіть жанр для редагування.")
            return
        genre_id = self.genre_tree.item(selected[0])['values'][0]
        name = simpledialog.askstring("Редагувати жанр", "Введіть нову назву жанру:")
        if name:
            execute_query('UPDATE genres SET name = ? WHERE id = ?', (name, genre_id))
            self.load_genres()

    def delete_genre(self):
        selected = self.genre_tree.selection()
        if not selected:
            messagebox.showerror("Помилка", "Оберіть жанр для видалення.")
            return
        genre_id = self.genre_tree.item(selected[0])['values'][0]
        execute_query('DELETE FROM genres WHERE id = ?', (genre_id,))
        self.load_genres()
    def create_types_tab(self):
        self.types_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.types_tab, text="Види")

        self.type_tree = ttk.Treeview(self.types_tab, columns=("ID", "Назва"), show="headings")
        for col in self.type_tree["columns"]:
            self.type_tree.heading(col, text=col)
            self.type_tree.column(col, width=200)
        self.type_tree.pack(expand=True, fill="both", pady=10)

        btn_frame = ttk.Frame(self.types_tab)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Додати вид", command=self.add_type).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Редагувати вид", command=self.edit_type).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Видалити вид", command=self.delete_type).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Оновити список", command=self.load_types).grid(row=0, column=3, padx=5)

        self.load_types()

    def load_types(self):
        for i in self.type_tree.get_children():
            self.type_tree.delete(i)
        types = execute_query('SELECT * FROM types')
        for t in types:
            self.type_tree.insert("", "end", values=t)

    def add_type(self):
        name = simpledialog.askstring("Додати вид", "Введіть назву виду:")
        if name:
            execute_query('INSERT INTO types (name) VALUES (?)', (name,))
            self.load_types()

    def edit_type(self):
        selected = self.type_tree.selection()
        if not selected:
            messagebox.showerror("Помилка", "Оберіть вид для редагування.")
            return
        type_id = self.type_tree.item(selected[0])['values'][0]
        name = simpledialog.askstring("Редагувати вид", "Введіть нову назву виду:")
        if name:
            execute_query('UPDATE types SET name = ? WHERE id = ?', (name, type_id))
            self.load_types()

    def delete_type(self):
        selected = self.type_tree.selection()
        if not selected:
            messagebox.showerror("Помилка", "Оберіть вид для видалення.")
            return
        type_id = self.type_tree.item(selected[0])['values'][0]
        execute_query('DELETE FROM types WHERE id = ?', (type_id,))
        self.load_types()
    def create_storage_tab(self):
        self.storage_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.storage_tab, text="Місця зберігання")

        self.storage_tree = ttk.Treeview(self.storage_tab, columns=("ID", "Шафа", "Полиця"), show="headings")
        for col in self.storage_tree["columns"]:
            self.storage_tree.heading(col, text=col)
            self.storage_tree.column(col, width=150)
        self.storage_tree.pack(expand=True, fill="both", pady=10)

        btn_frame = ttk.Frame(self.storage_tab)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Додати місце", command=self.add_storage).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Редагувати місце", command=self.edit_storage).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Видалити місце", command=self.delete_storage).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Оновити список", command=self.load_storage).grid(row=0, column=3, padx=5)

        self.load_storage()

    def load_storage(self):
        for i in self.storage_tree.get_children():
            self.storage_tree.delete(i)
        places = execute_query('SELECT * FROM storage')
        for place in places:
            self.storage_tree.insert("", "end", values=place)

    def add_storage(self):
        win = tk.Toplevel(self.root)
        win.title("Додавання місця зберігання")
        win.geometry("400x300")
        win.configure(bg="#f0f0f0")

        frame = ttk.Frame(win, padding=20)
        frame.pack(expand=True, fill="both")

        # Введення шафи
        ttk.Label(frame, text="Шафа:", font=('Arial', 12, 'bold')).pack(anchor="w", pady=(10, 0))
        shelf_entry = ttk.Entry(frame, font=('Arial', 11))
        shelf_entry.pack(fill="x", pady=5)

        # Введення полиці
        ttk.Label(frame, text="Полиця:", font=('Arial', 12, 'bold')).pack(anchor="w", pady=(10, 0))
        position_entry = ttk.Entry(frame, font=('Arial', 11))
        position_entry.pack(fill="x", pady=5)

        def save_storage():
            shelf = shelf_entry.get()
            position = position_entry.get()

            if not shelf or not position:
                messagebox.showerror("Помилка", "Заповніть обидва поля: Шафа та Полиця.")
                return

            execute_query('INSERT INTO storage (shelf, position) VALUES (?, ?)', (shelf, position))
            self.load_storage()
            win.destroy()

        ttk.Button(frame, text="Зберегти місце", command=save_storage, style="Accent.TButton").pack(pady=20)

    def edit_storage(self):
        selected = self.storage_tree.selection()
        if not selected:
            messagebox.showerror("Помилка", "Оберіть місце для редагування.")
            return

        storage_id = self.storage_tree.item(selected[0])['values'][0]
        current_shelf = self.storage_tree.item(selected[0])['values'][1]
        current_position = self.storage_tree.item(selected[0])['values'][2]

        win = tk.Toplevel(self.root)
        win.title("Редагування місця зберігання")
        win.geometry("400x300")
        win.configure(bg="#f0f0f0")

        frame = ttk.Frame(win, padding=20)
        frame.pack(expand=True, fill="both")

        # Поле для редагування шафи
        ttk.Label(frame, text="Шафа:", font=('Arial', 12, 'bold')).pack(anchor="w", pady=(10, 0))
        shelf_entry = ttk.Entry(frame, font=('Arial', 11))
        shelf_entry.pack(fill="x", pady=5)
        shelf_entry.insert(0, current_shelf)

        # Поле для редагування полиці
        ttk.Label(frame, text="Полиця:", font=('Arial', 12, 'bold')).pack(anchor="w", pady=(10, 0))
        position_entry = ttk.Entry(frame, font=('Arial', 11))
        position_entry.pack(fill="x", pady=5)
        position_entry.insert(0, current_position)

        def update_storage():
            new_shelf = shelf_entry.get()
            new_position = position_entry.get()

            if not new_shelf or not new_position:
                messagebox.showerror("Помилка", "Заповніть обидва поля: Шафа та Полиця.")
                return

            execute_query('UPDATE storage SET shelf=?, position=? WHERE id=?', (new_shelf, new_position, storage_id))
            self.load_storage()
            win.destroy()

        ttk.Button(frame, text="Оновити місце", command=update_storage, style="Accent.TButton").pack(pady=20)

    def delete_storage(self):
        selected = self.storage_tree.selection()
        if not selected:
            messagebox.showerror("Помилка", "Оберіть місце для видалення.")
            return
        storage_id = self.storage_tree.item(selected[0])['values'][0]
        execute_query('DELETE FROM storage WHERE id=?', (storage_id,))
        self.load_storage()
    def create_readers_tab(self):
        self.readers_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.readers_tab, text="Читачі")

        self.reader_tree = ttk.Treeview(self.readers_tab, columns=("ID", "Ім'я"), show="headings")
        for col in self.reader_tree["columns"]:
            self.reader_tree.heading(col, text=col)
            self.reader_tree.column(col, width=200)
        self.reader_tree.pack(expand=True, fill="both", pady=10)

        btn_frame = ttk.Frame(self.readers_tab)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Додати читача", command=self.add_reader).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Редагувати читача", command=self.edit_reader).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Видалити читача", command=self.delete_reader).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Оновити список", command=self.load_readers).grid(row=0, column=3, padx=5)

        self.load_readers()

    def load_readers(self):
        for i in self.reader_tree.get_children():
            self.reader_tree.delete(i)
        readers = execute_query('SELECT * FROM readers')
        for reader in readers:
            self.reader_tree.insert("", "end", values=reader)

    def add_reader(self):
        name = simpledialog.askstring("Додати читача", "Введіть ім'я читача:")
        if name:
            execute_query('INSERT INTO readers (name) VALUES (?)', (name,))
            self.load_readers()

    def edit_reader(self):
        selected = self.reader_tree.selection()
        if not selected:
            messagebox.showerror("Помилка", "Оберіть читача для редагування.")
            return
        reader_id = self.reader_tree.item(selected[0])['values'][0]
        name = simpledialog.askstring("Редагувати читача", "Введіть нове ім'я читача:")
        if name:
            execute_query('UPDATE readers SET name = ? WHERE id = ?', (name, reader_id))
            self.load_readers()

    def delete_reader(self):
        selected = self.reader_tree.selection()
        if not selected:
            messagebox.showerror("Помилка", "Оберіть читача для видалення.")
            return
        reader_id = self.reader_tree.item(selected[0])['values'][0]
        execute_query('DELETE FROM readers WHERE id = ?', (reader_id,))
        self.load_readers()
    def create_issues_tab(self):
        self.issues_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.issues_tab, text="Видачі книг")

        self.issue_tree = ttk.Treeview(self.issues_tab, columns=("ID", "Книга", "Читач", "Дата видачі", "Дата повернення"), show="headings")
        for col in self.issue_tree["columns"]:
            self.issue_tree.heading(col, text=col)
            self.issue_tree.column(col, width=200)
        self.issue_tree.pack(expand=True, fill="both", pady=10)

        btn_frame = ttk.Frame(self.issues_tab)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Видати книгу", command=self.add_issue).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Повернути книгу", command=self.return_issue).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Оновити список", command=self.load_issues).grid(row=0, column=2, padx=5)

        self.load_issues()

    def load_issues(self):
        for i in self.issue_tree.get_children():
            self.issue_tree.delete(i)
        issues = execute_query('''
            SELECT issues.id, books.title, readers.name, issues.issue_date, issues.return_date
            FROM issues
            JOIN books ON issues.book_id = books.id
            JOIN readers ON issues.reader_id = readers.id
        ''')
        for issue in issues:
            self.issue_tree.insert("", "end", values=issue)

    def add_issue(self):
        win = tk.Toplevel(self.root)
        win.title("Видача книги")
        win.geometry("400x400")
        win.configure(bg="#f0f0f0")

        frame = ttk.Frame(win, padding=20)
        frame.pack(expand=True, fill="both")

        # Вибір книги
        ttk.Label(frame, text="Оберіть книгу:", font=('Arial', 12, 'bold')).pack(anchor="w", pady=(10, 0))
        books = execute_query('SELECT id, title FROM books')
        book_data = [(b[0], b[1]) for b in books]
        book_combobox = ttk.Combobox(frame, values=[f"{b_id}: {b_title}" for b_id, b_title in book_data], state="readonly", font=('Arial', 11))
        book_combobox.pack(fill="x", pady=5)

        # Вибір читача
        ttk.Label(frame, text="Оберіть читача:", font=('Arial', 12, 'bold')).pack(anchor="w", pady=(15, 0))
        readers = execute_query('SELECT id, name FROM readers')
        reader_data = [(r[0], r[1]) for r in readers]
        reader_combobox = ttk.Combobox(frame, values=[f"{r_id}: {r_name}" for r_id, r_name in reader_data], state="readonly", font=('Arial', 11))
        reader_combobox.pack(fill="x", pady=5)

        # Дата видачі
        ttk.Label(frame, text="Дата видачі (РРРР-ММ-ДД):", font=('Arial', 12, 'bold')).pack(anchor="w", pady=(15, 0))
        issue_date_entry = ttk.Entry(frame, font=('Arial', 11))
        issue_date_entry.pack(fill="x", pady=5)

        def save_issue():
            selected_book = book_combobox.get()
            selected_reader = reader_combobox.get()
            issue_date = issue_date_entry.get()

            if not selected_book or not selected_reader or not issue_date:
                messagebox.showerror("Помилка", "Заповніть всі поля.")
                return

            book_id = int(selected_book.split(":")[0])
            reader_id = int(selected_reader.split(":")[0])

            execute_query('INSERT INTO issues (book_id, reader_id, issue_date, return_date) VALUES (?,?,?,?)',
                          (book_id, reader_id, issue_date, None))
            self.load_issues()
            win.destroy()

        ttk.Button(frame, text="Видати книгу", command=save_issue, style="Accent.TButton").pack(pady=20)


    def return_issue(self):
        selected = self.issue_tree.selection()
        if not selected:
            messagebox.showerror("Помилка", "Оберіть запис видачі для повернення.")
            return
        issue_id = self.issue_tree.item(selected[0])['values'][0]
        return_date = simpledialog.askstring("Дата повернення", "Введіть дату повернення (рік-місяць-день):")
        if return_date:
            execute_query('UPDATE issues SET return_date = ? WHERE id = ?', (return_date, issue_id))
            self.load_issues()
