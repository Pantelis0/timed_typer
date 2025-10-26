"""
App entrypoint. Run with:  python -m timed_typer.app
"""
import os, random  # <-- add
from colorama import init as colorama_init
from .game import run_game

def main() -> None:
    colorama_init()
    # Fixed seed unless user overrides with TIMED_TYPER_SEED
    seed = os.environ.get("TIMED_TYPER_SEED")
    if seed is None:
        random.seed(42)
    else:
        try:
            random.seed(int(seed))
        except ValueError:
            random.seed(seed)
    run_game()

if __name__ == "__main__":
    main()
