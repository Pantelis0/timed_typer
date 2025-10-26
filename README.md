# Timed Typer — Network Ops

> **Typing speed meets networking logic.**  
> A console-based, progressive typing game and self-testing suite built entirely in Python.  
> Includes training modes, self-tests, auto-demos, and one-click reporting.

---

## 🎯 Overview

**Timed Typer — Network Ops** is a text-based typing trainer disguised as a mini-game about computer networking.  
Each level introduces real-world network terms — like `tcp`, `dns`, `ping`, or `firewall` — which the player must type quickly and accurately to advance.

The program tracks:

- Words Per Minute (WPM)
- Accuracy (%)
- Streaks and Typos
- Unlock progression and PB scores

It also includes *automated self-testing*, *demo simulations*, and *report export* for instructors or evaluators.

---

## 🏗️ Features

| Mode | Description |
|------|--------------|
| **Start / Level Select** | Play the core typing levels (Ping → Traceroute → DNS → HTTP → Firewall). |
| **Practice Mode** | Endless random words from all levels, for casual speed training. |
| **Focus Practice** | Practice one level’s vocabulary repeatedly. |
| **Self-Test (auto)** | Runs scripted tests for reproducibility (used for QA / grading). |
| **Demo (auto)** | Simulates a perfect or imperfect run for presentation. |
| **Export Report** | Generates `REPORT.md` with all stats and PBs. |

---

## ⚙️ Requirements

| Component | Version |
|------------|----------|
| Python | 3.10 – 3.13 |
| OS | Windows 10 / 11 (tested), Linux & macOS (CLI only) |
| Required Packages | `colorama` |
| Optional (Builder) | `pyinstaller` |

Install dependencies:

```bash
pip install colorama
```
(PyInstaller is only needed if you want to rebuild the single-file EXE.)

---
## ▶️ Run from Source
```bash
# Windows PowerShell
$env:PYTHONPATH = "$PWD\src"
py -m timed_typer.app
```
---
## 💻 Build the EXE (optional)
💻 Build the EXE (optional)
```bash
py -m PyInstaller --onefile --name TimedTyper --console --paths "$PWD\src" run_timed_typer.py
```
Output:
```bash
dist/TimedTyper.exe
```
---
## 🚀 CLI Flags (headless use)

Command	Action

| Command                             | Action                                      |
| ----------------------------------- | ------------------------------------------- |
| `--selftest`                        | Run automated self-tests and exit           |
| `--report`                          | Export a fresh `REPORT.md` and exit         |
| `--demo <level> [speed] [accuracy]` | Simulate gameplay (e.g. `--demo 3 1.2 0.9`) |


## Examples:
```bash
.\dist\TimedTyper.exe --selftest
.\dist\TimedTyper.exe --demo 5 1.0 1.0
.\dist\TimedTyper.exe --report
```
---
## 📄 Generated Files
| File                         | Purpose                                          |
| ---------------------------- | ------------------------------------------------ |
| `REPORT.md`                  | Automatically created summary of test runs & PBs |
| `TimedTyper.exe`             | Single-file build for Windows                    |
| `TimedTyper.spec` / `build/` | Temporary build artifacts (safe to delete)       |
---
## 🧠 Educational Angle
Each level represents a networking layer concept:

| Level | Theme      | Example Words                               |
| ----- | ---------- | ------------------------------------------- |
| 1     | Ping       | `tcp`, `net`, `ping`, `deny`, `post`        |
| 2     | Traceroute | `ttl`, `route`, `allow[udp]`, `domain`      |
| 3     | DNS        | `resolve`, `txt`, `ns`, `cache`             |
| 4     | HTTP       | `GET`, `POST`, `header`, `cookie`           |
| 5     | Firewall   | `policy`, `drop`, `log`, `rule`, `port=443` |

## 📊 Example Output
```bash
=== RESULTS ===
Level: DNS
WPM:   28.6
Acc:   94.1%
OK/All:32/33  Typos:1
 >> ✅ Demo meets the level targets.
```
---
## 🧩 Credits
Lead Developer: Pantelis Kefalas

Concept & Design: Network Ops Training Lab 2025

Libraries: Python Standard Library, Colorama

---

## 🧱 `DESIGN.md`

## Design Document — Timed Typer (Network Ops)

---

## 1. Purpose & Vision

Timed Typer gamifies networking terminology through fast, feedback-rich typing practice.  
The core goal: **train technical reflexes and accuracy** while reinforcing key concepts from networking.

---

## 2. Core Architecture

run_timed_typer.py ← launcher / CLI flag handler
src/
└── timed_typer/
├── app.py ← main menu & input loop
├── game.py ← high-level game state flow
├── play.py ← gameplay logic & timing
├── levels.py ← word banks & difficulty tuning
├── state.py ← GameState, Screen, player progress
├── selftest.py ← reproducible QA tests
├── demo.py ← auto simulation / showcase
├── report.py ← markdown exporter
└── utils.py ← shared helpers & formatting

### Key Entities

| Class | Responsibility |
|--------|----------------|
| `GameState` | Tracks current screen, unlocked levels, PB scores |
| `LevelConfig` | Per-level target WPM / accuracy and word list |
| `PlayStats` | Tracks OK, typos, elapsed time, WPM, accuracy |
| `HUD` (implicit) | Prints progress metrics to console each turn |

---

## 4. Timing & Scoring

| Metric | Formula |
|---------|----------|
| **WPM** | `(correct_chars / 5) / (elapsed_seconds / 60)` |
| **Accuracy %** | `ok / (ok + typos) * 100` |
| **Unlock Condition** | `WPM ≥ target` and `Acc ≥ target` |

---

## 5. Data Design

Each level’s config (in `levels.py`) defines:

```python
LevelConfig(
    name="DNS",
    target_wpm=25,
    min_accuracy=0.85,
    words=[
        "dns","domain","cache","resolve","ttl",
        "zone","ns","cname","txt","allow[udp]",
        "deny[tcp]","port=443","/api","get","post"
    ],
)
```
This feeds the generator that ensures no immediate duplicate words (tested in Self-Test A).

---
## 6. Automation Modes

| Mode         | Description                  | Used For             |
| ------------ | ---------------------------- | -------------------- |
| `--selftest` | Runs repeatable logic checks | QA / grading         |
| `--demo`     | Simulates real gameplay      | Showcase / benchmark |
| `--report`   | Exports `REPORT.md`          | Documentation        |

All automation modes rely on the same engine used by human play, ensuring consistency.

---
## 9. Performance & Packaging

Runtime footprint < 10 MB as EXE

Load time ≈ 0.1 s

Pure Python; no external data files

Built with:
```python
py -m PyInstaller --onefile --name TimedTyper --console --paths "$PWD\src" run_timed_typer.py
```

---
10. Summary
Timed Typer (Network Ops) blends technical vocabulary, reaction training, and self-testing automation.
It demonstrates command-line design, modular architecture, and reproducible builds with PyInstaller.

“Type fast. Think faster.”
— Pantelis Kefalas (2025)


---