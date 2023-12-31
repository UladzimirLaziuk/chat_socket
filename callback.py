"""Callback handlers used in the app."""
from typing import Any, Dict, List

from schemas import ChatResponse


class StreamingLLMCallbackHandler:
    """Callback handler for streaming LLM responses."""

    def __init__(self, websocket):
        self.websocket = websocket

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        if token in '<END_OF_TURN>':
            token = ''
        resp = ChatResponse(sender="bot", message=token.replace('<', ''), type="stream")
        await self.websocket.send_json(resp.dict())


class QuestionGenCallbackHandler:
    """Callback handler for question generation."""

    def __init__(self, websocket):
        self.websocket = websocket

    async def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""
        resp = ChatResponse(
            sender="bot", message="Synthesizing question...", type="info"
        )
        await self.websocket.send_json(resp.dict())
