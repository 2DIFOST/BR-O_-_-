"""Graphical user interface of the emulator (tkinter)."""
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

from .history import History
from .response import Response
from .shell import Shell

FONT = ("Courier", 11)
BACKGROUND = "#1e1e1e"
FOREGROUND = "#d4d4d4"
INPUT_COLOR = "#7ec699"
ERROR_COLOR = "#f48771"
WINDOW_SIZE = "800x500"

TAG_INPUT = "input"
TAG_ERROR = "error"


class EmulatorWindow:
    """Window with an output area and an input line."""

    def __init__(self, shell: Shell, title: str) -> None:
        """Build the window for the given shell."""
        self.shell = shell
        self.history = History()
        self.root = tk.Tk()
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
        output.tag_configure(TAG_INPUT, foreground=INPUT_COLOR)
        output.tag_configure(TAG_ERROR, foreground=ERROR_COLOR)
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
        self.prompt_label.configure(text=self.shell.prompt())

    def write(self, text: str, tag: str | None = None) -> None:
        """Append a line to the output area and scroll down."""
        self.output.configure(state=tk.NORMAL)
        self.output.insert(tk.END, text + "\n", tag)
        self.output.configure(state=tk.DISABLED)
        self.output.see(tk.END)

    def show_response(self, response: Response) -> None:
        """Print all messages of a command."""
        for message in response.messages:
            tag = TAG_ERROR if message.is_error else None
            self.write(message.text, tag)

    def run_line(self, line: str) -> Response:
        """Echo a line as if typed, execute it and show the result."""
        self.write(self.shell.prompt() + line, TAG_INPUT)
        response = self.shell.execute(line)
        self.show_response(response)
        self.refresh_prompt()
        return response

    def on_enter(self, _event: tk.Event) -> None:
        """Handle the Enter key: execute the typed line."""
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        self.history.add(line)
        if self.run_line(line).should_exit:
            self.close()

    def on_up(self, _event: tk.Event) -> None:
        """Show the previous command from the history."""
        self.set_entry(self.history.previous())

    def on_down(self, _event: tk.Event) -> None:
        """Show the next command from the history."""
        self.set_entry(self.history.following())

    def set_entry(self, text: str) -> None:
        """Replace the content of the entry field."""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)

    def close(self) -> None:
        """Close the window."""
        self.root.destroy()

    def run(self) -> None:
        """Start the event loop."""
        self.root.mainloop()
