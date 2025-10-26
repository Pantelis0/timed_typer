1) Creative concept (answers report Q1)

Title: Network Ops Typer
Hook: You’re a junior network engineer racing through live incidents. Each level simulates a different networking task (Ping → Traceroute → DNS → HTTP → Firewall Rules). You type command-like words quickly and accurately to “stabilize the network.”

Why this is good: it’s unique (network theme), naturally supports 5 levels, and makes difficulty ramps intuitive.

2) Five difficulty levels + transitions (answers Q2)
Level	Theme	Word set & length	Timer / pace	Extra mechanic	Transition rule
1	Ping	short common words (3–4 letters)	generous per-word timer	none	≥90% accuracy OR beat easy overall time unlocks L2
2	Traceroute	4–6 letters; adds hyphenated tokens (e.g., hop)	slightly stricter per-word	-1s penalty on typo	Finish with ≥85% accuracy to unlock L3
3	DNS	5–7 letters; includes dots/hostnames (cache, domain, resolve)	steady global timer + small per-word	combo streaks boost score	Keep WPM ≥ target and accuracy ≥85%
4	HTTP	mixed case and symbols (GET, POST, /api)	faster spawn rate	“Burst” waves—3 quick words	Survive 3 bursts without breaking combo
5	Firewall	longest tokens; brackets/equals (port=443, allow[udp])	tough global timer	strict accuracy gate (typo resets word)	Beat target score to win game

Pacing: Each level has a target WPM & min accuracy. Meeting both advances; missing one reruns the level with coaching tips.

3) Progress & feedback design (answers Q3)

During play (HUD):

Live WPM, Accuracy %, Streak meter, Level progress bar, Timer countdown.

Inline validation: green word locks in only when perfectly matched; otherwise show minimal red underline at the first mismatched char.

Micro-coaching: if 3 typos in 10s → show a 1-line hint like “Eyes on next 3 letters; breathe steady.”

End of level / end game:

Card with WPM, Accuracy, Time, Longest streak, Words completed, Typos.

Badge system: “Latency Slayer” (L1), “Pathfinder” (L2), “Resolver” (L3), “REST Ranger” (L4), “Firewall Guardian” (L5).

Show improvement since last attempt (stored in localStorage): e.g., “+6 WPM vs last run.”

4) New functions beyond the skeleton (answers Q4)

We’ll modularize around a tiny state machine. New functions we’ll add:

setState(nextState) → central screen/state switcher (MENU, LEVEL_SELECT, PLAY, PAUSE, RESULTS).

generateWord(level) → word factory with per-level rules (length, symbols).

startTimer(mode) / stopTimer() / getElapsed() → timing utilities (global & per-word).

checkInput(target, typed) → returns {correctUpTo, complete, firstErrorIndex}.

updateHUD(stats) → WPM/Accuracy/Streak refresh.

scoreEvent(type) → handles points, streak boosts, penalties.

levelTargets(level) → returns {minAccuracy, targetWPM, timeBudget}.

persistRun(stats) / loadPB(level) → save/read personal bests (localStorage).

sfx(name) (optional) → minimal tick/confirm/error sounds with mute toggle.

uiToast(message, ttl) → small on-screen hints without breaking flow.

This directly addresses the “well-designed functions and modularization” requirement.

5) Coding style plan (answers Q5)

Readable names, short functions, single responsibility.

Doc-comments on each function: purpose, params, returns.

Consistent camelCase, const/let usage, no magic numbers (put in CONFIG).

Keep drawing/input code thin; push logic into pure functions (easy to test mentally).

Inline comments only where non-obvious; otherwise keep code clean.

6) Screens & flow (so menus are clear)

Screens: TitleMenu → LevelSelect → Play → Results (with Pause overlay).
TitleMenu: Start, Continue (resume last level), Options (SFX on/off), How to Play.
LevelSelect: Five cards (locked/unlocked), shows last PB badges.
Play: HUD + input field, big center word.
Results: metrics + badges + “retry/next level.”

State machine (pseudo):

state = 'MENU'
onClickStart -> setState('LEVEL_SELECT')
onSelectLevel(n) -> currentLevel = n; setState('PLAY'); startTimer('global')
onWordComplete -> scoreEvent('correct'); nextWord()
onTimeUp or LevelDone -> setState('RESULTS'); persistRun(stats)
onRetry -> resetLevel(); setState('PLAY')
onNext -> if passed targets then unlock next; setState('LEVEL_SELECT')
