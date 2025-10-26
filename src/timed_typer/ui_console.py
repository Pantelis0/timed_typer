"""
Console HUD + results display with color.
"""
from colorama import Fore, Style
from .scoring import RunStats

def _color_val(val: float, good_thresh: float, mid_thresh: float, invert: bool = False) -> str:
    """
    Color helper. If invert=True, lower is better.
    """
    x = val
    good = x <= good_thresh if invert else x >= good_thresh
    mid  = (good_thresh > x >= mid_thresh) if not invert else (good_thresh < x <= mid_thresh)
    if good:
        return Fore.GREEN
    if mid:
        return Fore.YELLOW
    return Fore.RED

def render_hud(level_name: str, remaining_s: int, wpm_live: float, acc: float, streak: int) -> None:
    acc_pct = acc * 100.0
    # thresholds tuned for readability; you can tweak per level if you want
    c_wpm = _color_val(wpm_live, good_thresh=20, mid_thresh=12, invert=False)
    c_acc = _color_val(acc_pct,  good_thresh=90, mid_thresh=80, invert=False)
    c_stk = Fore.GREEN if streak >= 5 else (Fore.YELLOW if streak >= 3 else Fore.RESET)

    line = (
        f"[{level_name}] "
        f"Time:{remaining_s:>3}s | "
        f"{c_wpm}WPM:{wpm_live:>5.1f}{Style.RESET_ALL} | "
        f"{c_acc}Acc:{acc_pct:>5.1f}%{Style.RESET_ALL} | "
        f"{c_stk}Streak:{streak}{Style.RESET_ALL}"
    )
    print(line)

def render_hud_practice(elapsed_s: int, wpm_live: float, acc: float, streak: int) -> None:
    acc_pct = acc * 100.0
    c_wpm = _color_val(wpm_live, good_thresh=20, mid_thresh=12, invert=False)
    c_acc = _color_val(acc_pct,  good_thresh=90, mid_thresh=80, invert=False)
    c_stk = Fore.GREEN if streak >= 5 else (Fore.YELLOW if streak >= 3 else Fore.RESET)

    line = (
        f"[Practice] "
        f"Elapsed:{elapsed_s:>3}s | "
        f"{c_wpm}WPM:{wpm_live:>5.1f}{Style.RESET_ALL} | "
        f"{c_acc}Acc:{acc_pct:>5.1f}%{Style.RESET_ALL} | "
        f"{c_stk}Streak:{streak}{Style.RESET_ALL}"
    )
    print(line)

def toast(msg: str) -> None:
    print(f"{Fore.CYAN} >> {msg}{Style.RESET_ALL}")

def results_card(level_name: str, stats: RunStats, wpm_final: float) -> None:
    header = f"{Fore.MAGENTA}\n=== RESULTS ==={Style.RESET_ALL}"
    print(header)
    print(f"Level: {level_name}")
    print(f"WPM:   {Fore.GREEN if wpm_final>=20 else Fore.YELLOW if wpm_final>=12 else Fore.RED}{wpm_final:.1f}{Style.RESET_ALL}")
    print(f"Acc:   {Fore.GREEN if stats.accuracy>=0.9 else Fore.YELLOW if stats.accuracy>=0.8 else Fore.RED}{stats.accuracy*100:.1f}%{Style.RESET_ALL}")
    print(f"OK/All:{stats.words_ok}/{stats.words_total}  Typos:{stats.typos}")
