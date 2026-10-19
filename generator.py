"""Desktop synthetic-code generator; generation stays on the Tk main thread."""
import json
from pathlib import Path
import sys
import tempfile
import tkinter as tk
from tkinter import ttk
from pattern_core import DEFAULT_PATTERNS, PatternStore, default_pattern_path, generate_batch, validate_pattern

VERSION = "1.1.0"


class CodeGeneratorApp:
    def __init__(self, root, pattern_file=None):
        self.master = root
        self.store = PatternStore(pattern_file or default_pattern_path())
        self.status = tk.StringVar(root)
        try:
            legacy = Path.cwd() / "patterns.json"
            if pattern_file is None and not self.store.path.exists() and legacy.is_file():
                self.patterns = PatternStore(legacy).load()
                self.status.set("Odczytano stare wzorce. Kolejny zapis trafi do profilu użytkownika; oryginał pozostanie bez zmian.")
            else:
                self.patterns = self.store.load()
        except (OSError, ValueError) as error:
            self.patterns = DEFAULT_PATTERNS.copy()
            self.status.set(f"Nie odczytano wzorców: {error} Przy zapisie uszkodzony plik otrzyma kopię zapasową.")
        self.patterns = self.patterns or DEFAULT_PATTERNS.copy()
        root.title(f"Generator kodów testowych {VERSION} — Swir")
        root.minsize(590, 410)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        frame = ttk.Frame(root, padding=16)
        frame.grid(sticky="nsew")
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(4, weight=1)
        self.pattern_choice = tk.StringVar(root, self.patterns[0])
        self.new_pattern = tk.StringVar(root)
        ttk.Label(frame, text="Wybierz wzór:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        self.pattern_dropdown = ttk.Combobox(frame, textvariable=self.pattern_choice, values=self.patterns, state="readonly")
        self.pattern_dropdown.grid(row=0, column=1, columnspan=2, sticky="ew", pady=5)
        ttk.Label(frame, text="Nowy wzór:").grid(row=1, column=0, sticky="w", pady=5)
        self.new_pattern_entry = ttk.Entry(frame, textvariable=self.new_pattern)
        self.new_pattern_entry.grid(row=1, column=1, sticky="ew", pady=5)
        self.add_button = ttk.Button(frame, text="Dodaj", command=self.add_new_pattern)
        self.add_button.grid(row=1, column=2, padx=(8, 0))
        self.generate_button = ttk.Button(frame, text="Generuj 10 kodów", command=self.start_code_generation)
        self.generate_button.grid(row=2, column=0, columnspan=3, pady=10)
        ttk.Label(frame, textvariable=self.status, wraplength=570).grid(row=3, column=0, columnspan=3, sticky="ew", pady=(0, 8))
        results = ttk.Frame(frame)
        results.grid(row=4, column=0, columnspan=3, sticky="nsew")
        results.rowconfigure(0, weight=1)
        results.columnconfigure(0, weight=1)
        self.codes = ttk.Treeview(results, columns=("code", "similarity"), show="headings", height=10, selectmode="browse")
        self.codes.heading("code", text="Kod testowy")
        self.codes.heading("similarity", text="Podobieństwo")
        self.codes.column("code", width=400, minwidth=200)
        self.codes.column("similarity", width=100, minwidth=90, stretch=False)
        self.codes.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(results, orient="vertical", command=self.codes.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        horizontal = ttk.Scrollbar(results, orient="horizontal", command=self.codes.xview)
        horizontal.grid(row=1, column=0, sticky="ew")
        self.codes.configure(yscrollcommand=scroll.set, xscrollcommand=horizontal.set)
        self.codes.tag_configure("best", foreground="#16803c")
        ttk.Button(frame, text="Kopiuj wybrany kod", command=self.copy_selected).grid(row=5, column=0, columnspan=3, pady=(10, 0))
        self.new_pattern_entry.bind("<Return>", lambda _event: self.add_new_pattern())

    def is_valid_pattern(self, pattern):
        try:
            validate_pattern(pattern)
            return True
        except ValueError:
            return False

    def add_new_pattern(self):
        pattern = self.new_pattern.get().strip()
        try:
            validate_pattern(pattern)
            if pattern in self.patterns:
                raise ValueError("Ten wzór już istnieje.")
            candidate = self.patterns + [pattern]
            backup = self.store.save(candidate)
        except (ValueError, OSError) as error:
            self.status.set(f"Nie zapisano wzoru: {error}")
            return False
        self.patterns = candidate
        self.pattern_dropdown.configure(values=self.patterns)
        self.pattern_choice.set(pattern)
        self.new_pattern.set("")
        self.status.set("Zapisano wzór." + (f" Kopia poprzedniego pliku: {backup.name}" if backup else ""))
        return True

    def start_code_generation(self):
        try:
            generated = generate_batch(self.pattern_choice.get())
        except ValueError as error:
            self.status.set(str(error))
            return False
        best = max(score for _code, score in generated)
        self.codes.delete(*self.codes.get_children())
        for code, score in generated:
            self.codes.insert("", "end", values=(code, f"{score:.0%}"), tags=("best",) if score == best else ())
        self.codes.selection_set(self.codes.get_children()[0])
        self.status.set("Wygenerowano 10 kodów testowych. Podobieństwo nie oznacza ważności kodu.")
        return True

    def copy_selected(self):
        selected = self.codes.selection()
        if not selected:
            self.status.set("Najpierw wybierz wygenerowany kod.")
            return False
        code = self.codes.item(selected[0], "values")[0]
        try:
            self.master.clipboard_clear()
            self.master.clipboard_append(code)
        except tk.TclError:
            self.status.set("Schowek jest niedostępny. Spróbuj ponownie.")
            return False
        self.status.set("Skopiowano kod testowy.")
        return True


def self_test(report):
    root = None
    result = {"application":"Key-Generator", "version":VERSION, "passed":False}
    try:
        report_parent = Path(report).resolve().parent
        with tempfile.TemporaryDirectory(prefix="pattern-generator-smoke-", dir=report_parent) as directory:
            if not Path(directory).resolve().is_relative_to(report_parent):
                raise RuntimeError("Unexpected smoke-test directory")
            path = Path(directory) / "patterns.json"
            root = tk.Tk()
            root.withdraw()
            app = CodeGeneratorApp(root, path)
            root.update_idletasks()
            app.new_pattern.set("Ab9-TEST-012")
            app.add_button.invoke()
            assert app.pattern_choice.get() == "Ab9-TEST-012"
            assert "Ab9-TEST-012" in PatternStore(path).load()
            app.generate_button.invoke()
            rows = app.codes.get_children()
            assert len(rows) == 10
            assert all(len(app.codes.item(row, "values")[0]) == 12 for row in rows)
            app.new_pattern.set("---")
            assert not app.add_new_pattern()
            root.destroy()
            root = None
            result.update(passed=True, checks=["Tk widgets", "add pattern button", "atomic JSON persistence", "ten generated rows", "invalid pattern"])
    except Exception as error:
        result["error"] = f"{type(error).__name__}: {error}"
    finally:
        if root is not None:
            root.destroy()
        Path(report).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if result["passed"] else 1


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--self-test":
        return self_test(sys.argv[2])
    root = tk.Tk()
    CodeGeneratorApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
