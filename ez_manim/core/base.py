import sys

from rich.console import Console
from rich.markdown import Markdown
from typing import *

from .content import ( 
    WELCOME_MESSAGE, 
    USER_PROMPT, 
    ASSISTANT_SUCCESS_PROMPT, 
    ASSISTANT_ERROR_PROMPT,
    INVALID_RESPONSE
)
from .mwrapper import MWrapper

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

        self.mwrapper = MWrapper(
            code_file_name=self.code_file_name, 
            quality=self.quality
        )

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
                    manim_code, ok = self.ask_llm(ui)
                    if not ok:
                        self._show_success_error_response(INVALID_RESPONSE, error=True, is_md=True)
                    else:
                        # run manim code and save/show
                        response, err = self.mwrapper.render_from_string(manim_code)
                        response = ("[bold green]" if not err else "[bold red]") + response
                        self.console.print(response)
        
        except KeyboardInterrupt:
            self.console.print("\n\nbye bye!\n")
            sys.exit(0)

    def _show_success_error_response(
            self, content: str, error: bool = False, is_md: bool = False
        ):
        assistant_prompt = ASSISTANT_SUCCESS_PROMPT if not error else ASSISTANT_ERROR_PROMPT
        self.console.print(f"\n{assistant_prompt}", end="")

        if is_md:
            self._show_markdown(content)
        else:
            self.console.print(content)

    def ask_llm(self, user_input: str) -> Tuple[str, int]:
        """
        Get a response from the llm
        """

        response: str = ""
        # 0: code, 1: invalid
        ok: int = 0

        messages = self.llm.get_windowed_history()
        messages.append({'role': 'user', 'content': user_input})
        
        response = self.llm.generate(messages)

        if response == "invalid":
            ok = 1
        elif response.startswith("Manim code:"):
            ok = 0
        
        return (response, ok)


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