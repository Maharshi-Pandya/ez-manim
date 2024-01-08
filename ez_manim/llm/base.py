from typing import *
from abc import ABC


class BaseLLM(ABC):
    """
    llm classes inherit from this class and follows ChatML format
    """

    def __init__(
            self,
            system_prompt: str = None,
            generation_params: Dict[str, Any] = None
        ) -> None:
        
        # every llm can have a system prompt to steer conversations
        self.system_prompt: str = system_prompt

        # every llm has access to a chat history
        # list of messages of format [{"role": "...", "content": "..."}]
        self.chat_history: List[Dict[str, str]] = None

        # text generation params
        self.generation_params: Dict[str, Any] = generation_params

        # the generation engine
        self._core: Any = None

    def update_system_prompt(self, value: str):
        """
        Updates the llm's system prompt to the passed value
        """
        self.system_prompt = value

    def clear_chat_history(self) -> None:
        """
        Resets the history
        """
        self.chat_history = None

    def update_generation_params(self, value: Dict[str, Any]):
        self.generation_params = value

    def generate(self, messages: List[Dict[str, str]]) -> Any:
        """
        llm classes override this method;
        system prompt should be prepended manually

        Args:
        messages
        """
        pass
