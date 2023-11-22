import base64
from pathlib import Path

import fitz
from langchain.docstore.document import Document


from contextqa import settings
from contextqa.parsers.models import Source, SourceFormat


def build_sources(sources: list[Document]) -> list[Source]:
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
