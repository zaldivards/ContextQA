import asyncio
import json
from typing import Coroutine, AsyncGenerator, Any, Dict, Tuple, Type, Sequence

import google.generativeai as genai
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chains import ConversationalRetrievalChain
from langchain.docstore.document import Document
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage, AIMessageChunk
from langchain_core.runnables.utils import AddableDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import _convert_to_parts
from langchain_google_genai._function_utils import convert_to_genai_function_declarations

from contextqa.utils.sources import build_sources


class NoneType:
    """None sentinel type"""


def _ensure_final_answer(chunk: AddableDict) -> str | None:
    return chunk.get("output")


async def consumer_producer(response_stream: AsyncGenerator[AIMessageChunk, None]) -> AsyncGenerator[str, None]:
    """Consumes an asynchronous stream and streams async messages

    Parameters
    ----------
    response_stream : AsyncGenerator[AIMessageChunk, None]

    Returns
    -------
    AsyncGenerator[str, None]
        Final stream

    Yields
    ------
    str
    """
    async for chunk in response_stream:
        if isinstance(chunk, AddableDict):
            # this type is streamed by agents, as normally it streams all the intermediate steps
            content = _ensure_final_answer(chunk)
            if not content:
                continue
        else:
            content = chunk.content
        if len(content) > 10:
            for word in content.split():
                await asyncio.sleep(0.05)
                yield f"{word} "
        else:
            yield content


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


class CustomQAChain(ConversationalRetrievalChain):
    """ConversationalRetrievalChain with custom `arun` method.

    This was added to support returning the relevant data sources"""

    sources: list[Document] | None = None

    async def arun(
        self,
        *args: Any,
        callbacks=None,
        tags=None,
        metadata=None,
        **_: Any,
    ) -> Any:
        result = await self.acall(args[0], callbacks=callbacks, tags=tags, metadata=metadata)
        self.sources = result.pop(self.output_keys[1])
        return result[self.output_keys[0]]


async def stream(
    llm_entrypoint: Coroutine, callback: AsyncIteratorCallbackHandler, entrypoint_obj: CustomQAChain | None = None
) -> AsyncGenerator:
    """Initialize a streaming response

    Parameters
    ----------
    llm_entrypoint : Coroutine
        the async object that will start the llm process
    callback : AsyncIteratorCallbackHandler
        callback that will iter through the async queue, starting the streaming
    entrypoint_obj : CustomQAChain | None, optional
        if provided it will contain the relevant sources used to generate a RAG-based answer, by default None

    Returns
    -------
    AsyncGenerator

    Yields
    ------
    str
        response tokens
    """
    task = asyncio.create_task(llm_entrypoint)

    try:
        temp = ""
        async for token in callback.aiter():
            # the logic below is to ensure some regex entities are streamed with all their characters in one token
            # this to properly render them
            if not temp:
                if token.endswith("\\"):
                    temp = token
                else:
                    yield token
            else:
                yield temp + token
                temp = ""
    finally:
        callback.done.set()

    await task
    if entrypoint_obj:
        try:
            # sources are streamed in chunks because when a source contains a base64 image, some of the
            # content get lost somehow. Hence we need to divide it into chunks
            data = json.dumps(build_sources(entrypoint_obj.sources))
            size = 10_000
            for chunk_start in range(0, len(data), size):
                chunk = data[chunk_start : chunk_start + size]
                yield "<source>" + chunk
        finally:
            pass
