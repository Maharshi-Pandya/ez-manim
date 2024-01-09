import sys

from rich.console import Console
from rich.markdown import Markdown
from typing import *

from .content import ( 
    WELCOME_MESSAGE, 
    USER_PROMPT, 
    ASSISTANT_SUCCESS_PROMPT, 
    ASSISTANT_ERROR_PROMPT 
)

from ..llm import BaseLLM, OpenAIManim


class Core:
    """
    Responsible for executing the manim code from LLM
    """
    def __init__(
        self,
        code_file_name: str = "trialCode",
        console: Console = None,
        llm: BaseLLM = None,
        quality: str = "h"
    ) -> None:
        self.code_file_name = code_file_name
        self.console = console or Console()
        self.llm = llm or OpenAIManim()
        self.quality = quality

    def run(self):
        self._show_markdown(WELCOME_MESSAGE, extra_lines=True)
        self._main_loop()
    
    def _main_loop(self):
        try:
            while True:
                user_input = ""
                multiline_mode = False

                while True:
                    if not multiline_mode:
                        prompt = USER_PROMPT
                        self.console.print()
                    else:
                        prompt = "... "

                    self.console.print(prompt, end="")
                    line = input()

                    if not multiline_mode:
                        if line.startswith('"""'):
                            multiline_mode = True
                            user_input += line[3:] + "\n"  # Remove the first triple quotes
                        elif line:  # Capture single-line strings
                            break  # Exit inner loop after capturing single-line string
                    else:
                        if line.endswith('"""'):
                            multiline_mode = False
                            user_input += line[:-3]  # Remove the last triple quotes
                            break  # Exit inner loop after capturing multiline string
                        else:
                            user_input += line + "\n"

                    if not multiline_mode and not line:  # Empty line outside multiline mode
                        break

                ui = user_input if user_input else line
                ui = ui.strip()
                # reset string buffer
                user_input = ""

                # TODO: got the user input, now process 
                if ui:
                    self.console.print(f"\n{ASSISTANT_SUCCESS_PROMPT}", end="")
                    self.console.print(ui)
        
        except KeyboardInterrupt:
            self.console.print("\n\nbye bye!\n")
            sys.exit(0)

    def ask_llm(self, user_input: str) -> str:
        """
        Get a response from the llm
        """

        response: str = ""
        # 0: code, 1: invalid
        response_type: int = 0

    def _str2md(self, content: str) -> Markdown:
        _md = Markdown(content)
        return _md

    def _show_markdown(self, content: str, extra_lines=False):
        if extra_lines:
            self.console.print()

        _md = self._str2md(content)
        self.console.print(_md)

        if extra_lines:
            self.console.print()