"""
Tkinter GUI for Ultimate Tic-Tac-Toe -- Pokemon edition.

A point-and-click front-end on top of the pure game engine in
ultimate_tictactoe.py. Click any tile in any mini-board that hasn't been
decided yet to play it there.

Pokemon theme
-------------
Player X battles with Fire-type Pokemon, Player O with Water-type (see
PLAYER_TYPE below if you want to retheme). Whenever a player wins a
mini-board ("claims a big tile"), a random Pokemon of their type is caught
and its sprite is shown on that tile. A drawn mini-board shows a Poke Ball
instead.

Sprites are downloaded from the PokeAPI sprite repo on first use and cached
in .pokemon_cache/ next to this file. If a download fails (e.g. no
internet), that tile just falls back to a plain colored letter.

Run:  python gui.py
"""

from __future__ import annotations

import os
import random
import tkinter as tk
from tkinter import font as tkfont
from urllib.error import URLError
from urllib.request import urlopen

from ultimate_tictactoe import Player, UltimateTicTacToe, WIN_LINES

# ---------------------------------------------------------------------------
# Pokemon theme data
# ---------------------------------------------------------------------------

SPRITE_BASE_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites"
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".pokemon_cache")
DOWNLOAD_TIMEOUT = 3  # seconds -- keeps the GUI responsive if offline

# Each player battles with Pokemon of one type. Swap these to retheme.
PLAYER_TYPE: dict[Player, str] = {Player.X: "Fire", Player.O: "Water"}

TYPE_COLOR = {
    "Fire": "#F08030",
    "Water": "#6890F0",
    "Draw": "#C6C6A7",  # Normal-type grey, used for drawn mini-boards
}

# A handful of recognizable Pokemon per type: (name, national dex number).
POKEMON_BY_TYPE: dict[str, list[tuple[str, int]]] = {
    "Fire": [
        ("Charmander", 4), ("Charmeleon", 5), ("Charizard", 6),
        ("Vulpix", 37), ("Ninetales", 38),
        ("Growlithe", 58), ("Arcanine", 59),
        ("Ponyta", 77), ("Rapidash", 78),
        ("Magmar", 126), ("Flareon", 136), ("Moltres", 146),
        ("Cyndaquil", 155), ("Quilava", 156), ("Typhlosion", 157),
        ("Houndour", 228), ("Houndoom", 229),
        ("Torchic", 255), ("Combusken", 256), ("Blaziken", 257),
        ("Chimchar", 390), ("Monferno", 391), ("Infernape", 392),
    ],
    "Water": [
        ("Squirtle", 7), ("Wartortle", 8), ("Blastoise", 9),
        ("Psyduck", 54), ("Golduck", 55),
        ("Poliwag", 60), ("Poliwhirl", 61), ("Poliwrath", 62),
        ("Tentacool", 72), ("Slowpoke", 79),
        ("Seel", 86), ("Dewgong", 87),
        ("Shellder", 90), ("Cloyster", 91),
        ("Krabby", 98), ("Kingler", 99),
        ("Horsea", 116), ("Seadra", 117),
        ("Goldeen", 118), ("Seaking", 119),
        ("Staryu", 120), ("Starmie", 121),
        ("Magikarp", 129), ("Gyarados", 130), ("Lapras", 131), ("Vaporeon", 134),
        ("Totodile", 158), ("Croconaw", 159), ("Feraligatr", 160),
        ("Mudkip", 258), ("Marshtomp", 259), ("Swampert", 260),
    ],
}

# ---------------------------------------------------------------------------
# Sprite loading / caching
# ---------------------------------------------------------------------------


def _fetch_sprite(relative_path: str) -> str | None:
    """Return a local cached path for a PokeAPI sprite, downloading it on
    first use. Returns None if it can't be fetched (e.g. no internet)."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    local_path = os.path.join(CACHE_DIR, relative_path.replace("/", "_"))
    if os.path.exists(local_path):
        return local_path
    try:
        with urlopen(f"{SPRITE_BASE_URL}/{relative_path}", timeout=DOWNLOAD_TIMEOUT) as resp:
            data = resp.read()
    except (URLError, OSError):
        return None
    with open(local_path, "wb") as f:
        f.write(data)
    return local_path


def _load_photo(local_path: str, zoom: int, subsample: int = 1) -> tk.PhotoImage | None:
    """Load a sprite, scaled by zoom/subsample (both PokeAPI sprite sizes
    are fixed, so a simple integer ratio is enough)."""
    try:
        img = tk.PhotoImage(file=local_path)
        if zoom > 1:
            img = img.zoom(zoom, zoom)
        if subsample > 1:
            img = img.subsample(subsample, subsample)
        return img
    except tk.TclError:
        return None


def random_pokemon(poke_type: str) -> tuple[str, tk.PhotoImage | None]:
    """Pick a random Pokemon of the given type. Returns its name and sprite
    (sprite is None if it couldn't be downloaded)."""
    name, dex_number = random.choice(POKEMON_BY_TYPE[poke_type])
    path = _fetch_sprite(f"pokemon/{dex_number}.png")
    photo = _load_photo(path, zoom=3, subsample=2) if path else None  # 96px -> 144px
    return name, photo


def pokeball_sprite() -> tk.PhotoImage | None:
    path = _fetch_sprite("items/poke-ball.png")
    return _load_photo(path, zoom=4) if path else None  # 30px -> 120px


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

ROOT_BG = "#FFF8E7"
HEADER_BG = "#DC0A2D"
HEADER_FG = "#FFFFFF"
GRID_COLOR = "#2C2C54"
HIGHLIGHT_COLOR = "#FFCB05"
CELL_BG = "#FFFFFF"
CELL_HOVER_BG = "#FFF3CD"


class UltimateTicTacToeGUI:
    """A 9x9 grid of buttons (nine 3x3 mini-boards) wired to a game."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.game = UltimateTicTacToe()

        # board -> (sprite or None, fallback letter, card bg, card fg)
        self._assigned: dict[int, tuple[tk.PhotoImage | None, str, str, str]] = {}
        self._announcement: str | None = None

        root.title("Ultimate Tic-Tac-Toe: Pokemon Edition")
        root.configure(bg=ROOT_BG)
        root.resizable(False, False)

        icon = pokeball_sprite()
        if icon is not None:
            self._icon = icon  # keep a reference alive
            root.iconphoto(True, icon)

        header = tk.Frame(root, bg=HEADER_BG)
        header.pack(fill="x")
        tk.Label(
            header, text="Ultimate Tic-Tac-Toe", bg=HEADER_BG, fg=HEADER_FG,
            font=("Segoe UI", 20, "bold"), pady=10,
        ).pack()

        self.status_var = tk.StringVar()
        self.status_label = tk.Label(
            root, textvariable=self.status_var, bg=ROOT_BG,
            font=("Segoe UI", 13, "bold"), pady=8,
        )
        self.status_label.pack()

        grid_frame = tk.Frame(root, bg=GRID_COLOR)
        grid_frame.pack(padx=12, pady=(0, 12))

        cell_font = tkfont.Font(family="Segoe UI", size=18, weight="bold")
        overlay_font = ("Segoe UI", 40, "bold")

        self.buttons: list[list[tk.Button]] = [[None] * 9 for _ in range(9)]  # type: ignore[list-item]
        self.overlays: list[tk.Label] = [None] * 9  # type: ignore[list-item]
        self.wrappers: list[tk.Frame] = [None] * 9  # type: ignore[list-item]

        for board in range(9):
            br, bc = divmod(board, 3)
            wrapper = tk.Frame(grid_frame, bg=GRID_COLOR)
            wrapper.grid(row=br, column=bc, padx=3, pady=3)
            self.wrappers[board] = wrapper

            inner = tk.Frame(wrapper, bg=GRID_COLOR)
            inner.pack(padx=2, pady=2)

            for cell in range(9):
                cr, cc = divmod(cell, 3)
                btn = tk.Button(
                    inner,
                    text="",
                    width=3,
                    height=1,
                    font=cell_font,
                    bg=CELL_BG,
                    activebackground=CELL_HOVER_BG,
                    bd=1,
                    relief=tk.FLAT,
                    command=lambda b=board, c=cell: self.on_click(b, c),
                )
                btn.grid(row=cr, column=cc, padx=1, pady=1)
                btn.bind("<Enter>", lambda _e, b=btn: self._hover(b, True))
                btn.bind("<Leave>", lambda _e, b=btn: self._hover(b, False))
                self.buttons[board][cell] = btn

            overlay = tk.Label(inner, text="", font=overlay_font)
            self.overlays[board] = overlay

        tk.Button(
            root,
            text="New Game",
            command=self.reset,
            bg=HEADER_BG,
            fg=HEADER_FG,
            activebackground="#FF4D4D",
            activeforeground=HEADER_FG,
            font=("Segoe UI", 11, "bold"),
            padx=12,
            pady=4,
            bd=0,
        ).pack(pady=(0, 14))

        self.refresh()

    # ----- interaction -------------------------------------------------

    def on_click(self, board: int, cell: int) -> None:
        if not self.game.can_play(board, cell):
            return
        self.game.make_move(board, cell)
        self.refresh()

    def reset(self) -> None:
        self.game = UltimateTicTacToe()
        self._assigned.clear()
        self._announcement = None
        self.refresh()

    def _hover(self, btn: tk.Button, entering: bool) -> None:
        if str(btn["state"]) == tk.DISABLED:
            return
        btn.config(bg=CELL_HOVER_BG if entering else CELL_BG)

    # ----- rendering -----------------------------------------------------

    def refresh(self) -> None:
        """Redraw every tile, overlay, and the status line from game state."""
        self._announcement = None

        for board in range(9):
            mini = self.game.boards[board]

            for cell in range(9):
                btn = self.buttons[board][cell]
                played = mini.cells[cell]
                if played is None:
                    playable = self.game.can_play(board, cell)
                    btn.config(text="", state=tk.NORMAL if playable else tk.DISABLED, bg=CELL_BG)
                else:
                    color = TYPE_COLOR[PLAYER_TYPE[played]]
                    btn.config(text=str(played), fg=color, disabledforeground=color, state=tk.DISABLED, bg=CELL_BG)

            overlay = self.overlays[board]
            if mini.is_decided:
                if board not in self._assigned:
                    self._assigned[board] = self._catch(mini)
                photo, letter, bg, fg = self._assigned[board]
                if photo is not None:
                    overlay.config(image=photo, text="", bg=bg)
                else:
                    overlay.config(image="", text=letter, fg=fg, bg=bg)
                overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
                overlay.lift()
            else:
                overlay.place_forget()

        self._highlight_winning_line()
        self._update_status()

    def _catch(self, mini) -> tuple[tk.PhotoImage | None, str, str, str]:
        """Pick the sprite/letter shown on a mini-board that just became decided."""
        if mini.winner is not None:
            poke_type = PLAYER_TYPE[mini.winner]
            name, photo = random_pokemon(poke_type)
            self._announcement = f"{poke_type} Trainer caught {name}!"
            return photo, str(mini.winner), TYPE_COLOR[poke_type], "white"
        return pokeball_sprite(), "=", TYPE_COLOR["Draw"], "#666666"

    def _highlight_winning_line(self) -> None:
        """Mark the three mini-boards that complete the winning macro line, if any."""
        macro = self.game.macro_cells
        winning_boards: set[int] = set()
        if self.game.winner is not None:
            for a, b, c in WIN_LINES:
                if macro[a] is not None and macro[a] == macro[b] == macro[c]:
                    winning_boards = {a, b, c}
                    break
        for board, wrapper in enumerate(self.wrappers):
            wrapper.config(bg=HIGHLIGHT_COLOR if board in winning_boards else GRID_COLOR)

    def _update_status(self) -> None:
        if self.game.is_over:
            if self.game.is_draw:
                self.status_var.set("It's a draw!")
                self.status_label.config(fg="#666666")
            else:
                poke_type = PLAYER_TYPE[self.game.winner]
                self.status_var.set(f"{poke_type} Trainer wins the match!")
                self.status_label.config(fg=TYPE_COLOR[poke_type])
        elif self._announcement:
            self.status_var.set(self._announcement)
            self.status_label.config(fg="#333333")
        else:
            poke_type = PLAYER_TYPE[self.game.current_player]
            self.status_var.set(f"{poke_type} Trainer's turn")
            self.status_label.config(fg=TYPE_COLOR[poke_type])


def main() -> None:
    root = tk.Tk()
    UltimateTicTacToeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
