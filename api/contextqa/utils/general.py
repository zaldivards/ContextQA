import asyncio
import json
import time
from typing import Coroutine, AsyncGenerator, Any

from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chains import ConversationalRetrievalChain
from langchain.docstore.document import Document

from contextqa.utils.sources import build_sources


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
        **kwargs: Any,
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
        async for token in callback.aiter():
            yield token
            time.sleep(0.05)
    finally:
        callback.done.set()

    await task
    if entrypoint_obj:
        try:
            yield json.dumps({"sources": build_sources(entrypoint_obj.sources)})
        finally:
            pass
