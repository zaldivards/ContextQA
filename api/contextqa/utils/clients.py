from typing import Iterable

from langchain_community.vectorstores import Chroma
from pinecone import Index

from contextqa import logger
from contextqa.utils.settings import get_or_set


class StoreClient:
    """Generic store client

    Children classes must override the `delete` and `get` methods
    """

    def delete(self, ids: list[str]):
        """Remove chunks from the store using the given IDs

        Parameters
        ----------
        ids : list[str]
            Chunks IDs
        """
        raise NotImplementedError

    def get_ids(self, sources: list[str]) -> list[str]:
        """Get the chunk IDs related to the given sources

        Parameters
        ----------
        sources : list[str]
            Sources names

        Returns
        -------
        list[str]
            Chunk IDs
        """
        chunks_to_remove = []
        for source in sources:
            if source.endswith(".pdf"):
                source = f"{get_or_set('extra').media_dir}/{source}"
            chunks = self.get(source)
            chunks_to_remove.extend(chunks)

        return chunks_to_remove

    def get(self, source: str) -> Iterable[str]:
        """Get the chunks IDs related to the given source

        Parameters
        ----------
        source : str
            Source name

        Returns
        -------
        Iterable[str]
            Chunks IDs
        """
        raise NotImplementedError

    def is_alive(self) -> bool:
        """Check if the vector DB is up and running

        Returns
        -------
        bool
        """
        raise NotImplementedError


class ChromaClient(StoreClient):
    """Chroma client"""

    def __init__(self, client: Chroma):
        super().__init__()
        self._client = client

    def delete(self, ids: list[str]):
        self._client.delete(ids)

    def get(self, source: str) -> Iterable[str]:
        return self._client.get(where={"source": source})["ids"]

    def is_alive(self) -> bool:
        try:
            self._client.get(limit=1)
            return True
        except Exception as ex:
            logger.error("vectorDB client is not alive: %s", ex)
            return False


class PineconeClient(StoreClient):
    """Pinecone client"""

    def __init__(self, client: Index):
        super().__init__()
        self._client = client

    def delete(self, ids: list[str]):
        self._client.delete(ids=ids)

    def get(self, source: str) -> Iterable[str]:
        data = self._client.query(
            top_k=10_000,
            filter={"source": {"$eq": source}},
            include_metadata=False,
            include_values=False,
            vector=[0] * 768,
        )

        return map(lambda item: item["id"], data["matches"])

    def is_alive(self) -> bool:
        try:
            self._client.describe_index_stats()
            return True
        except Exception as ex:
            logger.error("vectorDB client is not alive: %s", ex)
            return False
