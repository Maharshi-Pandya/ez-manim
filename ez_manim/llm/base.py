from typing import *
from abc import ABC

from ..utils import num_tokens_from_messages


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
        self.chat_history: List[Dict[str, str]] = [
            {"role": "system", "content": self.system_prompt}
        ]

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
        self.chat_history = [
            {"role": "system", "content": self.system_prompt}
        ]

    def add_to_history(self, role: str, content: str):
        """
        Add the message to chat history
        """
        self.chat_history.append(dict(role=role, content=content))

    def update_generation_params(self, value: Dict[str, Any]):
        self.generation_params = value

    def get_windowed_history(self, num_tokens: int = 1500) -> List[Dict[str, str]]:
        """
        returns a windowed chat history with a limit of `num_tokens` tokens
        """
        selected_messages: List[Dict[str, str]] = []
        total_length = 0

        # Iterate through messages in reverse order
        for message in reversed(self.chat_history):
            role = message['role']
            content = message['content']

            if role == "system":
                continue

            # Calculate the token length of the content
            content_length = num_tokens_from_messages([message])

            # Check if adding this message exceeds the maximum length
            if total_length + content_length <= num_tokens:
                # Add the message to the selected list
                selected_messages.append({'role': role, 'content': content})

                # Update the total length
                total_length += content_length


        selected_messages.append({'role': 'system', 'content': self.system_prompt})
        selected_messages.reverse()

        return selected_messages
            

    def generate(self, messages: List[Dict[str, str]]) -> Any:
        """
        llm classes override this method;
        system prompt should be prepended manually

        Args:
        messages
        """
        pass
