from typing import Any, Dict, List
from openai import OpenAI

from .base import BaseLLM
from .prompts import DEFAULT_SYSTEM_PROMPT


DEFAULT_GENERATION_PARAMS = dict(
    temperature = 0.5,
    top_p = 0.95,
    max_tokens = 1024,
)


class OpenAIManim(BaseLLM):
    def __init__(
            self, 
            system_prompt: str = DEFAULT_SYSTEM_PROMPT, 
            generation_params: Dict[str, Any] = DEFAULT_GENERATION_PARAMS,
            openai_api_key: str = None,
            model: str = "gpt-3.5-turbo"
        ) -> None:

        super().__init__(system_prompt, generation_params)

        self._core: OpenAI = OpenAI(api_key=openai_api_key)
        self._model = model

    def generate(self, messages: List[Dict[str, str]]) -> str:
        completion = self._core.chat.completions.create(
            model=self._model,
            messages=messages,
            **self.generation_params
        )

        return completion.choices[0].message
    