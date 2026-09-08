import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import numpy as np
from PIL import Image, ImageTk

class Task3App:
    def __init__(self, root):
        self.root = root
        self.root.title("Завдання 3: Класифікація з навчанням (Центри та Ортогональні області)")
        self.root.geometry("950x700")

        self.rows = 5
        self.cols = 5

        # Навчальна вибірка: {'Клас 1': [vec1, vec2, ...], 'Клас 2': [...]}
        self.train_data = {}

        self.setup_ui()

    def setup_ui(self):
        # Панель навчання
        frame_train = ttk.LabelFrame(self.root, text=" Навчання системи ")
        frame_train.pack(fill="x", padx=10, pady=5)

        ttk.Button(frame_train, text="Завантажити вибірку для НОВОГО класу", command=self.load_class_samples).pack(side="left", padx=10, pady=10)
        
        self.lbl_train_info = ttk.Label(frame_train, text="Сформовано класів: 0", font=('Arial', 10, 'bold'))
        self.lbl_train_info.pack(side="left", padx=10)

        # Панель класифікації
        frame_class = ttk.LabelFrame(self.root, text=" Класифікація ")
        frame_class.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_class, text="Метод розпізнавання:").pack(side="left", padx=10)
        self.method_var = tk.StringVar(value="Геометричні центри")
        method_box = ttk.Combobox(
            frame_class, 
            textvariable=self.method_var, 
            values=["Геометричні центри", "Ортогональні області"], 
            state="readonly",
            width=22
        )
        method_box.pack(side="left", padx=5)

        ttk.Button(frame_class, text="Класифікувати новий образ", command=self.classify_image).pack(side="left", padx=15, pady=10)

        # Основна частина
        frame_main = ttk.Frame(self.root)
        frame_main.pack(fill="both", expand=True, padx=10, pady=5)

        self.lbl_img = ttk.Label(frame_main, text="Тестовий образ", borderwidth=2, relief="groove")
        self.lbl_img.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        self.txt_res = tk.Text(frame_main, height=18, width=55, font=('Consolas', 10))
        self.txt_res.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    def extract_features(self, image_path):
        """Побудова нормованого вектора ознак"""
        img = Image.open(image_path).convert('L')
        img_np = np.array(img)
        h, w = img_np.shape

        cell_h, cell_w = h / self.rows, w / self.cols
        abs_vector = []

        for r in range(self.rows):
            for c in range(self.cols):
                r_s, r_e = int(r * cell_h), int((r + 1) * cell_h)
                c_s, c_e = int(c * cell_w), int((c + 1) * cell_w)
                cell = img_np[r_s:r_e, c_s:c_e]
                abs_vector.append(np.sum(cell < 128))

        abs_vector = np.array(abs_vector, dtype=float)
        total = np.sum(abs_vector)
        return abs_vector / total if total > 0 else abs_vector

    def load_class_samples(self):
        """Обираємо одразу кілька файлів (.bmp) для створення нового класу"""
        file_paths = filedialog.askopenfilenames(
            initialdir="data", 
            filetypes=[("BMP files", "*.bmp")],
            title="Оберіть 2 або більше картинок для одного класу"
        )
        if not file_paths:
            return

        class_num = len(self.train_data) + 1
        class_name = f"Клас_{class_num}"

        vectors = [self.extract_features(p) for p in file_paths]
        self.train_data[class_name] = vectors

        self.lbl_train_info.config(text=f"Сформовано класів: {len(self.train_data)}")
        self.txt_res.insert(tk.END, f"Успішно завантажено {len(vectors)} зразки(ів) для '{class_name}'.\n")

    def classify_image(self):
        if not self.train_data:
            messagebox.showwarning("Увага", "Спочатку додайте хоча б один клас із навчальною вибіркою!")
            return

        file_path = filedialog.askopenfilename(initialdir="data", filetypes=[("BMP files", "*.bmp")])
        if not file_path:
            return

        # Відображення тестового зображення
        pil_img = Image.open(file_path).resize((200, 200), Image.Resampling.NEAREST)
        photo = ImageTk.PhotoImage(pil_img)
        self.lbl_img.config(image=photo, text="")
        self.lbl_img.image = photo

        test_vec = self.extract_features(file_path)
        method = self.method_var.get()

        self.txt_res.delete("1.0", tk.END)
        self.txt_res.insert(tk.END, f"=== МЕТОД: {method.upper()} ===\n\n")

        if method == "Геометричні центри":
            distances = {}
            for class_name, vectors in self.train_data.items():
                # Обчислюємо геометричний центр (середнє значення вектора)
                center_vec = np.mean(vectors, axis=0)
                # Евклідова відстань до центру
                dist = np.sqrt(np.sum((test_vec - center_vec) ** 2))
                distances[class_name] = dist
                self.txt_res.insert(tk.END, f"Відстань до центру '{class_name}': {dist:.6f}\n")

            best_class = min(distances, key=distances.get)
            self.txt_res.insert(tk.END, f"\nВИСНОВОК: Образ належить до -> {best_class}")

        elif method == "Ортогональні області":
            matched_classes = []
            
            for class_name, vectors in self.train_data.items():
                vecs_matrix = np.array(vectors)
                min_bounds = np.min(vecs_matrix, axis=0)
                max_bounds = np.max(vecs_matrix, axis=0)

                # Перевіряємо, чи входить кожен елемент вектора в [min, max]
                inside = np.all((test_vec >= min_bounds) & (test_vec <= max_bounds))
                
                self.txt_res.insert(tk.END, f"Перевірка для '{class_name}': {'ПОТРАПЛЯЄ' if inside else 'НЕ потрапляє'}\n")
                if inside:
                    matched_classes.append(class_name)

            self.txt_res.insert(tk.END, "\n" + "="*35 + "\n")
            if len(matched_classes) == 1:
                self.txt_res.insert(tk.END, f"ВИСНОВОК: Образ належить до -> {matched_classes[0]}")
            elif len(matched_classes) > 1:
                self.txt_res.insert(tk.END, f"ВИСНОВОК: Перетин областей! Належить до: {', '.join(matched_classes)}")
            else:
                self.txt_res.insert(tk.END, "ВИСНОВОК: Об'єкт НЕ потрапляє в жодну з відомих областей.")

if __name__ == "__main__":
    root = tk.Tk()
    app = Task3App(root)
    root.mainloop()