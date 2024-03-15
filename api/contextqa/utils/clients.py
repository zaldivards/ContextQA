from typing import Iterable

from langchain.vectorstores.chroma import Chroma
from pinecone import Index

from contextqa import settings


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
                source = f"{settings.media_home}/{source}"
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


class ChromaClient(StoreClient):
    """Chroma client"""

    def __init__(self, client: Chroma):
        super().__init__()
        self._client = client

    def delete(self, ids: list[str]):
        self._client.delete(ids)

    def get(self, source: str) -> Iterable[str]:
        return self._client.get(where={"source": source})["ids"]


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
            # OpenAI's embeddings dimension. This needs to change if support for huggingface encoders is added
            vector=[0] * 1536,
        )

        return map(lambda item: item["id"], data["matches"])
