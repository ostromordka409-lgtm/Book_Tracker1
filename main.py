import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import subprocess

# --- Конфигурация ---
DATA_FILE = "books.json"
README_FILE = "README.md"
GITHUB_REPO_URL = "https://github.com/YOUR_USERNAME/BookTracker.git"  # Замените на свой URL

# --- Класс приложения ---
class BookTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker")
        self.books = []
        self.load_books()
        self.create_widgets()
        self.update_table()

    def create_widgets(self):
        # --- Рамка для ввода ---
        frame = ttk.LabelFrame(self.root, text="Добавить новую книгу", padding="10")
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Поля ввода
        ttk.Label(frame, text="Название:").grid(row=0, column=0, sticky="w")
        self.title_entry = ttk.Entry(frame)
        self.title_entry.grid(row=0, column=1, sticky="ew", padx=5)

        ttk.Label(frame, text="Автор:").grid(row=1, column=0, sticky="w")
        self.author_entry = ttk.Entry(frame)
        self.author_entry.grid(row=1, column=1, sticky="ew", padx=5)

        ttk.Label(frame, text="Жанр:").grid(row=2, column=0, sticky="w")
        self.genre_entry = ttk.Entry(frame)
        self.genre_entry.grid(row=2, column=1, sticky="ew", padx=5)

        ttk.Label(frame, text="Страниц:").grid(row=3, column=0, sticky="w")
        self.pages_entry = ttk.Entry(frame)
        self.pages_entry.grid(row=3, column=1, sticky="ew", padx=5)

        # Кнопка добавления
        ttk.Button(frame, text="Добавить книгу", command=self.add_book).grid(
            row=4, column=0, columnspan=2, pady=10)

        # --- Фильтры ---
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding="5")
        filter_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        ttk.Label(filter_frame, text="Жанр:").grid(row=0, column=0, sticky="w")
        self.filter_genre = ttk.Entry(filter_frame)
        self.filter_genre.grid(row=0, column=1, sticky="ew", padx=5)

        ttk.Label(filter_frame, text="Страниц >:").grid(row=1, column=0, sticky="w")
        self.filter_pages = ttk.Entry(filter_frame)
        self.filter_pages.grid(row=1, column=1, sticky="ew", padx=5)

        ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(
            row=2, column=0, columnspan=2, pady=5)

        # --- Кнопки действий ---
        btn_frame = ttk.Frame(self.root)
        btn_frame.grid(row=2, column=0, pady=(5, 10), sticky="e")

        ttk.Button(btn_frame, text="Сохранить в JSON", command=self.save_books).pack(side="left", padx=5)
        
         # Кнопки Git (только если .git существует)
         if os.path.exists(".git"):
             ttk.Button(btn_frame, text="Git: Commit & Push", command=self.git_commit_push).pack(side="left", padx=5)
             # Кнопки Init и Link (для примера оставлены как есть)
             # В реальном приложении их можно сделать активными
             # и привязать к соответствующим функциям.
             # Здесь они просто для визуального отображения.
             # ...
        

    def add_book(self):
         title = self.title_entry.get().strip()
         author = self.author_entry.get().strip()
         genre = self.genre_entry.get().strip()
         pages_raw = self.pages_entry.get().strip()

         if not title or not author or not genre or not pages_raw:
             messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
             return

         if not pages_raw.isdigit():
             messagebox.showerror("Ошибка", "Количество страниц должно быть числом!")
             return

         pages = int(pages_raw)

         self.books.append({
             "title": title,
             "author": author,
             "genre": genre,
             "pages": pages
         })

         self.clear_entries()
         self.update_table()

    def clear_entries(self):
         self.title_entry.delete(0, tk.END)
         self.author_entry.delete(0, tk.END)
         self.genre_entry.delete(0, tk.END)
         self.pages_entry.delete(0, tk.END)

    def update_table(self):
         # Очищаем таблицу перед обновлением
         for i in self.tree.get_children():
             self.tree.delete(i)
         
         # Вставляем все книги из основного списка (self.books)
         for book in self.books:
             self.tree.insert("", "end", values=(book["title"], book["author"], book["genre"], book["pages"]))

    def apply_filter(self):
         filter_genre = self.filter_genre.get().strip().lower()
         
         try:
             filter_pages = int(self.filter_pages.get().strip())
         except ValueError:
             filter_pages = 0

         filtered_books = []
         for book in self.books:
             genre_match = (filter_genre == "" or filter_genre in book["genre"].lower())
             pages_match = (filter_pages == 0 or book["pages"] > filter_pages)
             
             if genre_match and pages_match:
                 filtered_books.append(book)
         
         # Обновляем таблицу с отфильтрованными данными
         for i in self.tree.get_children():
             self.tree.delete(i)
         
         for book in filtered_books:
             self.tree.insert("", "end", values=(book["title"], book["author"], book["genre"], book["pages"]))

    def save_books(self):
         try:
             with open(DATA_FILE, 'w', encoding='utf-8') as f:
                 json.dump(self.books, f, ensure_ascii=False, indent=4)
             
             # Создаем README.md при первом сохранении или обновляем его
             with open(README_FILE, 'w', encoding='utf-8') as f:
                 f.write(f"# Book Tracker\n\nТекущее количество книг: {len(self.books)}")
             
             messagebox.showinfo("Успех", f"Данные сохранены в {DATA_FILE} и {README_FILE}")
             
             if os.path.exists(".git"):
                 self.git_commit_push()
                 
         except Exception as e:
             messagebox.showerror("Ошибка сохранения", str(e))

    def load_books(self):
         if os.path.exists(DATA_FILE):
             try:
                 with open(DATA_FILE, 'r', encoding='utf-8') as f:
                     self.books = json.load(f)
                     messagebox.showinfo("Загрузка", f"Данные успешно загружены из {DATA_FILE}")
             except Exception as e:
                 messagebox.showwarning("Ошибка загрузки", f"Не удалось загрузить данные: {e}\nБудет создан новый файл.")
                 self.books = []
                 # Создаем пустой файл для избежания ошибки при следующем запуске
                 with open(DATA_FILE, 'w', encoding='utf-8') as f:
                     json.dump([], f)
         else:
             # Если файла нет — создаем пустой список и файл
             self.books = []
             with open(DATA_FILE, 'w', encoding='utf-8') as f:
                 json.dump([], f)

    def git_commit_push(self):
         try:
             subprocess.run(["git", "add", DATA_FILE], check=True)
             subprocess.run(["git", "add", README_FILE], check=True)
             
             result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
             
             if result.stdout.strip() == "":
                 messagebox.showinfo("Git Status", "Нет изменений для коммита.")
                 return

             subprocess.run(["git", "commit", "-m", "Обновление данных книг"], check=True)
             
             result_remote = subprocess.run(["git", "remote"], capture_output=True, text=True)
             
             if "origin" in result_remote.stdout:
                 subprocess.run(["git", "push"], check=True)
                 messagebox.showinfo("Git Push", "Изменения успешно отправлены в удалённый репозиторий.")
             else:
                 messagebox.showinfo("Git Info",
                     "Репозиторий не связан с удалённым (origin).\n"
                     "Используйте команду в терминале:\n"
                     f"  git remote add origin {GITHUB_REPO_URL}\n"
                     "  git push -u origin master"
                 )
                 
         except subprocess.CalledProcessError as e:
             messagebox.showerror("Ошибка Git",
                 f"Не удалось выполнить команду Git:\n"
                 f"{e.stderr}\n"
                 "Убедитесь что Git установлен и инициализирован."
              )


# --- Точка входа ---
if __name__ == "__main__":
    root = tk.Tk()
    
    # Настройка сетки для растягивания таблицы
    root.grid_rowconfigure(3, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    app = BookTrackerApp(root)
    
    root.mainloop()