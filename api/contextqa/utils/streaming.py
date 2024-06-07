import asyncio
import json
from typing import AsyncGenerator, Any, Dict, Tuple, Type, Sequence

import google.generativeai as genai
from langchain_community.docstore.document import Document
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage, AIMessageChunk
from langchain_core.runnables.schema import StreamEvent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import _convert_to_parts
from langchain_google_genai._function_utils import convert_to_genai_function_declarations

from contextqa.utils.sources import build_sources


class NoneType:
    """None sentinel type"""


async def consumer_producer(
    response_stream: AsyncGenerator[StreamEvent, None], is_agent: bool
) -> AsyncGenerator[str, None]:
    """Consumes an asynchronous stream and streams async messages

    Parameters
    ----------
    response_stream : AsyncGenerator[StreamEvent, None]
    is_agent : bool

    Returns
    -------
    AsyncGenerator[str, None]
        Final stream

    Yields
    ------
    str
    """
    iter_content = ""
    final_answer = False
    async for event_chunk in response_stream:
        await asyncio.sleep(0.02)
        if event_chunk["event"] == "on_chat_model_stream":
            if is_agent:
                if content := event_chunk["data"]["chunk"].content:
                    if '"action_input": "' in iter_content:
                        if content not in ('"', "}", "```"):
                            yield content
                    if content in ("Final Answer", "Final", "Answer"):
                        final_answer = True
                    if final_answer:
                        iter_content += content
            else:
                chunk = event_chunk["data"]["chunk"]
                if isinstance(chunk, AIMessageChunk):
                    yield chunk.content


async def consumer_producer_qa(
    response_stream: AsyncGenerator[dict[str, Document] | dict[str, AIMessageChunk], None],
) -> AsyncGenerator[str, None]:
    """Consumes an asynchronous stream and streams async messages. After processing the messages, relevant sources are
    also streamed

    Parameters
    ----------
    response_stream : AsyncGenerator[dict[str, Document] | dict[str, AIMessageChunk], None]

    Returns
    -------
    AsyncGenerator[str, None]
        Final stream

    Yields
    ------
    str
    """
    async for chunk in response_stream:
        if answer := chunk.get("answer"):
            await asyncio.sleep(0.05)
            if isinstance(answer, str):
                yield answer
            else:
                yield answer.content
        elif docs := chunk.get("context"):
            try:
                # sources are streamed in chunks because when a source contains a base64 image, some of the
                # content get lost somehow. Hence we need to divide it into chunks
                data = json.dumps(build_sources(docs))
                size = 10_000
                for chunk_start in range(0, len(data), size):
                    chunk = data[chunk_start : chunk_start + size]
                    await asyncio.sleep(0.05)
                    yield "<source>" + chunk
            finally:
                pass


def _parse_chat_history(input_messages: Sequence[BaseMessage]) -> list:
    messages = []
    parts = []
    previous_type: Type[BaseMessage | NoneType] | tuple[Type[BaseMessage], Type[BaseMessage]] = NoneType
    for i, message in enumerate(input_messages):
        if isinstance(message, AIMessage):
            role = "model"
            local_parts = _convert_to_parts(message.content)
            if isinstance(message, previous_type):
                parts = parts + local_parts
            else:
                if parts:
                    messages.append({"role": "user", "parts": parts})
                parts = local_parts
            previous_type = AIMessage
        elif isinstance(message, (HumanMessage, SystemMessage)):
            role = "user"
            local_parts = _convert_to_parts(message.content)
            if isinstance(message, previous_type):
                parts = parts + local_parts
            else:
                if parts:
                    messages.append({"role": "model", "parts": parts})
                parts = local_parts
            previous_type = (HumanMessage, SystemMessage)
        else:
            raise ValueError(f"Unexpected message with type {type(message)} at the position {i}.")

    messages.append({"role": role, "parts": parts})

    return messages


class ChainCompatibleGoogleGenerativeAI(ChatGoogleGenerativeAI):
    """Enhanced ChatGoogleGenerativeAI"""

    # pylint: disable=W0221
    def _prepare_chat(
        self, messages: list[BaseMessage], stop: list[str] | None = None, **kwargs: Any
    ) -> Tuple[Dict[str, Any], genai.ChatSession, genai.types.ContentDict]:
        client = self.client
        functions = kwargs.pop("functions", None)
        safety_settings = kwargs.pop("safety_settings", self.safety_settings)
        if functions or safety_settings:
            tools = convert_to_genai_function_declarations(functions) if functions else None
            client = genai.GenerativeModel(model_name=self.model, tools=tools, safety_settings=safety_settings)

        params = self._prepare_params(stop, **kwargs)
        # this method was overridden just to call my own implementation of `_parse_chat_history`. The other above and
        # below code is the same as the original implementation
        history = _parse_chat_history(messages)
        message = history.pop()
        chat = client.start_chat(history=history)
        return params, chat, message
