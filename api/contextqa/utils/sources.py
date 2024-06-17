import base64
import hashlib
import uuid
from pathlib import Path

import fitz
from fastapi import HTTPException, status
from langchain.docstore.document import Document
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from contextqa import settings, logger
from contextqa.models.orm import Source as SourceORM, VectorStore, Index
from contextqa.models.schemas import SourceSegment, SourceFormat
from contextqa.utils.exceptions import DuplicatedSourceError
from contextqa.utils.settings import get_or_set


def _get_or_create_index(session: Session) -> Index:
    settings_ = get_or_set(kind="store")
    # collection for chroma and index for pinecone
    if settings_.store == "chroma":
        current_index = f'{settings_.store_params.get("home")}/{settings_.store_params.get("collection")}'
    else:
        current_index = f'{settings_.store_params.get("environment")}/{settings_.store_params.get("index")}'
    index = session.query(Index).filter_by(name=current_index).first()
    if index:
        return index
    store = session.query(VectorStore).filter_by(name=settings_.store).first()
    new_index = Index(name=current_index, store_id=store.id)
    try:
        session.add(new_index)
        session.commit()
        session.refresh(new_index)
    except IntegrityError as ex:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY, detail="New index could not be created"
        ) from ex
    logger.info("New index created: %s", current_index)
    return new_index


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
        index = _get_or_create_index(session)
        new_source = SourceORM(name=name, digest=digest, index_id=index.id)
        session.add(new_source)


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
    media_dir = get_or_set("extra").media_dir
    unique_ids = set()
    for idx, (chunk, id_) in enumerate(zip(chunks, ids), start=1):
        chunk: Document = chunk
        if extension == SourceFormat.PDF:
            chunk.metadata.update(source=chunk.metadata["source"].replace(media_dir, "{}"))
        else:
            # removes random prefix generated when creating the temporary file. This ensures easier queries against
            # vector databases, using metadata lookups
            chunk.metadata.update(source=chunk.metadata["source"].split(settings.tmp_separator)[-1])
        if id_ not in unique_ids:
            if len(chunk.page_content) > 2:
                if extension != SourceFormat.PDF:
                    chunk.metadata.update(idx=idx)
                unique_chunks.append(chunk)
                unique_ids.add(id_)
    return unique_chunks, list(unique_ids)


def _get_base64_image(path_: Path, page_number: int) -> str:
    pdf = fitz.open(str(path_))
    page = pdf[page_number]
    img_bytes = page.get_pixmap().tobytes()
    base64_img = base64.b64encode(img_bytes).decode().replace('"', '\\"')
    return base64_img


def _csv_repr(cell_content: str) -> list[dict]:
    data = {}
    for cell in cell_content.split("\n"):
        key, value = cell.split(":", 1)
        data[key] = value.strip()
    return [data]


def build_sources(sources: list[Document]) -> list[SourceSegment]:
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
    media_dir = get_or_set("extra").media_dir
    for source in sources:
        name: str = source.metadata.pop("source")
        source_name = name.split(settings.tmp_separator)[-1]
        extension = "." + name.split(".")[-1]

        match extension:
            case SourceFormat.PDF:
                page_number = int(source.metadata.get("page"))
                path = Path(name.format(media_dir))
                title = f"{path.name} - Page {page_number}"
                if title not in processed_sources:
                    format_ = SourceFormat.PDF
                    content = _get_base64_image(path, page_number)
            case SourceFormat.TXT:
                idx = source.metadata.get("idx")
                title = f"{source_name} - Segment {int(idx)}"
                if title not in processed_sources:
                    format_ = SourceFormat.TXT
                    content = source.page_content
            case SourceFormat.CSV:
                title = f"{source_name} - Row {int(source.metadata.get('row'))}"
                format_ = SourceFormat.CSV
                if title not in processed_sources:
                    content = _csv_repr(source.page_content)

        if title not in processed_sources:
            source_data = SourceSegment(title=title, format=format_, content=content)
            result.append(source_data.model_dump())
            processed_sources.add(title)

    return result
