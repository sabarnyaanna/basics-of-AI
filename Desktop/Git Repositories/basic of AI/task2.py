import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import numpy as np
from PIL import Image, ImageTk

class Task2App:
    def __init__(self, root):
        self.root = root
        self.root.title("Завдання 2: Система розпізнавання за еталонами")
        self.root.geometry("900x650")

        self.rows = 5
        self.cols = 5

        # Словник для збереження еталонів: {'Клас 1': norm_vector, ...}
        self.templates = {}

        self.setup_ui()

    def setup_ui(self):
        # Панель керування еталонами
        frame_controls = ttk.LabelFrame(self.root, text=" Керування еталонами ")
        frame_controls.pack(fill="x", padx=10, pady=5)

        ttk.Button(frame_controls, text="Додати еталон класу", command=self.add_template).pack(side="left", padx=10, pady=10)
        
        self.lbl_templates_count = ttk.Label(frame_controls, text="Завантажено еталонів: 0", font=('Arial', 10, 'bold'))
        self.lbl_templates_count.pack(side="left", padx=10)

        # Панель класифікації
        frame_class = ttk.LabelFrame(self.root, text=" Класифікація невідомого образу ")
        frame_class.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_class, text="Оберіть норму:").pack(side="left", padx=10)
        self.norm_var = tk.StringVar(value="Евклідова")
        norm_box = ttk.Combobox(
            frame_class, 
            textvariable=self.norm_var, 
            values=["Евклідова", "Чебишева", "Манхеттенська"], 
            state="readonly",
            width=15
        )
        norm_box.pack(side="left", padx=5)

        ttk.Button(frame_class, text="Завантажити та розпізнати образ", command=self.classify_image).pack(side="left", padx=15, pady=10)

        # Область результатів
        frame_main = ttk.Frame(self.root)
        frame_main.pack(fill="both", expand=True, padx=10, pady=5)

        self.lbl_unknown_img = ttk.Label(frame_main, text="Невідомий образ", borderwidth=2, relief="groove")
        self.lbl_unknown_img.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        self.txt_results = tk.Text(frame_main, height=15, width=50, font=('Consolas', 10))
        self.txt_results.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    def extract_features(self, image_path):
        """Побудова нормованого вектора ознак"""
        img = Image.open(image_path).convert('L')
        img_np = np.array(img)
        h, w = img_np.shape

        cell_h, cell_w = h / self.rows, w / self.cols
        abs_vector = []

        for r in range(self.rows):
            for c in range(self.cols):
                r_start, r_end = int(r * cell_h), int((r + 1) * cell_h)
                c_start, c_end = int(c * cell_w), int((c + 1) * cell_w)
                cell = img_np[r_start:r_end, c_start:c_end]
                abs_vector.append(np.sum(cell < 128))

        abs_vector = np.array(abs_vector, dtype=float)
        total_sum = np.sum(abs_vector)
        norm_vector = abs_vector / total_sum if total_sum > 0 else abs_vector
        return norm_vector

    def add_template(self):
        file_path = filedialog.askopenfilename(initialdir="data", filetypes=[("BMP files", "*.bmp")])
        if not file_path:
            return

        class_num = len(self.templates) + 1
        class_name = f"Клас_{class_num}"
        norm_vec = self.extract_features(file_path)

        self.templates[class_name] = norm_vec
        self.lbl_templates_count.config(text=f"Завантажено еталонів: {len(self.templates)} ({', '.join(self.templates.keys())})")

    def calculate_distance(self, vec1, vec2, metric):
        """Обчислення відстаней між векторами за варіантом норми"""
        if metric == "Евклідова":
            return np.sqrt(np.sum((vec1 - vec2) ** 2))
        elif metric == "Чебишева":
            return np.max(np.abs(vec1 - vec2))
        elif metric == "Манхеттенська":
            return np.sum(np.abs(vec1 - vec2))

    def classify_image(self):
        if not self.templates:
            messagebox.showwarning("Увага", "Спочатку додайте хоча б 2-3 еталони категорій!")
            return

        file_path = filedialog.askopenfilename(initialdir="data", filetypes=[("BMP files", "*.bmp")])
        if not file_path:
            return

        # Відображення невідомого образу
        pil_img = Image.open(file_path).resize((200, 200), Image.Resampling.NEAREST)
        photo = ImageTk.PhotoImage(pil_img)
        self.lbl_unknown_img.config(image=photo, text="")
        self.lbl_unknown_img.image = photo

        # Обчислення вектора невідомого образу
        unknown_vec = self.extract_features(file_path)
        selected_metric = self.norm_var.get()

        distances = {}
        for class_name, template_vec in self.templates.items():
            dist = self.calculate_distance(unknown_vec, template_vec, selected_metric)
            distances[class_name] = dist

        # Визначення найкращого класу (з найменшою відстанню)
        best_class = min(distances, key=distances.get)

        # Вивід у текстове поле
        self.txt_results.delete("1.0", tk.END)
        self.txt_results.insert(tk.END, f"--- МЕТРИКА: {selected_metric.upper()} ---\n\n")
        self.txt_results.insert(tk.END, "Відстані до еталонів:\n")
        
        for c_name, dist in distances.items():
            self.txt_results.insert(tk.END, f" • {c_name}: {dist:.6f}\n")

        self.txt_results.insert(tk.END, "\n" + "="*30 + "\n")
        self.txt_results.insert(tk.END, f"ВИСНОВОК: Образ належить до -> {best_class.upper()}")

if __name__ == "__main__":
    root = tk.Tk()
    app = Task2App(root)
    root.mainloop()