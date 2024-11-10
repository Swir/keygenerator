import random
import tkinter as tk
from tkinter import StringVar, ttk, messagebox
import json
import os
import threading

class CodeGeneratorApp:
    def __init__(self, master):
        self.master = master
        self.master.attributes('-topmost', True)
        self.pattern_file = "patterns.json"
        
        self.load_patterns()
        self.build_gui()

    def load_patterns(self):
        try:
            if os.path.exists(self.pattern_file):
                with open(self.pattern_file, "r") as file:
                    content = file.read()
                    if content.strip():
                        self.patterns = json.loads(content)
                        if not self.patterns:
                            self.set_default_patterns()
                    else:
                        self.set_default_patterns()
            else:
                self.set_default_patterns()
        except (IOError, json.decoder.JSONDecodeError) as e:
            messagebox.showerror("Błąd", f"Nie udało się załadować wzorców: {e}")
            self.set_default_patterns()

    def set_default_patterns(self):
        self.patterns = [
            "RDCT-X9GR-XHHS-99UN-HKR9",
            "UADX-XM64-FC4R-EGBR-7HTX",
        ]

    def save_patterns(self):
        try:
            with open(self.pattern_file, "w") as file:
                json.dump(self.patterns, file)
        except IOError as e:
            messagebox.showerror("Błąd", f"Nie udało się zapisać wzorców: {e}")

    def build_gui(self):
        mainframe = ttk.Frame(self.master, padding="10")
        mainframe.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.master.attributes('-alpha', 0.95)

        self.code = StringVar()
        self.pattern_choice = StringVar()

        ttk.Label(mainframe, text="Wybierz wzór:").grid(column=1, row=1, sticky=tk.W)
        self.pattern_dropdown = ttk.Combobox(mainframe, textvariable=self.pattern_choice, values=self.patterns, state="readonly")
        self.pattern_dropdown.grid(column=2, row=1, sticky=(tk.W, tk.E))
        if self.patterns:
            self.pattern_dropdown.set(self.patterns[0])

        ttk.Label(mainframe, text="Dodaj nowy wzór:").grid(column=1, row=2, sticky=tk.W)
        self.new_pattern_entry = ttk.Entry(mainframe)
        self.new_pattern_entry.grid(column=2, row=2, sticky=(tk.W, tk.E))
        ttk.Button(mainframe, text="Dodaj", command=self.add_new_pattern).grid(column=3, row=2)

        # Ramka do wyświetlania kodów
        self.codes_frame = tk.Frame(mainframe, bg="#f0f0f0", bd=2, relief="groove")
        self.codes_frame.grid(column=1, row=3, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(mainframe, text="Generuj kody", command=self.start_code_generation).grid(column=2, row=4, pady=10)

        self.progress = ttk.Progressbar(mainframe, orient="horizontal", length=200, mode="indeterminate")
        self.progress.grid(column=2, row=5, sticky=(tk.W, tk.E))

    def add_new_pattern(self):
        new_pattern = self.new_pattern_entry.get()
        if self.is_valid_pattern(new_pattern) and new_pattern not in self.patterns:
            self.patterns.append(new_pattern)
            self.pattern_dropdown['values'] = self.patterns
            self.pattern_dropdown.set(new_pattern)
            self.new_pattern_entry.delete(0, tk.END)
            self.save_patterns()
            messagebox.showinfo("Sukces", "Nowy wzór dodany!")
        else:
            messagebox.showerror("Błąd", "Nieprawidłowy wzór lub wzór już istnieje!")

    def start_code_generation(self):
        if not self.pattern_choice.get():
            messagebox.showwarning("Ostrzeżenie", "Wybierz wzór przed wygenerowaniem kodów.")
            return
        self.progress.start(10)
        threading.Thread(target=self.generate_multiple_codes).start()

    def generate_multiple_codes(self):
        pattern = self.pattern_choice.get()
        generated_codes = []
        max_similarity = 0
        best_code = None

        # Generowanie 10 kodów z oceną precyzji
        for _ in range(10):
            code = self.generate_code_with_precision(pattern)
            similarity = self.calculate_similarity(pattern, code)

            generated_codes.append((code, similarity))

            # Aktualizacja najlepszego kodu na podstawie precyzji
            if similarity > max_similarity:
                max_similarity = similarity
                best_code = code

        self.display_codes(generated_codes, best_code)
        self.progress.stop()

    def generate_code_with_precision(self, pattern):
        """Generuje kod, maksymalizując podobieństwo do wzorca z lekkim elementem losowości."""
        generated_code = ""
        for char in pattern:
            if char.isalpha():
                generated_code += self.precise_letter_with_randomness(char)
            elif char.isdigit():
                generated_code += self.precise_digit_with_randomness(char)
            else:
                generated_code += char
        return generated_code

    def precise_letter_with_randomness(self, letter):
        """Dobiera literę maksymalnie podobną do podanej, z lekkim elementem losowości."""
        base_ascii = ord(letter.upper())
        # Dodaj element losowości do najbliższych sąsiednich znaków
        possible_choices = [chr(base_ascii)]
        if random.random() < 0.5:  # 50% szans na zmianę znaku
            possible_choices.append(chr((base_ascii + 1 - 65) % 26 + 65))
            possible_choices.append(chr((base_ascii - 1 - 65) % 26 + 65))
        return random.choice(possible_choices) if letter.isupper() else random.choice(possible_choices).lower()

    def precise_digit_with_randomness(self, digit):
        """Dobiera cyfrę maksymalnie podobną do podanej, z lekkim elementem losowości."""
        base_ascii = ord(digit)
        possible_choices = [chr(base_ascii)]
        if random.random() < 0.5:  # 50% szans na zmianę cyfry
            possible_choices.append(chr((base_ascii + 1 - 48) % 10 + 48))
            possible_choices.append(chr((base_ascii - 1 - 48) % 10 + 48))
        return random.choice(possible_choices)

    def calculate_similarity(self, original, generated):
        """Oblicza precyzję podobieństwa między wzorcem a wygenerowanym kodem."""
        similarity = sum(1 for o, g in zip(original, generated) if o == g)
        return similarity / len(original)

    def display_codes(self, generated_codes, best_code):
        """Wyświetla wygenerowane kody w interfejsie, podświetlając najlepszy i dodając przyciski do kopiowania."""
        for widget in self.codes_frame.winfo_children():
            widget.destroy()

        for code, similarity in generated_codes:
            # Ramka dla każdego kodu
            code_frame = tk.Frame(self.codes_frame, bg="#ffffff", padx=5, pady=5, relief="solid", bd=1)
            code_frame.pack(fill="x", pady=2)

            color = "green" if code == best_code else "black"
            code_label = tk.Label(code_frame, text=f"{code} (Precyzja: {similarity * 100:.2f}%)", fg=color, font=('Arial', 10))
            code_label.pack(side="left", padx=(0, 10))

            copy_button = tk.Button(code_frame, text="Kopiuj", command=lambda c=code: self.copy_to_clipboard(c))
            copy_button.pack(side="right")

    def copy_to_clipboard(self, code):
        """Kopiuje podany kod do schowka."""
        self.master.clipboard_clear()
        self.master.clipboard_append(code)
        messagebox.showinfo("Schowek", "Kod został skopiowany do schowka!")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Generator kodów")
    app = CodeGeneratorApp(root)
    root.mainloop()
