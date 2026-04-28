import json
import os
from tkinter import *
from tkinter import messagebox, ttk

DATA_FILE = "books.json"

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker")
        self.root.geometry("800x500")

        self.books = []
        self.load_data()

        # Поля ввода
        input_frame = LabelFrame(root, text="Добавить книгу", padx=10, pady=10)
        input_frame.pack(pady=10, padx=10, fill="x")

        Label(input_frame, text="Название:").grid(row=0, column=0, sticky="w")
        self.title_entry = Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=2)

        Label(input_frame, text="Автор:").grid(row=1, column=0, sticky="w")
        self.author_entry = Entry(input_frame, width=30)
        self.author_entry.grid(row=1, column=1, padx=5, pady=2)

        Label(input_frame, text="Жанр:").grid(row=2, column=0, sticky="w")
        self.genre_entry = Entry(input_frame, width=30)
        self.genre_entry.grid(row=2, column=1, padx=5, pady=2)

        Label(input_frame, text="Страниц:").grid(row=3, column=0, sticky="w")
        self.pages_entry = Entry(input_frame, width=30)
        self.pages_entry.grid(row=3, column=1, padx=5, pady=2)

        add_btn = Button(input_frame, text="Добавить книгу", command=self.add_book)
        add_btn.grid(row=4, column=0, columnspan=2, pady=10)

        # Фильтры
        filter_frame = LabelFrame(root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(pady=5, padx=10, fill="x")

        Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0, sticky="w")
        self.genre_filter = Entry(filter_frame, width=20)
        self.genre_filter.grid(row=0, column=1, padx=5)
        self.genre_filter.bind("<KeyRelease>", lambda e: self.apply_filters())

        Label(filter_frame, text="Страниц больше:").grid(row=1, column=0, sticky="w")
        self.pages_filter = Entry(filter_frame, width=20)
        self.pages_filter.grid(row=1, column=1, padx=5)
        self.pages_filter.bind("<KeyRelease>", lambda e: self.apply_filters())

        # Таблица
        columns = ("title", "author", "genre", "pages")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        self.tree.heading("title", text="Название")
        self.tree.heading("author", text="Автор")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("pages", text="Страниц")
        self.tree.column("title", width=200)
        self.tree.column("author", width=150)
        self.tree.column("genre", width=150)
        self.tree.column("pages", width=80)

        scrollbar = Scrollbar(root, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(pady=10, padx=10, fill="both", expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Кнопки Save/Load (автосохранение при добавлении, но можно и отдельно)
        btn_frame = Frame(root)
        btn_frame.pack(pady=5)
        Button(btn_frame, text="Сохранить в JSON", command=self.save_data).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Загрузить из JSON", command=self.load_data).pack(side=LEFT, padx=5)

        self.update_table()

    def add_book(self):
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_entry.get().strip()
        pages_str = self.pages_entry.get().strip()

        if not title or not author or not genre or not pages_str:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        try:
            pages = int(pages_str)
            if pages <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом!")
            return

        new_book = {
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages
        }
        self.books.append(new_book)
        self.save_data()
        self.clear_entries()
        self.apply_filters()

    def clear_entries(self):
        self.title_entry.delete(0, END)
        self.author_entry.delete(0, END)
        self.genre_entry.delete(0, END)
        self.pages_entry.delete(0, END)

    def apply_filters(self):
        genre_filter = self.genre_filter.get().strip().lower()
        pages_filter_str = self.pages_filter.get().strip()

        filtered = self.books[:]

        if genre_filter:
            filtered = [b for b in filtered if genre_filter in b["genre"].lower()]

        if pages_filter_str:
            try:
                pages_min = int(pages_filter_str)
                filtered = [b for b in filtered if b["pages"] > pages_min]
            except ValueError:
                pass

        self.update_table(filtered)

    def update_table(self, books_list=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        if books_list is None:
            books_list = self.books

        for book in books_list:
            self.tree.insert("", END, values=(book["title"], book["author"], book["genre"], book["pages"]))

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Сохранение", f"Данные сохранены в {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.books = json.load(f)
            self.apply_filters()
            messagebox.showinfo("Загрузка", f"Загружено {len(self.books)} книг")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки: {e}")

if __name__ == "__main__":
    root = Tk()
    app = BookTracker(root)
    root.mainloop()