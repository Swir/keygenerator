"""Synthetic pattern variants and bounded, atomic JSON persistence."""
import json
import os
from pathlib import Path
import random
import shutil
import tempfile
import uuid

DEFAULT_PATTERNS = ["RDCT-X9GR-XHHS-99UN-HKR9", "UADX-XM64-FC4R-EGBR-7HTX"]
MAX_PATTERNS = 500


def validate_pattern(pattern):
    if not isinstance(pattern, str) or not 1 <= len(pattern) <= 128:
        raise ValueError("Wzór musi mieć od 1 do 128 znaków.")
    if not all(32 <= ord(char) <= 126 for char in pattern) or not any(char.isalnum() for char in pattern):
        raise ValueError("Użyj liter A–Z/a–z, cyfr i drukowalnych separatorów ASCII.")
    return pattern


def validate_patterns(patterns):
    if not isinstance(patterns, list) or len(patterns) > MAX_PATTERNS:
        raise ValueError(f"Plik musi zawierać listę maksymalnie {MAX_PATTERNS} wzorców.")
    return list(dict.fromkeys(validate_pattern(pattern) for pattern in patterns))


def generate_code(pattern, rng=None):
    validate_pattern(pattern)
    rng = rng or random
    output = []
    for char in pattern:
        if char.isascii() and char.isalnum():
            base, count = (ord("0"), 10) if char.isdigit() else ((ord("A"), 26) if char.isupper() else (ord("a"), 26))
            choices = [char]
            if rng.random() < 0.5:
                choices.extend(chr(base + (ord(char) - base + offset) % count) for offset in (-1, 1))
            output.append(rng.choice(choices))
        else:
            output.append(char)
    return "".join(output)


def similarity(original, generated):
    if not original or len(original) != len(generated):
        raise ValueError("Porównywane kody muszą być niepuste i jednakowej długości.")
    return sum(a == b for a, b in zip(original, generated)) / len(original)


def generate_batch(pattern, count=10, rng=None):
    validate_pattern(pattern)
    if not isinstance(count, int) or not 1 <= count <= 100:
        raise ValueError("Liczba kodów musi mieścić się w przedziale 1–100.")
    return [(code, similarity(pattern, code)) for code in (generate_code(pattern, rng) for _ in range(count))]


def default_pattern_path():
    base = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".config")))
    return base / "Swir" / "PatternCodeGenerator" / "patterns.json"


class PatternStore:
    def __init__(self, path):
        self.path = Path(path)

    def load(self):
        if not self.path.exists():
            return DEFAULT_PATTERNS.copy()
        if self.path.stat().st_size > 256 * 1024:
            raise ValueError("Plik wzorców przekracza limit 256 KiB.")
        try:
            data = json.loads(self.path.read_text(encoding="utf-8-sig"))
        except (UnicodeError, json.JSONDecodeError) as error:
            raise ValueError("Plik wzorców nie zawiera poprawnego JSON.") from error
        return validate_patterns(data)

    def save(self, patterns):
        patterns = validate_patterns(patterns)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        backup = None
        if self.path.exists():
            try:
                self.load()
            except ValueError:
                backup = self.path.with_name(f"{self.path.stem}.invalid-{uuid.uuid4().hex}.json")
                shutil.copy2(self.path, backup)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=self.path.parent, prefix=".patterns-", suffix=".tmp", delete=False) as stream:
                temporary = Path(stream.name)
                json.dump(patterns, stream, ensure_ascii=False, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        return backup
