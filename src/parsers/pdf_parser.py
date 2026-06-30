from io import BytesIO

from pypdf import PdfReader


class PDFParser:
    """Extract text from uploaded PDF files."""

    def __init__(self, max_pages: int = 50):
        self.max_pages = max_pages

    def parse(self, file_bytes: bytes, filename: str = "document.pdf") -> dict:
        reader = PdfReader(BytesIO(file_bytes))
        total_pages = len(reader.pages)
        pages_to_read = min(total_pages, self.max_pages)

        chunks: list[str] = []
        for index in range(pages_to_read):
            text = reader.pages[index].extract_text() or ""
            if text.strip():
                chunks.append(f"[Page {index + 1}]\n{text.strip()}")

        full_text = "\n\n".join(chunks)
        truncated = total_pages > self.max_pages

        return {
            "filename": filename,
            "total_pages": total_pages,
            "pages_extracted": pages_to_read,
            "truncated": truncated,
            "text": full_text,
            "char_count": len(full_text),
        }

    @staticmethod
    def to_context_block(parsed: dict) -> str:
        if not parsed.get("text"):
            return f"PDF '{parsed['filename']}' contains no extractable text."

        note = ""
        if parsed.get("truncated"):
            note = (
                f" (Note: only first {parsed['pages_extracted']} of "
                f"{parsed['total_pages']} pages were loaded.)"
            )

        return (
            f"--- PDF Document: {parsed['filename']}{note} ---\n"
            f"{parsed['text']}\n"
            f"--- End PDF ---"
        )
