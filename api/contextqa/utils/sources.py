import base64
import hashlib
from pathlib import Path

import uuid

import fitz
from langchain.docstore.document import Document
from sqlalchemy.orm import Session


from contextqa import settings
from contextqa.models.schemas import Source, SourceFormat
from contextqa.models.orm import Source as SourceORM
from contextqa.utils.exceptions import DuplicatedSourceError


def _get_digest(content: bytes) -> str:
    """Get the digest of the given data source

    Parameters
    ----------
    content : bytes
        the data source content

    Returns
    -------
    str
        hexadecimal representation of the digest
    """
    hasher = hashlib.sha256()
    # Define the chunk size
    chunk_size = 4096
    # Process the file bytes in chunks
    for idx in range(0, len(content), chunk_size):
        # Get the current chunk
        chunk = content[idx : idx + chunk_size]
        # Update the hash object with the current chunk
        hasher.update(chunk)
    # Get the hexadecimal representation of the digest
    digest = hasher.hexdigest()
    return digest


def check_digest(name: str, content: bytes, session: Session):
    """Check if the data source already exists, if so it checks the digest and compares
    it against the existing one.

    Parameters
    ----------
    name : str
        data source name
    content : bytes
        data source content
    session : Session
        connection to the db

    Raises
    ------
    DuplicatedSourceError
        If the data source already exists and its content has not changed
    """
    digest = _get_digest(content)
    source = session.query(SourceORM).filter_by(name=name).first()
    if source:
        if source.digest == digest:
            raise DuplicatedSourceError(f"Digest of {name} has not changed")
        source.digest = digest
    else:
        new_source = SourceORM(name=name, digest=digest)
        session.add(new_source)
    session.commit()


def get_not_seen_chunks(chunks: list[Document], extension: str) -> tuple[list[Document], list[str]]:
    """Search for new chunks that do not exist in ChromaDB

    Parameters
    ----------
    chunks : list[Document]
        the source chunks
    extension : str
        file extension

    Returns
    -------
    tuple[list[Document], list[str]]
        document chunks that do not exist in ChromaDB and their corresponding IDs
    """
    unique_chunks = []
    # generate UUIDs based on the chunk content. Note that if the same chunk(same file content) is ingested again,
    # it won't be added by chromadb thanks to the unique UUID
    ids = [str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk.page_content)) for chunk in chunks]
    unique_ids = set()
    for idx, (chunk, id_) in enumerate(zip(chunks, ids), start=1):
        chunk: Document = chunk
        if id_ not in unique_ids:
            if len(chunk.page_content) > 2:
                if extension != SourceFormat.PDF:
                    chunk.metadata.update(idx=idx)
                unique_chunks.append(chunk)
                unique_ids.add(id_)
    return unique_chunks, list(unique_ids)


def build_sources(sources: list[Document]) -> list[Source]:
    """Analyze each source and transform them into a format the client can render

    Parameters
    ----------
    sources : list[Document]
        relevant sources related to the user's query/question

    Returns
    -------
    list[Source]
        sources transformed into a proper format depending the file type
    """
    result = []
    processed_sources = set()

    for source in sources:
        name = source.metadata.pop("source")
        source_name = name.split(settings.tmp_separator)[-1]
        extension = name.split(".")[-1]

        match extension:
            case SourceFormat.PDF:
                page_number = source.metadata.get("page")
                path = Path(name)
                title = f"{path.name} - Page {page_number}"
                if title not in processed_sources:
                    pdf = fitz.open(str(path))
                    page = pdf[page_number]
                    img_bytes = page.get_pixmap().tobytes()
                    base64_img = base64.b64encode(img_bytes).decode().replace('"', '\\"')
                    format_ = SourceFormat.PDF
                    content = base64_img
            case SourceFormat.TXT:
                idx = source.metadata.get("idx")
                title = f"{source_name} - Segment {idx}"
                if title not in processed_sources:
                    format_ = SourceFormat.TXT
                    content = source.page_content
            case SourceFormat.CSV:
                row = source.metadata.get("row")
                title = f"{source_name} - Row {row}"
                format_ = SourceFormat.CSV
                if title not in processed_sources:
                    data = {}
                    for cell in source.page_content.split("\n"):
                        key, value = cell.split(":", 1)
                        data[key] = value.strip()
                    content = [data]

        if title not in processed_sources:
            source_data = Source(title=title, format=format_, content=content)
            result.append(source_data.model_dump())
            processed_sources.add(title)

    return result
