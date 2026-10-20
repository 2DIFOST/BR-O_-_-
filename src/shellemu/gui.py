"""Graphical user interface of the emulator (tkinter)."""
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

from .config import Config
from .errors import GuiUnavailableError
from .history import History
from .session import KIND_DEBUG, KIND_ERROR, KIND_INPUT, Session
from .shell import Shell

FONT = ("Courier", 11)
BACKGROUND = "#1e1e1e"
FOREGROUND = "#d4d4d4"
INPUT_COLOR = "#7ec699"
ERROR_COLOR = "#f48771"
DEBUG_COLOR = "#8a8a8a"
WINDOW_SIZE = "800x500"

TAG_COLORS = {
    KIND_INPUT: INPUT_COLOR,
    KIND_ERROR: ERROR_COLOR,
    KIND_DEBUG: DEBUG_COLOR,
}


class EmulatorWindow:
    """Window with an output area and an input line."""

    def __init__(self, shell: Shell, title: str) -> None:
        """Build the window for the given shell."""
        try:
            self.root = tk.Tk()
        except tk.TclError as error:
            raise GuiUnavailableError(str(error)) from error
        self.session = Session(shell, self)
        self.history = History()
        self.root.title(title)
        self.root.geometry(WINDOW_SIZE)
        self.output = self.build_output()
        self.prompt_label, self.entry = self.build_input_line()
        self.refresh_prompt()

    def build_output(self) -> ScrolledText:
        """Create the read-only area where the dialog is shown."""
        output = ScrolledText(
            self.root, font=FONT, bg=BACKGROUND, fg=FOREGROUND,
            state=tk.DISABLED, wrap=tk.WORD,
        )
        for tag, color in TAG_COLORS.items():
            output.tag_configure(tag, foreground=color)
        output.pack(fill=tk.BOTH, expand=True)
        return output

    def build_input_line(self) -> tuple[tk.Label, tk.Entry]:
        """Create the prompt label and the entry field below the output."""
        frame = tk.Frame(self.root, bg=BACKGROUND)
        frame.pack(fill=tk.X)
        label = tk.Label(frame, font=FONT, bg=BACKGROUND, fg=INPUT_COLOR)
        label.pack(side=tk.LEFT)
        entry = tk.Entry(
            frame, font=FONT, bg=BACKGROUND, fg=FOREGROUND,
            insertbackground=FOREGROUND, relief=tk.FLAT,
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        entry.bind("<Return>", self.on_enter)
        entry.bind("<Up>", self.on_up)
        entry.bind("<Down>", self.on_down)
        entry.focus_set()
        return label, entry

    def refresh_prompt(self) -> None:
        """Show the current prompt of the shell."""
        self.prompt_label.configure(text=self.session.shell.prompt())

    def write(self, text: str, kind: str) -> None:
        """Append a line to the output area and scroll down.

        Debug lines are duplicated to stdout of the real terminal.
        """
        self.output.configure(state=tk.NORMAL)
        self.output.insert(tk.END, text + "\n", kind)
        self.output.configure(state=tk.DISABLED)
        self.output.see(tk.END)
        if kind == KIND_DEBUG:
            print(text, flush=True)

    def on_enter(self, _event: tk.Event | None) -> None:
        """Handle the Enter key: execute the typed line."""
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        self.history.add(line)
        self.session.run_line(line)
        self.refresh_prompt()
        if self.session.finished:
            self.close()

    def on_up(self, _event: tk.Event | None) -> None:
        """Show the previous command from the history."""
        self.set_entry(self.history.previous())

    def on_down(self, _event: tk.Event | None) -> None:
        """Show the next command from the history."""
        self.set_entry(self.history.following())

    def set_entry(self, text: str) -> None:
        """Replace the content of the entry field."""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)

    def close(self) -> None:
        """Close the window."""
        self.root.destroy()

    def run(self, config: Config) -> None:
        """Run the startup actions, then the event loop.

        If the startup script ends with ``exit`` the window is closed
        without entering the loop.
        """
        self.session.startup(config)
        self.refresh_prompt()
        if self.session.finished:
            self.close()
        else:
            self.root.mainloop()
