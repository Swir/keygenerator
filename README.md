# Generator Kodów / Code Generator

## Opis / Description

### 🇵🇱 Wersja polska
Generator Kodów to aplikacja GUI stworzona w Pythonie, która generuje unikalne kody o strukturze maksymalnie zbliżonej do wybranego wzorca. Program pozwala użytkownikowi na:
- Wybór lub dodanie wzorca kodu.
- Generowanie 10 kodów jednocześnie, zachowujących możliwie największe podobieństwo do wzorca.
- Kopiowanie poszczególnych kodów do schowka.
- Oznaczanie kodu najbardziej zbliżonego do wzorca kolorem zielonym.

Program jest szczególnie przydatny do generowania kodów lub kluczy, które muszą spełniać określony wzorzec. Dzięki wbudowanemu algorytmowi każdy kod jest obliczany, aby jak najwierniej odzwierciedlać wzorzec z dodanym elementem losowości, co zapewnia unikalność każdego kodu.

### 🇬🇧 English Version
The Code Generator is a Python-based GUI application that generates unique codes that closely match a selected pattern. The program allows users to:
- Choose or add a code pattern.
- Generate 10 codes simultaneously that maintain a high level of similarity to the pattern.
- Copy individual codes to the clipboard.
- Highlight the code most similar to the pattern in green.

The application is especially useful for generating codes or keys that must meet a specified format. Thanks to the built-in algorithm, each code is calculated to closely match the pattern, with a slight element of randomness to ensure each code is unique.

## Funkcjonalności / Features

### 🇵🇱 Wersja polska
- **Wybór wzorca kodu**: Możliwość wyboru jednego z predefiniowanych wzorców lub dodanie własnego.
- **Generowanie kodów**: Program generuje 10 kodów na podstawie wybranego wzorca i wyświetla je w formie listy.
- **Oznaczenie najlepszego dopasowania**: Kod najbardziej zbliżony do wzorca jest oznaczony kolorem zielonym, a jego precyzja wyświetlana jest w procentach.
- **Kopiowanie kodów**: Każdy kod można łatwo skopiować do schowka, klikając przycisk „Kopiuj” obok kodu.

### 🇬🇧 English Version
- **Pattern Selection**: Choose from predefined patterns or add a custom one.
- **Code Generation**: The program generates 10 codes based on the selected pattern and displays them as a list.
- **Highlight Best Match**: The code most similar to the pattern is highlighted in green, with its similarity displayed as a percentage.
- **Copy Codes**: Each code can be easily copied to the clipboard by clicking the “Copy” button next to it.

## Wymagania systemowe / System Requirements

- Python 3.x
- Tkinter (zwykle dostępny jako część instalacji Pythona)

## Instalacja i uruchomienie / Installation and Running

1. Sklonuj repozytorium:
   ```bash
   git clone https://github.com/swir/keygenerator.git
