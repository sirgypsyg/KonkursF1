# AGENTS.md - HackArena 3.0 Competition

## Project Overview

HackArena 3.0 is a racing game competition where teams write AI bots (drivers) to compete in races.

## Quick Start (Official Instructions)

1. **Download CLI release v0.1.0** from https://github.com/INIT-SGGW/HackArena-Cli/releases/tag/v0.1.0
   - macOS: `hackarena-aarch64-apple-darwin`
   - Linux: `hackarena-x86_64-unknown-linux-musl`
   - Windows: `hackarena-x86_64-pc-windows-msvc.exe`

2. **Setup in your project directory:**
   ```bash
   hackarena use 3
   hackarena install
   hackarena auth login
   ```

3. **Write your bot** using wrapper (Python/C++/C#/TypeScript)

4. **Create local server** on HackArena website → "Local Servers" tab

5. **Run your bot** from IDE to connect to local server

## Local Sandbox (Backend Lokalny)

**⚠️ WAŻNE: Backend lokalny działa TYLKO na Windows!**

Mechanizm sandboxów lokalnych pozwala testować boty bez limitów oficjalnego serwera:
- Bez limitu liczby botów
- Pełna swoboda testowania
- Komunikacja z ha3-game w tle

### Uruchamianie backend lokalny (Windows)

```bash
# 1. Upewnij się, że masz najnowszą wersję
hackarena update backend

# 2. Idź do katalogu backend
cd backend

# 3. Uruchom backend (plik wykonywalny)
./ha3-backend-local    # Linux/macOS
ha3-backend-local.exe  # Windows
```

### Tworzenie sandbox na stronie

1. Zaloguj się na stronę HackArena
2. Przejdź do zakładki "Local Servers"
3. Kliknij "+" aby utworzyć nowy sandbox
4. Twój backend powinien się pojawić na liście

### Dołączanie do sandbox

- **Jako spectator**: Przeglądarka → strona HackArena → "Join"
- **Jako bot**: Uruchom wrapper → wybierz backend z listy

### Workflow dla zespołu

```
┌─────────────────────────────────────────┐
│  Członek z Windows                       │
│  └─ Uruchamia backend lokalny            │
│     └─ Tworzy sandbox na stronie         │
│        └─ Inni dołączają botami         │
└─────────────────────────────────────────┘
          │
    ┌─────┴─────┐
    ▼           ▼
┌───────┐   ┌───────┐
│macOS  │   │ Linux │
│bot    │   │ bot   │
└───────┘   └───────┘
```

## Linked Repositories

| Repository | Language | Purpose |
|------------|----------|---------|
| [HackArena-Cli](https://github.com/INIT-SGGW/HackArena-Cli) | Rust | Main CLI tool for participants |
| [HackArena3.0-ApiWrapper-Python](https://github.com/INIT-SGGW/HackArena3.0-ApiWrapper-Python) | Python | Python API wrapper for bot development |
| [HackArena-Auth-Cli](https://github.com/INIT-SGGW/HackArena-Auth-Cli) | Rust | Authentication CLI (Keycloak OIDC) |
| [HackArena3.0-Backend](https://github.com/INIT-SGGW/HackArena3.0-Backend) | Rust | Game server backend |

## CLI Commands

```bash
# Setup
hackarena use 3
hackarena install

# Authentication
hackarena auth login
hackarena auth whoami

# Development
hackarena status
hackarena doctor
hackarena update              # Update all components
hackarena update backend      # Update backend only
hackarena update wrapper python  # Update Python wrapper
hackarena clean

# Submit
hackarena submit --slot 1
hackarena submit --slot 2 -d "description"
```

## Python Bot Structure

```
wrappers/python/
  system/manifest.toml    # Auto-generated
  user/
    requirements.txt      # Dependencies
    .env                  # Environment (optional)
    src/bot/
      __main__.py         # Entry point
```

### Example Bot (`__main__.py`)

```python
from hackarena3 import BotContext, DriveGear, GearShift, RaceSnapshot, run_bot

class MyBot:
    def __init__(self) -> None:
        self.tick = 0

    def on_tick(self, snapshot: RaceSnapshot, ctx: BotContext) -> None:
        self.tick += 1
        ctx.set_controls(
            throttle=0.55,
            brake=0,
            steer=0.0,
        )

if __name__ == "__main__":
    raise SystemExit(run_bot(MyBot()))
```

### Key Types

- `RaceSnapshot` - Current race state (car, opponents, track)
- `BotContext` - Control methods (`set_controls`, `set_tire_compound`)
- `DriveGear` - Gear enum (REVERSE, NEUTRAL, FIRST...TENTH)
- `GearShift` - DOWNSHIFT, UPSHIFT, NONE
- `TireType` - HARD, SOFT, WET

## Environment Variables

### Sandbox Mode (Local Server)
```bash
HA3_WRAPPER_API_URL=http://localhost:50051  # Auto-set by CLI
HA3_WRAPPER_HA_AUTH_BIN=/path/to/ha-auth     # Auto-set by CLI
```

### Official Mode (Competition Servers)
```bash
HA3_WRAPPER_BACKEND_ENDPOINT=https://server/backend
HA3_WRAPPER_TEAM_TOKEN=xxx
HA3_WRAPPER_AUTH_TOKEN=xxx
```

## Code Style Guidelines

### Python

- Use `pyproject.toml` for project configuration
- Follow PEP 8: snake_case for functions/variables, PascalCase for classes
- Type hints recommended: `def on_tick(self, snapshot: RaceSnapshot, ctx: BotContext) -> None:`
- Use dataclasses for structured data

### TOML Configuration (manifest.toml)

```toml
schema = 1

[wrapper]
language = "python"
template_version = "0.0.0"

[runtime]
engine = "python"
version = "3.10"

[run]
entrypoint = ["python", "-m", "bot"]
source_dir = "user/src"

[submit]
include = ["user/src", "user/requirements.txt"]
exclude = ["**/__pycache__/**", "**/*.pyc"]
```

## Game Mechanics Summary

### Vehicle Physics

- 10 gears (including reverse and neutral)
- Engine power peaks in upper RPM range (not at max)
- "Rev limiter" cuts power at max RPM
- Traction budget system - throttle/brake/steering compete for grip
- Differential stiffness affects cornering behavior

### Tire System

- Three tire types: Hard (100-110°C), Soft (80-90°C), Wet (60-70°C)
- Cold tires = hard, poor grip; Overheated tires = slippery
- Tire wear affects grip; tires can "suddenly die"

### Track Conditions

- Rain reduces grip significantly (especially on Hard/Soft tires)
- Off-track surfaces (grass, gravel) slow and damage vehicles

### Ghost Mode

States: Inactive → Pending Enter → Active → Pending Exit
Triggers: Low speed, lap count, overlap, pit zone

### Pit Stop

Three zones: Enter → Fix → Exit
- Speed limit enforced in Fix zone
- Auto tire repair on stop
- Driver/bot change possible
- Tire compound change possible

### Race Dashboard Features

- Driver Change: Swap bots mid-race
- Request Pit Stop: Signal bot to pit
- Emergency Pit Stop: Teleport to pit (30s cooldown)
- Back to Track: Teleport to track center (30s cooldown)

## Tournament Format

- Qualifying: Unscored, determines starting positions
- 4 Scored Races: 1 hour each
- Final Race: 30 minutes
- Points scale: Race 1 (3/3x), Race 2 (4/3x), Race 3 (5/3x), Race 4 (6/3x), Final (7/3x)
- Final Lap: 5 minutes to complete current lap after time expires

## Key Racing Concepts

- Stint: Segment between pit stops
- Race Pace: Sustainable lap time
- Out-lap/In-lap: First lap after pit / Last lap before pit
- Racing Line: Optimal path through corners
- Apex: Innermost point of corner trajectory
- Undercut: Early pit stop to gain positions
- Overcut: Staying out longer on old tires

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No project found | Run `hackarena use 3` |
| GitHub API 404 | Check `GH_TOKEN` permissions |
| C++ build fails on Windows | Use MSVC (Visual Studio), not MinGW |
| TypeScript submit error | Add `user/package.json` to manifest |
| Login required (exit 2) | Run `hackarena auth login` |
| GitHub rate limit | Use own hotspot or authenticated requests |
| No backend for aarch64-apple-darwin | Backend only on Windows - use teammate's backend |
| No backend for linux | Check if Linux build available, otherwise use Windows |

## Pre-commit Checklist

- [ ] Bot runs without errors
- [ ] `requirements.txt` includes all dependencies
- [ ] No hardcoded secrets or tokens
- [ ] Manifest includes correct files for submission