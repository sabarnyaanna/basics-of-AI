import tkinter as tk
from tkinter import filedialog, ttk
import numpy as np
from PIL import Image, ImageTk

class Task1App:
    def __init__(self, root):
        self.root = root
        self.root.title("Завдання 1: Побудова векторів ознак")
        self.root.geometry("800x500")

        # Розмірність сітки (5 на 5)
        self.rows = 5
        self.cols = 5

        self.setup_ui()

    def setup_ui(self):
        # Панель кнопок
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=10)

        btn_browse = ttk.Button(top_frame, text="Завантажити .BMP зображення", command=self.load_image)
        btn_browse.pack(side="left")

        # Основна область
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Контейнер для зображення
        self.lbl_image = ttk.Label(main_frame, text="Оберіть файл .bmp", borderwidth=2, relief="groove")
        self.lbl_image.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        # Контейнер для текстового виводу векторів
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=10)

        ttk.Label(right_frame, text="Абсолютний вектор ознак X (25 елементів):", font=('Arial', 10, 'bold')).pack(anchor="w")
        self.txt_abs = tk.Text(right_frame, height=7, width=45, wrap="word")
        self.txt_abs.pack(fill="x", pady=5)

        ttk.Label(right_frame, text="Нормований вектор ознак X_norm:", font=('Arial', 10, 'bold')).pack(anchor="w")
        self.txt_norm = tk.Text(right_frame, height=7, width=45, wrap="word")
        self.txt_norm.pack(fill="x", pady=5)

    def extract_features(self, image_path):
        """
        Побудова вектора ознак:
        1. Зображення розбивається на сітку rows x cols.
        2. У кожному прямокутнику підраховується кількість чорних пікселів.
        """
        img = Image.open(image_path).convert('L')
        img_np = np.array(img)
        h, w = img_np.shape

        cell_h = h / self.rows
        cell_w = w / self.cols

        abs_vector = []

        # Обхід комірок сітки
        for r in range(self.rows):
            for c in range(self.cols):
                r_start, r_end = int(r * cell_h), int((r + 1) * cell_h)
                c_start, c_end = int(c * cell_w), int((c + 1) * cell_w)

                # Вирізаємо область комірки
                cell = img_np[r_start:r_end, c_start:c_end]
                
                # Чорні/темні пікселі мають значення колірної інтенсивності < 128
                black_pixel_count = np.sum(cell < 128)
                abs_vector.append(black_pixel_count)

        abs_vector = np.array(abs_vector, dtype=float)

        # Нормування (сума векторних компонент дорівнюватиме 1.0)
        total_sum = np.sum(abs_vector)
        if total_sum > 0:
            norm_vector = abs_vector / total_sum
        else:
            norm_vector = abs_vector.copy()

        return abs_vector, norm_vector

    def load_image(self):
        file_path = filedialog.askopenfilename(
            initialdir="data",
            filetypes=[("BMP files", "*.bmp")]
        )
        if not file_path:
            return

        # Обчислюємо вектори
        abs_vec, norm_vec = self.extract_features(file_path)

        # Відображаємо зображення в UI
        pil_img = Image.open(file_path).resize((200, 200), Image.Resampling.NEAREST)
        photo = ImageTk.PhotoImage(pil_img)
        self.lbl_image.config(image=photo, text="")
        self.lbl_image.image = photo

        # Виводимо абсолютний вектор
        self.txt_abs.delete("1.0", tk.END)
        self.txt_abs.insert(tk.END, str([int(x) for x in abs_vec]))

        # Виводимо нормований вектор (округлений для зручності прочитання)
        self.txt_norm.delete("1.0", tk.END)
        self.txt_norm.insert(tk.END, str([round(float(x), 4) for x in norm_vec]))

if __name__ == "__main__":
    root = tk.Tk()
    app = Task1App(root)
    root.mainloop()