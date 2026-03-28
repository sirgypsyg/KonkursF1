# KonkursF1 - HackArena 3.0

Repozytorium drużyny na konkurs HackArena 3.0.

## ⚠️ Co NIE działa na macOS (ARM/M1/M2/M3)

- **Backend lokalny** - organizatorzy nie wydali binarki dla macOS ARM
- **Build ze źródła** - brakuje biblioteki `libboink.dylib`
- **Rozwiązanie:** Użyj Windows u kolegi lub oficjalnych serwerów

## Status platform

| Komponent | Windows | macOS (Intel) | macOS (ARM/M1/M2/M3) | Linux |
|-----------|---------|---------------|---------------------|--------|
| CLI | ✅ | ✅ | ✅ | ✅ |
| **Backend lokalny** | ✅ | ❌ | ❌ | ❓ |
| Auth CLI | ✅ | ✅ | ✅ | ✅ |
| Python wrapper | ✅ | ✅ | ✅ | ✅ |

---

## 🪟 Instrukcja dla Windows (HOST serwera)

**Jeden członek drużyny na Windows uruchamia backend lokalny:**

### Krok 1: Pobierz CLI
```powershell
# Pobierz z:
https://github.com/INIT-SGGW/HackArena-Cli/releases/tag/v0.1.0
# Plik: hackarena-x86_64-pc-windows-msvc.exe
```

### Krok 2: Setup projektu
```powershell
# Sklonuj repo
git clone https://github.com/sirgypsyg/KonkursF1.git
cd KonkursF1

# Setup
hackarena.exe use 3
hackarena.exe install
hackarena.exe auth login
```

### Krok 3: Uruchom backend lokalny
```powershell
# Upewnij się, że masz najnowszą wersję
hackarena.exe update backend

# Wejdź do katalogu backend
cd backend

# Uruchom backend
.\ha3-backend-local.exe
```

### Krok 4: Stwórz sandbox na stronie HackArena
1. Zaloguj się na https://hackarena.pl (lub odpowiednia strona)
2. Przejdź do zakładki **"Local Servers"**
3. Kliknij **"+"** aby utworzyć nowy sandbox
4. Twój backend powinien się pojawić automatycznie

### Krok 5: Inni członkowie drużyny mogą się połączyć
- macOS/Linux: Widzą Twój sandbox na stronie
- Klikają "Join" lub uruchamiają bota z Twoim sandbox_id

---

## 🍎 Instrukcja dla macOS/Linux (CLIENT)

**Nie możesz uruchomić backendu lokalnego - łączysz się z Windows:**

### Krok 1: Setup
```bash
# Sklonuj repo
git clone https://github.com/sirgypsyg/KonkursF1.git
cd KonkursF1

# Dodaj hackarena do PATH (opcjonalnie)
echo 'export PATH="$PATH:$(pwd)"' >> ~/.zshrc
source ~/.zshrc

# Setup
./hackarena use 3
./hackarena auth login
```

### Krok 2: Zainstaluj zależności Python
```bash
pip install -e workspace/HackArena3.0-ApiWrapper-Python
# lub
pip install hackarena3
```

### Krok 3: Uruchom bota
```bash
cd wrappers/python/user/src
python3 -m bot

# Bot połączy się z dostępnym sandboxem
# Upewnij się, że kolega z Windows ma uruchomiony backend
```

---

## Architektura

```
┌─────────────────────────────────────────────────────────┐
│                    Strona HackArena                      │
│  (tworzenie sandboxów, spectating, dashboard)           │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              Backend lokalny (Windows)                   │
│  - Komunikuje się z ha3-game                             │
│  - Bez limitu botów                                      │
│  - Pełna swoboda testowania                              │
└─────────────────────────────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Bot (Ty) │ │ Bot (Kolega)│ │ Bot (...)│
        │ Python   │ │ C++/C#/TS  │ │ Python   │
        └──────────┘ └──────────┘ └──────────┘
```

---

## Szybki start (Windows)

### 1. Pobierz CLI
```powershell
# Z releases
https://github.com/INIT-SGGW/HackArena-Cli/releases/tag/v0.1.0
```

### 2. Setup projektu
```powershell
hackarena.exe use 3
hackarena.exe install
hackarena.exe auth login
```

### 3. Uruchom backend lokalny
```powershell
# Upewnij się, że masz najnowszą wersję
hackarena.exe update backend

# Uruchom backend
cd backend
.\ha3-backend-local.exe   # lub inna nazwa pliku
```

### 4. Stwórz sandbox na stronie
1. Zaloguj się na stronę HackArena
2. Kliknij "+" w zakładce "Local Servers"
3. Twój backend powinien się pojawić

### 5. Podłącz bota
```powershell
cd wrappers\python\user\src\bot
python -m bot
# Wybierz backend z listy
```

---

## Szybki start (macOS/Linux) - backend kolegi

### 1. Pobierz CLI
```bash
chmod +x hackarena
./hackarena use 3
./hackarena auth login
```

### 2. Dołącz do backendu kolegi (Windows)
- Kolega uruchamia backend lokalny (patrz wyżej)
- Ty na stronie HackArena widzisz jego sandbox
- Kliknij "Join" jako spectator lub bot

### 3. Uruchom bota
```bash
cd wrappers/python/user/src/bot
python -m bot --sandbox_id <ID>
```

---

## Sandboxy lokalne - wyjaśnienie

**Co to jest?**
- Lokalny serwer gry na twojej maszynie
- Pozwala testować bez limitów oficjalnego serwera
- Możesz uruchomić wiele botów jednocześnie

**Jak działa?**
1. Uruchamiasz `backend/ha3-backend-local` na Windows
2. Program komunikuje się z ha3-game w tle
3. Na stronie pojawia się Twój sandbox
4. Członkowie drużyny mogą się połączyć

**Limitacje:**
- Backend lokalny działa TYLKO na Windows
- macOS/Linux - muszą łączyć się z backendem kogoś innego

---

## Struktura projektu

```
KonkursF1/
├── AGENTS.md                     # Dokumentacja dla AI
├── README.md                     # Ten plik
├── Mechaniki Gry HackArena 3.0.* # Mechaniki gry (PL)
├── Racing 101 HackArena 3.0.*    # Poradnik wyścigowy (PL)
├── Zasady Turnieju HackArena 3.0.* # Zasady (PL)
├── hackarena                     # CLI binary
├── .hackarena/                   # Konfiguracja projektu
│   └── project.json
└── workspace/                    # Kloned repos
    ├── HackArena-Cli/
    └── HackArena3.0-ApiWrapper-Python/
```

---

## Dostępne języki (wrappery)

| Język | Status | Uwagi |
|-------|--------|-------|
| **Python** | ✅ Gotowy | `HackArena3.0-ApiWrapper-Python` |
| **C++** | ✅ Dostępny | Wymaga cmake + MSVC na Windows |
| **C#** | ✅ Dostępny | `dotnet run` |
| **TypeScript** | ✅ Dostępny | `npm install && npm run` |

---

## Przykładowy bot (Python)

```python
# wrappers/python/user/src/bot/__main__.py
from hackarena3 import BotContext, RaceSnapshot, run_bot

class MyBot:
    def __init__(self):
        self.tick = 0

    def on_tick(self, snapshot: RaceSnapshot, ctx: BotContext):
        self.tick += 1
        
        ctx.set_controls(
            throttle=0.6,   # Gaz (0-1)
            brake=0,        # Hamulec (0-1)
            steer=0.0,      # Skręt (-1 do 1)
        )

if __name__ == "__main__":
    raise SystemExit(run_bot(MyBot()))
```

---

## Komendy CLI

```bash
# Setup
./hackarena use 3
./hackarena install
./hackarena auth login

# Update
./hackarena update backend      # Najnowszy backend
./hackarena update wrapper python

# Info
./hackarena status              # Status projektu
./hackarena doctor              # Diagnostyka
./hackarena auth whoami         # Kto jest zalogowany

# Submit
./hackarena submit --slot 1
```

---

## Troubleshooting

| Problem | Rozwiązanie |
|---------|-------------|
| `No project found` | `./hackarena use 3` |
| `GitHub API 403/404` | Użyj własnego hotspotu |
| `No backend for aarch64-apple-darwin` | Normalne - tylko Windows ma backend |
| Backend nie działa | Tylko Windows wspierany |
| Nie widzę sandbox na stronie | Upewnij się że backend działa lokalnie |

---

## Linki

- [HackArena-Cli](https://github.com/INIT-SGGW/HackArena-Cli)
- [HackArena3.0-ApiWrapper-Python](https://github.com/INIT-SGGW/HackArena3.0-ApiWrapper-Python)
- [Releases CLI](https://github.com/INIT-SGGW/HackArena-Cli/releases)
- [Releases Backend](https://github.com/INIT-SGGW/HackArena3.0-Backend/releases)