from typing import Any, Dict, List
from .base import BaseLLM

from openai import OpenAI


DEFAULT_GENERATION_PARAMS = dict(
    temperature = 0.5,
    top_p = 0.95,
    max_tokens = 1024,
)


class OpenAIManim(BaseLLM):
    def __init__(
            self, 
            system_prompt: str = None, 
            generation_params: Dict[str, Any] = DEFAULT_GENERATION_PARAMS,
            openai_api_key: str = None,
            model: str = "gpt-3.5-turbo"
        ) -> None:

        super().__init__(system_prompt, generation_params)

        self._core: OpenAI = OpenAI(api_key=openai_api_key)
        self._model = model

    def generate(self, messages: List[Dict[str, str]]) -> str:
        _messages = messages.insert(0, dict(role="system", content=self.system_prompt))

        completion = self._core.chat.completions.create(
            model=self._model,
            messages=_messages,
            **self.generation_params
        )

        return completion.choices[0].message
    