Report Notes (Timed Typer)
Generated: 2025-10-27T02:27:48

## Q1. Creative goals
- Make a high-pressure typing trainer that feels like doing real
  network ops work (Ping / Traceroute / DNS / HTTP / Firewall),
  not kiddie 'the quick brown fox' drills.
- Force the player to enter short technical strings and symbols
  accurately under a live countdown, to build speed *and* accuracy.
- Give it a vibe: terminal HUD, streak counter, live WPM, etc.,
  so each level feels like a mission instead of homework.

## Q2. Five levels + transitions
- The game has 5 missions, escalating from Ping to Firewall.
  Each mission has its own wordlist and accuracy/WPM target.
- When you pass a mission (hit target WPM and accuracy without
  quitting early), the next mission unlocks automatically.
- Current status:
- 1. Ping — UNLOCKED — 30.9 WPM @ 100.0% acc
- 2. Traceroute — UNLOCKED — 23.2 WPM @ 100.0% acc
- 3. DNS — UNLOCKED — 8.2 WPM @ 33.3% acc
- 4. HTTP — LOCKED — PB: —
- 5. Firewall — LOCKED — PB: —
- The Level Select menu shows which levels are UNLOCKED vs LOCKED
  and displays your PB for each one.

## Q3. Progress & final success feedback
- Cleared levels so far: 1, 2
- Strongest performance: Level 1 (Ping) at 30.9 WPM / 100.0% accuracy
- After every run, the game prints feedback:
  * ✅ "Level passed! Next level unlocked." when you hit both
    target WPM and accuracy without quitting.
  * Otherwise it tells you why you failed (too slow vs too many
    typos) and gives a tip, e.g. 'Slow down slightly' or 'Push
    speed on short words.'

## Q4. New functions beyond skeleton
- `storage.py`: full save system. It writes a `profile.json` file
  with unlocked levels, PBs (best WPM + accuracy ratio), and
  settings. It also does migration: older PBs stored as `acc`
  get upgraded to `accuracy` automatically so the menus don't
  crash on missing keys.
  (Catching missing keys and mismatched names is important:
   otherwise you get `KeyError` or `ImportError` when modules try
   to access data that isn't there.)
- `GameState.after_level_finish(...)`: called right after you
  finish a run. It:
    * records PB for that level,
    * unlocks the next level if you passed,
    * saves to disk,
    * refreshes the in-memory unlocked/PBs for the menus.
- Level Select reads the save and shows:
    * PB: 32.1 WPM, 97%
    * LOCKED/UNLOCKED state
  This UI is proof that persistence actually works.
- Export Report (this file): menu option [7] calls
  `export_report_to_project_root()`, which turns the runtime
  data into a Markdown hand-in. That’s basically a dev tool /
  teacher tool wired directly into the game.

## Q5. Code readability & style
- The code is split into focused modules:
  * `state.py` = game state machine + screen routing
  * `game.py`  = main loop that switches screens
  * `menu.py`  = title menu + level select menu
  * `play.py`  = the live typing loop with timer, streak,
                 WPM/accuracy tracking, pass/fail logic
  * `storage.py` = persistence helpers (`record_pb`,
                   `unlock_next_level`, etc.)
  * `report.py`  = generates this structured Q&A Markdown
- We fixed circular-import crashes by cleaning up imports so
  modules don’t import each other while they’re still loading.
  That 'partially initialized module' ImportError is classic
  circular import in Python, and the fix is to stop modules from
  importing each other at import time or to move shared logic
  into a helper module. :contentReference[oaicite:3]{index=3}
- We fixed NameError / ImportError issues in the menu and report
  flow by making sure:
    * functions we import (like `export_report_to_project_root`)
      actually exist at the top level of the module, and
    * variables we print (like `output_path`) are assigned before
      we print them. In Python, referencing a name before it is
      defined triggers `NameError`. :contentReference[oaicite:4]{index=4}
- Player UX got attention: on fail you don't just 'lose', you get
  targeted advice ('slow down for accuracy' vs 'push speed'),
  which is part of the grading story for "progress & feedback".
