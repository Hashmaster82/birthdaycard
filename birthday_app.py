#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from tkinter import Tk, Label, Button, Listbox, END, Scrollbar, RIGHT, Y, Entry, Frame, messagebox, LEFT, BOTH
try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk
except ImportError:
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk(); root.withdraw()
    messagebox.showerror(
        "Отсутствует зависимость",
        "Не найден модуль Pillow (PIL).\nУстановите его командой:\n\npip install pillow"
    )
    raise

# ==== Пути и фон по умолчанию ====
def get_desktop_path():
    if sys.platform == "win32":
        import ctypes.wintypes
        CSIDL_DESKTOP = 0
        SHGFP_TYPE_CURRENT = 0
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_DESKTOP, None, SHGFP_TYPE_CURRENT, buf)
        return buf.value
    return os.path.join(os.path.expanduser("~"), "Desktop")


def create_default_background():
    if not os.path.exists("background.jpg"):
        img = Image.new('RGB', (800, 1000), color=(255, 255, 255))
        img.save("background.jpg")
    return "background.jpg"


def get_default_font(size):
    try:
        if sys.platform == "win32":
            return ImageFont.truetype("dehinted-DarumadropOne.ttf", size)
        elif sys.platform == "darwin":
            return ImageFont.truetype("dehinted-DarumadropOne.ttf", size)
        else:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()


def generate_image(birthdays, background_path):
    try:
        img = Image.open(background_path)
        draw = ImageDraw.Draw(img)

        title_font = get_default_font(67)
        list_font = get_default_font(30)

        # === Заголовок ===
        title = "Дни рождения"
        title_width = draw.textlength(title, font=title_font)
        title_x = (img.width - title_width) // 2
        draw.text((title_x, 245), title, font=title_font, fill="black")

        # === Название месяца ===
        if birthdays:
            month_num = int(birthdays[0]["date"].split(".")[1])
            months_ru = [
                "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
            ]
            month_name = months_ru[month_num - 1]

            month_width = draw.textlength(month_name, font=title_font)
            month_x = (img.width - month_width) // 2
            draw.text((month_x, 325), month_name, font=title_font, fill="black")

        # === Сортировка по дате ===
        sorted_birthdays = sorted(
            birthdays,
            key=lambda p: (int(p["date"].split(".")[1]), int(p["date"].split(".")[0]))
        )

        # === Список именинников (нумерованный) ===
        y_position = 430
        for idx, person in enumerate(sorted_birthdays, start=1):
            text = f"{idx}. {person['name']} — {person['date']}"
            draw.text((160, y_position), text, font=list_font, fill="black")
            y_position += 50

        output_filename = os.path.join(get_desktop_path(), "birthdays_current.jpg")
        img.save(output_filename, quality=95)

        return output_filename
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось создать изображение: {e}")
        return None


class BirthdayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎂 Список именинников")

        self.background_file = create_default_background()
        self.birthdays = []
        self.preview_image = None

        # ==== Основной контейнер: слева список, справа предпросмотр ====
        main_frame = Frame(root)
        main_frame.pack(fill=BOTH, expand=True)

        left_frame = Frame(main_frame)
        left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=5)

        right_frame = Frame(main_frame)
        right_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=5)

        # ==== Форма для ввода ====
        form_frame = Frame(left_frame)
        form_frame.pack(pady=5)

        Label(form_frame, text="ФИО:").grid(row=0, column=0, padx=5)
        self.name_entry = Entry(form_frame, width=30, font=("Arial", 14))
        self.name_entry.grid(row=0, column=1, padx=5)

        Label(form_frame, text="Дата (ДД.ММ):").grid(row=0, column=2, padx=5)
        self.date_entry = Entry(form_frame, width=12, font=("Arial", 14))
        self.date_entry.grid(row=0, column=3, padx=5)

        Button(form_frame, text="Добавить", command=self.add_person).grid(row=0, column=4, padx=5)

        # ==== Список именинников ====
        Label(left_frame, text="Список именинников:").pack()
        self.scrollbar = Scrollbar(left_frame)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.listbox = Listbox(left_frame, width=50, height=10, yscrollcommand=self.scrollbar.set, font=("Arial", 12))
        self.listbox.pack()

        self.scrollbar.config(command=self.listbox.yview)

        # ==== Кнопки ====
        Button(left_frame, text="Сгенерировать картинку", command=self.generate).pack(pady=5)
        Button(left_frame, text="Сохранить список в файл", command=self.save_to_file).pack(pady=5)
        Button(left_frame, text="About", command=self.show_about).pack(pady=5)

        # ==== Предпросмотр справа ====
        Label(right_frame, text="Предпросмотр:").pack(pady=5)
        self.preview_label = Label(right_frame)
        self.preview_label.pack()

    def show_about(self):
        messagebox.showinfo("About", "Программа для генерации изображения со списком именинников текущего месяца. "
                                     "Автор: Разин Григорий, razin.grigory@yandex.ru")

    def validate_date(self, date_str):
        try:
            day, month = date_str.split(".")
            day = int(day)
            month = int(month)
            if 1 <= day <= 31 and 1 <= month <= 12:
                return True
        except:
            pass
        return False

    def add_person(self):
        name = self.name_entry.get().strip()
        date = self.date_entry.get().strip()

        if not name:
            messagebox.showwarning("Ошибка", "Введите ФИО.")
            return

        if not self.validate_date(date):
            messagebox.showwarning("Ошибка", "Дата должна быть в формате ДД.ММ и существовать.")
            return

        self.birthdays.append({"name": name, "date": date})
        self.update_listbox()

        self.name_entry.delete(0, END)
        self.date_entry.delete(0, END)

    def update_listbox(self):
        self.listbox.delete(0, END)
        if not self.birthdays:
            self.listbox.insert(END, "Список пуст.")
        else:
            # отображаем тоже отсортированный список
            sorted_birthdays = sorted(
                self.birthdays,
                key=lambda p: (int(p["date"].split(".")[1]), int(p["date"].split(".")[0]))
            )
            for idx, b in enumerate(sorted_birthdays, start=1):
                self.listbox.insert(END, f"{idx}. {b['name']} — {b['date']}")

    def update_preview(self, image_path):
        try:
            img = Image.open(image_path)
            img = img.convert("RGB")
            img.thumbnail((400, 500), Image.Resampling.LANCZOS)
            self.preview_image = ImageTk.PhotoImage(img)
            self.preview_label.config(image=self.preview_image)
            self.preview_label.image = self.preview_image
        except Exception as e:
            messagebox.showerror("Ошибка предпросмотра", f"Не удалось загрузить картинку: {e}")

    def generate(self):
        if not self.birthdays:
            messagebox.showwarning("Внимание", "Список именинников пуст.")
            return

        image_path = generate_image(self.birthdays, self.background_file)
        if image_path:
            messagebox.showinfo("Готово", f"Файл сохранён на рабочем столе:\n{image_path}")
            self.update_preview(image_path)

    def save_to_file(self):
        if not self.birthdays:
            messagebox.showwarning("Внимание", "Список пуст, сохранять нечего.")
            return
        file_path = os.path.join(os.getcwd(), "birthdays.txt")
        try:
            sorted_birthdays = sorted(
                self.birthdays,
                key=lambda p: (int(p["date"].split(".")[1]), int(p["date"].split(".")[0]))
            )
            with open(file_path, "w", encoding="utf-8") as f:
                for idx, b in enumerate(sorted_birthdays, start=1):
                    f.write(f"{idx}. {b['name']},{b['date']}\n")
            messagebox.showinfo("Сохранено", f"Список сохранён в {file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")


if __name__ == "__main__":
    root = Tk()
    app = BirthdayApp(root)
    root.mainloop()
