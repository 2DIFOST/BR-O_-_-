"""Dialog between the user and the shell, shared by GUI and console."""
from typing import Protocol

from .config import Config, debug_lines
from .errors import ScriptError
from .response import Response
from .script import read_script
from .shell import Shell

KIND_INPUT = "input"
KIND_OUTPUT = "output"
KIND_ERROR = "error"
KIND_DEBUG = "debug"


class Output(Protocol):
    """Destination of the dialog: a window or a terminal."""

    def write(self, text: str, kind: str) -> None:
        """Show a line of the given kind (input/output/error/debug)."""


class Session:
    """Runs lines and startup scripts and reports results to Output."""

    def __init__(self, shell: Shell, output: Output) -> None:
        """Create a session of ``shell`` writing to ``output``."""
        self.shell = shell
        self.output = output
        self.finished = False
        self.startup_ok = True

    def show_response(self, response: Response) -> None:
        """Print all messages of a command."""
        for message in response.messages:
            kind = KIND_ERROR if message.is_error else KIND_OUTPUT
            self.output.write(message.text, kind)

    def execute_line(self, line: str) -> Response:
        """Execute a line typed by the user and show the result."""
        response = self.shell.execute(line)
        self.show_response(response)
        if response.should_exit:
            self.finished = True
        return response

    def run_line(self, line: str) -> Response:
        """Echo a line as if it was typed, then execute it."""
        self.output.write(self.shell.prompt() + line, KIND_INPUT)
        return self.execute_line(line)

    def run_script(self, path: str) -> bool:
        """Run a script imitating a dialog; stop at the first error.

        Returns True if the whole script was executed successfully.
        """
        try:
            lines = read_script(path)
        except ScriptError as error:
            self.output.write(f"script error: {error}", KIND_ERROR)
            return False
        for number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            response = self.run_line(line)
            if not response.ok:
                self.report_script_failure(path, number, response)
                return False
            if self.finished:
                break
        return True

    def report_script_failure(
        self, path: str, number: int, response: Response
    ) -> None:
        """Tell the user where the startup script has stopped."""
        self.output.write(
            f"script error: {path}: line {number} failed "
            f"with status {response.status}, script stopped",
            KIND_ERROR,
        )

    def startup(self, config: Config) -> None:
        """Print the debug output and run the startup script."""
        for line in debug_lines(config):
            self.output.write(line, KIND_DEBUG)
        if config.script_path is not None:
            self.startup_ok = self.run_script(config.script_path)
