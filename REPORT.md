# Timed Typer — Network Ops (Python)
_Auto-generated: 2025-10-26 23:09_

## Overview
- Console typing game about network operations (Ping → Traceroute → DNS → HTTP → Firewall + secret).
- Modes: Self-tests, Auto Demo, Practice, Focus Practice, Exportable Report.

## Level Targets & Personal Bests
| Level | Name | Min Accuracy | Target WPM | Time (s) | PB WPM | PB Acc | Unlocked |
|------:|------|--------------:|-----------:|---------:|-------:|-------:|:--------:|
| 1 | Ping | 80% | 12 | 45 | 27.9 | 100% | ✅ |
| 2 | Traceroute | 82% | 17 | 45 | 19.0 | 90% | ❌ |
| 3 | DNS | 85% | 25 | 60 | - | - | ❌ |
| 4 | HTTP | 87% | 32 | 60 | - | - | ❌ |
| 5 | Firewall | 90% | 40 | 75 | - | - | ❌ |

## Coaching Advice
- **Ping**: ✅ Meets target. Maintain consistency.
- **Traceroute**: ✅ Meets target. Maintain consistency.
- **DNS**: No PB yet. Run a `--demo 3 1.1 0.9` to preview pacing.
- **HTTP**: No PB yet. Run a `--demo 4 1.1 0.9` to preview pacing.
- **Firewall**: No PB yet. Run a `--demo 5 1.1 0.9` to preview pacing.

## How to run
```bash
py -m timed_typer.app
```
- Headless: `TimedTyper.exe --selftest`, `--demo 3 1.2 0.9`, `--report`