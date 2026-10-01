from io import BytesIO
from pathlib import PurePath

from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".pdf", ".txt"}


class UnsupportedFileError(ValueError):
    pass


def extract_text(filename: str, data: bytes) -> str:

    suffix = PurePath(filename).suffix.lower()

    if suffix == ".pdf":
        reader = PdfReader(BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if suffix == ".txt":
        return data.decode("utf-8", errors="ignore")

    raise UnsupportedFileError("Only .pdf and .txt files are supported")
