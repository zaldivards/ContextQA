import base64
from pathlib import Path

import uuid

import fitz
from langchain.docstore.document import Document


from contextqa import settings
from contextqa.parsers.models import Source, SourceFormat


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

    seen_ids = set()
    for idx, (chunk, id_) in enumerate(zip(chunks, ids), start=1):
        chunk: Document = chunk
        if id_ not in seen_ids and len(chunk.page_content) > 2:
            if extension != SourceFormat.PDF:
                chunk.metadata.update(idx=idx)
            unique_chunks.append(chunk)
        else:
            ids.pop(idx)
    return unique_chunks, ids


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
    for source in sources:
        name = source.metadata.pop("source")
        extension = name.split(".")[-1]
        match extension:
            case SourceFormat.PDF:
                page_number = source.metadata.get("page")
                path = Path(name)
                pdf = fitz.open(str(path))
                page = pdf[page_number]
                img_bytes = page.get_pixmap().tobytes()
                base64_img = base64.b64encode(img_bytes)
                source = Source(title=f"{path.name} - Page {page_number}", format=SourceFormat.PDF, content=base64_img)
                result.append(source)
            case SourceFormat.TXT:
                idx = source.metadata.get("idx")
                source_name = name.split(settings.tmp_separator)[-1]
                source = Source(
                    title=f"{source_name} - Segment {idx}", format=SourceFormat.TXT, content=source.page_content
                )
                result.append(source)
    return result
