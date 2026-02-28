"""Tkinter UI for the orthophony memory test."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from orthophony_memory.constants import (
    DEFAULT_DISPLAY_SECONDS,
    DEFAULT_SEQUENCE_LENGTH,
    RECALL_GRID_COLUMNS,
)
from orthophony_memory.engine import MemoryGameEngine
from orthophony_memory.models import RoundConfig, SymbolCard
from orthophony_memory.storage import BestScoreStore


class MemoryTestApp(tk.Tk):
    """Main application window and interaction flow."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Orthophony Memory Test")
        self.geometry("980x760")
        self.minsize(900, 700)

        self.engine = MemoryGameEngine()
        self.best_score_store = BestScoreStore()

        self.total_points = 0
        self.round_points = 0
        self.best_round_points = self.best_score_store.load()

        self.current_config: RoundConfig | None = None
        self.current_sequence: list[SymbolCard] = []
        self.recall_cards: list[SymbolCard] = []
        self.selected_cards: set[SymbolCard] = set()
        self.selections: list[SymbolCard] = []

        self._display_index = 0
        self._scheduled_id: str | None = None
        self._recall_active = False

        self.sequence_length_var = tk.IntVar(value=DEFAULT_SEQUENCE_LENGTH)
        self.display_seconds_var = tk.StringVar(value=str(DEFAULT_DISPLAY_SECONDS))
        self.status_var = tk.StringVar(value="Configure the game, then click Start round.")
        self.round_points_var = tk.StringVar()
        self.total_points_var = tk.StringVar()
        self.best_points_var = tk.StringVar()
        self.sequence_result_var = tk.StringVar(value="")

        self.card_canvases: dict[SymbolCard, tk.Canvas] = {}

        self._build_layout()
        self._update_score_labels()
        self._draw_focus_message("Ready")

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_layout(self) -> None:
        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)

        controls = ttk.LabelFrame(root, text="Round settings", padding=10)
        controls.pack(fill="x")

        ttk.Label(controls, text="Symbols to memorize (1-16):").grid(
            row=0, column=0, padx=(0, 8), pady=4, sticky="w"
        )
        self.sequence_spin = tk.Spinbox(
            controls,
            from_=1,
            to=16,
            textvariable=self.sequence_length_var,
            width=6,
        )
        self.sequence_spin.grid(row=0, column=1, padx=(0, 20), pady=4, sticky="w")

        ttk.Label(controls, text="Display time per symbol (seconds):").grid(
            row=0, column=2, padx=(0, 8), pady=4, sticky="w"
        )
        self.display_spin = tk.Spinbox(
            controls,
            from_=0.2,
            to=10.0,
            increment=0.1,
            textvariable=self.display_seconds_var,
            width=8,
        )
        self.display_spin.grid(row=0, column=3, padx=(0, 20), pady=4, sticky="w")

        self.start_button = ttk.Button(
            controls,
            text="Start round",
            command=self.start_round,
        )
        self.start_button.grid(row=0, column=4, padx=4, pady=4, sticky="e")

        points_frame = ttk.LabelFrame(root, text="Points", padding=10)
        points_frame.pack(fill="x", pady=(10, 0))

        ttk.Label(points_frame, textvariable=self.round_points_var).grid(
            row=0, column=0, padx=(0, 24), sticky="w"
        )
        ttk.Label(points_frame, textvariable=self.total_points_var).grid(
            row=0, column=1, padx=(0, 24), sticky="w"
        )
        ttk.Label(points_frame, textvariable=self.best_points_var).grid(
            row=0, column=2, padx=(0, 24), sticky="w"
        )

        ttk.Label(
            root,
            textvariable=self.status_var,
            font=("TkDefaultFont", 11, "bold"),
        ).pack(fill="x", pady=(10, 6))

        memorization_frame = ttk.LabelFrame(root, text="Memorization phase", padding=10)
        memorization_frame.pack(fill="x")
        self.focus_canvas = tk.Canvas(
            memorization_frame,
            width=280,
            height=280,
            bg="white",
            highlightthickness=2,
            highlightbackground="#94A3B8",
        )
        self.focus_canvas.pack(pady=4)

        recall_frame = ttk.LabelFrame(root, text="Recall phase", padding=10)
        recall_frame.pack(fill="both", expand=True, pady=(10, 0))

        self.recall_grid = ttk.Frame(recall_frame)
        self.recall_grid.pack(fill="both", expand=True)

        for column in range(RECALL_GRID_COLUMNS):
            self.recall_grid.columnconfigure(column, weight=1)

        ttk.Label(
            root,
            textvariable=self.sequence_result_var,
            wraplength=920,
            justify="left",
        ).pack(fill="x", pady=(10, 0))

    def start_round(self) -> None:
        config = self._read_config_from_controls()
        if config is None:
            return

        self._cancel_scheduled_callback()
        self._set_controls_enabled(False)

        self.current_config = config
        self.current_sequence = self.engine.create_round_sequence(config.sequence_length)
        self.recall_cards = self.engine.shuffled_recall_pool()
        self.selected_cards.clear()
        self.selections.clear()
        self.round_points = 0
        self._display_index = 0
        self._recall_active = False
        self.sequence_result_var.set("")
        self._update_score_labels()

        self._clear_recall_grid()
        self.status_var.set(
            f"Memorization started: symbol 1 of {len(self.current_sequence)}."
        )
        self._show_next_symbol()

    def _read_config_from_controls(self) -> RoundConfig | None:
        try:
            sequence_length = int(self.sequence_length_var.get())
            display_seconds = float(self.display_seconds_var.get())
            return RoundConfig(
                sequence_length=sequence_length,
                display_seconds=display_seconds,
            )
        except (ValueError, tk.TclError):
            messagebox.showerror(
                "Invalid settings",
                "Please choose a sequence length between 1 and 16 and a positive display time.",
            )
            return None

    def _show_next_symbol(self) -> None:
        if not self.current_config:
            return

        if self._display_index >= len(self.current_sequence):
            self._draw_focus_message("Recall phase")
            self.status_var.set(
                f"Select symbol 1 of {len(self.current_sequence)} in the right order."
            )
            self._start_recall_phase()
            return

        symbol = self.current_sequence[self._display_index]
        self._draw_symbol(self.focus_canvas, symbol, inset=36)

        self._display_index += 1
        if self._display_index < len(self.current_sequence):
            self.status_var.set(
                f"Memorization: symbol {self._display_index + 1} of "
                f"{len(self.current_sequence)}."
            )
        else:
            self.status_var.set("Memorization complete. Get ready for recall.")

        self._scheduled_id = self.after(
            self.current_config.display_milliseconds,
            self._show_next_symbol,
        )

    def _start_recall_phase(self) -> None:
        self._recall_active = True
        self.card_canvases.clear()
        self._clear_recall_grid()

        for index, card in enumerate(self.recall_cards):
            row = index // RECALL_GRID_COLUMNS
            col = index % RECALL_GRID_COLUMNS
            canvas = tk.Canvas(
                self.recall_grid,
                width=120,
                height=120,
                bg="white",
                highlightthickness=2,
                highlightbackground="#CBD5E1",
                cursor="hand2",
            )
            canvas.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            self._draw_symbol(canvas, card, inset=22)
            canvas.bind("<Button-1>", lambda _event, symbol=card: self._on_card_click(symbol))
            self.card_canvases[card] = canvas

    def _on_card_click(self, chosen: SymbolCard) -> None:
        if not self._recall_active or chosen in self.selected_cards:
            return

        expected_index = len(self.selections)
        expected = self.current_sequence[expected_index]
        is_final_choice = expected_index == len(self.current_sequence) - 1

        is_correct, delta = self.engine.score_choice(expected, chosen, is_final_choice)
        self.round_points += delta
        self.total_points += delta
        self._update_score_labels()

        if is_correct:
            self.selections.append(chosen)
            self.selected_cards.add(chosen)
            self._highlight_card(chosen, "#16A34A")

            if is_final_choice:
                self._finish_round(
                    success=True,
                    status_message=f"Success! You completed the sequence. Round points: {self.round_points}.",
                )
                return

            self.status_var.set(
                f"Correct. Select symbol {len(self.selections) + 1} of {len(self.current_sequence)}."
            )
            return

        self._highlight_card(chosen, "#DC2626")
        self._highlight_card(expected, "#2563EB")
        self._finish_round(
            success=False,
            status_message=(
                f"Incorrect order. Expected: {expected.label}. "
                f"Round points: {self.round_points}."
            ),
        )

    def _finish_round(self, success: bool, status_message: str) -> None:
        self._recall_active = False
        self._cancel_scheduled_callback()
        self._set_controls_enabled(True)

        for canvas in self.card_canvases.values():
            canvas.unbind("<Button-1>")
            canvas.configure(cursor="")

        self.best_round_points = self.best_score_store.save_if_higher(self.round_points)
        self._update_score_labels()
        self.status_var.set(status_message)

        prefix = "Sequence (correct order): "
        self.sequence_result_var.set(prefix + self.engine.sequence_labels(self.current_sequence))

        if success:
            self._draw_focus_message("Round complete")
        else:
            self._draw_focus_message("Round ended")

    def _set_controls_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self.sequence_spin.configure(state=state)
        self.display_spin.configure(state=state)
        self.start_button.configure(state=state)

    def _update_score_labels(self) -> None:
        self.round_points_var.set(f"Round points: {self.round_points}")
        self.total_points_var.set(f"Session points: {self.total_points}")
        self.best_points_var.set(f"Best round score: {self.best_round_points}")

    def _draw_focus_message(self, message: str) -> None:
        self.focus_canvas.delete("all")
        self.focus_canvas.create_text(
            140,
            140,
            text=message,
            font=("TkDefaultFont", 16, "bold"),
            fill="#334155",
        )

    def _clear_recall_grid(self) -> None:
        for child in self.recall_grid.winfo_children():
            child.destroy()

    def _highlight_card(self, card: SymbolCard, border_color: str) -> None:
        canvas = self.card_canvases.get(card)
        if not canvas:
            return
        canvas.configure(highlightbackground=border_color, highlightcolor=border_color)

    def _draw_symbol(self, canvas: tk.Canvas, card: SymbolCard, inset: int) -> None:
        canvas.delete("all")

        width = int(canvas.cget("width"))
        height = int(canvas.cget("height"))
        left, top = inset, inset
        right, bottom = width - inset, height - inset
        center_x = width // 2
        center_y = height // 2

        if card.shape == "circle":
            canvas.create_oval(
                left,
                top,
                right,
                bottom,
                fill=card.color_hex,
                outline="#1F2937",
                width=2,
            )
        elif card.shape == "triangle":
            canvas.create_polygon(
                center_x,
                top,
                right,
                bottom,
                left,
                bottom,
                fill=card.color_hex,
                outline="#1F2937",
                width=2,
            )
        elif card.shape == "square":
            side = min(right - left, bottom - top)
            half = side // 2
            canvas.create_rectangle(
                center_x - half,
                center_y - half,
                center_x + half,
                center_y + half,
                fill=card.color_hex,
                outline="#1F2937",
                width=2,
            )
        elif card.shape == "rectangle":
            rect_width = int((right - left) * 0.95)
            rect_height = int((bottom - top) * 0.6)
            canvas.create_rectangle(
                center_x - rect_width // 2,
                center_y - rect_height // 2,
                center_x + rect_width // 2,
                center_y + rect_height // 2,
                fill=card.color_hex,
                outline="#1F2937",
                width=2,
            )
        else:
            canvas.create_text(center_x, center_y, text=card.label)

    def _cancel_scheduled_callback(self) -> None:
        if self._scheduled_id:
            self.after_cancel(self._scheduled_id)
            self._scheduled_id = None

    def _on_close(self) -> None:
        self._cancel_scheduled_callback()
        self.destroy()


def launch_app() -> None:
    app = MemoryTestApp()
    app.mainloop()

