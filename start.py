# Проект 28, зробив Олександр Лютий
from gui import LibraryApp
import tkinter as tk
from database import create_db

if __name__ == "__main__":
    create_db()
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()
