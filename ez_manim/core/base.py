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


def run_with_status(console: Console, func: Callable, *args, **kwargs) -> Any:
    """
    Runs the function with status
    """
    result: Any = None

    with console.status("[bold blue]working on it...") as status:
        result = func(*args, **kwargs)
        console.print("[bold blue]done.")

    return result


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
                    manim_code, ok = run_with_status(
                        self.console, 
                        self.ask_llm, 
                        ui
                    )
                    if not ok:
                        self._show_success_error_response(INVALID_RESPONSE, error=True, is_md=True)
                    else:
                        # run manim code and save/show
                        self._show_success_error_response(manim_code, error=False, is_md=True, end="\n")
                        sind, eind = manim_code.find("```python"), manim_code.rfind("```")
                        mcode = manim_code[sind + len("```python"): eind]
                        
                        response, err = run_with_status(
                            self.console, 
                            self.mwrapper.render_from_string, 
                            mcode
                        )
                        response = ("[bold green]" if not err else "[bold red]") + response
                        self.console.print(response)
        
        except KeyboardInterrupt:
            self.console.print("\n\nbye bye!\n")
            sys.exit(0)

    def _show_success_error_response(
            self, content: str, error: bool = False, is_md: bool = False, end=""
        ):
        assistant_prompt = ASSISTANT_SUCCESS_PROMPT if not error else ASSISTANT_ERROR_PROMPT
        self.console.print(f"\n{assistant_prompt}", end=end)

        if is_md:
            self._show_markdown(content)
        else:
            self.console.print(content)

    def ask_llm(self, user_input: str) -> Tuple[str, bool]:
        """
        Get a response from the llm
        """

        response: str = ""
        # 0: invalid, 1: code
        ok: int = False

        messages = self.llm.get_windowed_history()
        messages.append({'role': 'user', 'content': user_input})

        # add to history
        self.llm.add_to_history("user", user_input)
        
        response = self.llm.generate(messages)

        if response == "-1":
            ok = False
        elif response.startswith("Manim code:"):
            ok = True
        
        self.llm.add_to_history("assistant", response)
        _response = response.replace("Manim code:", "").strip() if ok else response

        return (_response, ok)


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