# KonkursF1 - HackArena 3.0

Repozytorium drużyny na konkurs HackArena 3.0.

## Status

| Komponent | Windows | macOS (Intel) | macOS (ARM/M1/M2/M3) | Linux |
|-----------|---------|---------------|---------------------|--------|
| CLI | ✅ | ✅ | ✅ | ✅ |
| Backend lokalny | ✅ | ❓ | ❌ | ✅ |
| Auth CLI | ✅ | ✅ | ✅ | ✅ |
| Python wrapper | ✅ | ✅ | ✅ | ✅ |

### Co działa:
- CLI - konfiguracja i submit
- Python wrapper - pisanie botów
- Dokumentacja mechanik gry
- Testowanie na serwerach zdalnych

### Co NIE działa:
- **Backend lokalny na macOS ARM** - organizatorzy nie wydali binarki dla `aarch64-apple-darwin`
- Jedyne opcje dla macOS ARM: testować na serwerze kolegi (Windows/Linux) lub łączyć się z oficjalnymi serwerami

---

## Instalacja

### Wymagania
- Python 3.10+ (dla bota w Pythonie)
- GitHub account (do autoryzacji)

### Pobierz CLI

1. Pobierz z: https://github.com/INIT-SGGW/HackArena-Cli/releases/tag/v0.1.0
   - **Windows**: `hackarena-x86_64-pc-windows-msvc.exe`
   - **macOS ARM**: `hackarena-aarch64-apple-darwin` (lub skopiuj z tego repo)
   - **Linux**: `hackarena-x86_64-unknown-linux-musl`

2. Nadaj uprawnienia (Unix):
   ```bash
   chmod +x hackarena
   ```

### Setup

```bash
# W katalogu projektu
./hackarena use 3
./hackarena install          # Windows/Linux - instaluje backend lokalny
./hackarena auth login       # Otwiera przeglądarkę do logowania
```

---

## Uruchamianie na Windows

```powershell
# 1. Pobierz CLI
# https://github.com/INIT-SGGW/HackArena-Cli/releases

# 2. Setup
hackarena.exe use 3
hackarena.exe install
hackarena.exe auth login

# 3. Zainstaluj zależności Python
cd wrappers/python/user
pip install -r requirements.txt

# 4. Utwórz lokalny serwer na stronie HackArena
#    (zakładka "Local Servers")

# 5. Uruchom bota
python -m bot
```

---

## Uruchamianie na macOS ARM (M1/M2/M3)

**⚠️ Backend lokalny NIE DZIAŁA - brak binarki dla ARM**

### Opcja 1: Testowanie na serwerze kolegi (Windows/Linux)

1. Kolega (Windows/Linux) uruchamia lokalny backend
2. Ty piszesz bota lokalnie
3. Łączysz się z jego serwerem przez stronę HackArena

### Opcja 2: Oficjalne serwery

```bash
# Ustaw zmienne środowiskowe (otrzymasz od organizatorów)
export HA3_WRAPPER_BACKEND_ENDPOINT=https://server/backend
export HA3_WRAPPER_TEAM_TOKEN=xxx
export HA3_WRAPPER_AUTH_TOKEN=xxx

# Uruchom bota
python -m bot --official
```

### Instalacja Python wrapper

```bash
cd workspace/HackArena3.0-ApiWrapper-Python
pip install -e .

# Test importu
python -c "from hackarena3 import run_bot; print('OK')"
```

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
│   └──	project.json
└── workspace/                    # Kloned repos
    ├── HackArena-Cli/
    └── HackArena3.0-ApiWrapper-Python/
```

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
        
        # Prosta logika - jazda prosto
        ctx.set_controls(
            throttle=0.6,
            brake=0,
            steer=0.0,
        )

if __name__ == "__main__":
    raise SystemExit(run_bot(MyBot()))
```

---

## Przydatne komendy

```bash
# CLI
./hackarena status          # Status projektu
./hackarena doctor          # Diagnostyka
./hackarena auth whoami     # Kto jest zalogowany
./hackarena submit --slot 1 # Submit rozwiązania

# Python
python -m bot               # Uruchom bota lokalnie
python -m bot --official    # Uruchom na oficjalnych serwerach
```

---

## Linki

- [HackArena-Cli](https://github.com/INIT-SGGW/HackArena-Cli)
- [HackArena3.0-ApiWrapper-Python](https://github.com/INIT-SGGW/HackArena3.0-ApiWrapper-Python)
- [HackArena-Auth-Cli](https://github.com/INIT-SGGW/HackArena-Auth-Cli)
- [HackArena3.0-Backend](https://github.com/INIT-SGGW/HackArena3.0-Backend)
- [Releases CLI](https://github.com/INIT-SGGW/HackArena-Cli/releases)
- [Releases Backend](https://github.com/INIT-SGGW/HackArena3.0-Backend/releases)

---

## Troubleshooting

| Problem | Rozwiązanie |
|---------|-------------|
| `No project found` | `./hackarena use 3` |
| `GitHub API 403/404` | Użyj własnego hotspotu lub GH_TOKEN |
| `Permission denied (publickey)` | Użyj HTTPS zamiast SSH |
| `No asset matching backend for aarch64-apple-darwin` | macOS ARM nie jest wspierany - użyj Windows/Linux lub serwer zdalny |
| Login required (exit 2) | `./hackarena auth login` |