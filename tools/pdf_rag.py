"""PDF text extraction and TF-IDF retrieval for RAG."""

from __future__ import annotations

import re
from io import BytesIO
from typing import Any

from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class PDFRAGStore:
    """In-memory RAG index built from one or more PDF manuals."""

    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 120

    def __init__(self) -> None:
        self.documents: list[dict[str, Any]] = []
        self.chunks: list[str] = []
        self.chunk_meta: list[dict[str, str]] = []
        self._vectorizer: TfidfVectorizer | None = None
        self._matrix = None

    def add_pdf(self, file_bytes: bytes, filename: str) -> dict[str, Any]:
        """Extract text from a PDF and append chunks to the index."""
        reader = PdfReader(BytesIO(file_bytes))
        pages_text: list[str] = []

        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages_text.append(f"[Page {idx + 1}]\n{text.strip()}")

        full_text = "\n\n".join(pages_text)
        doc_id = filename
        self.documents.append(
            {"filename": filename, "pages": len(reader.pages), "char_count": len(full_text)}
        )

        for chunk in self._split_text(full_text):
            self.chunks.append(chunk)
            self.chunk_meta.append({"filename": filename, "doc_id": doc_id})

        self._rebuild_index()
        return self.documents[-1]

    def _split_text(self, text: str) -> list[str]:
        """Split text into overlapping chunks for retrieval."""
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) <= self.CHUNK_SIZE:
            return [text] if text else []

        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = start + self.CHUNK_SIZE
            chunks.append(text[start:end])
            if end >= len(text):
                break
            start = end - self.CHUNK_OVERLAP
        return chunks

    def _rebuild_index(self) -> None:
        if not self.chunks:
            self._vectorizer = None
            self._matrix = None
            return
        self._vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        self._matrix = self._vectorizer.fit_transform(self.chunks)

    def retrieve(self, query: str, top_k: int = 4) -> list[dict[str, str]]:
        """Return the most relevant text chunks for a query."""
        if not self.chunks or self._vectorizer is None or self._matrix is None:
            return []

        query_vec = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self._matrix).flatten()
        ranked = scores.argsort()[::-1][:top_k]

        results: list[dict[str, str]] = []
        for idx in ranked:
            if scores[idx] < 0.05:
                continue
            meta = self.chunk_meta[idx]
            results.append(
                {
                    "filename": meta["filename"],
                    "score": f"{scores[idx]:.3f}",
                    "text": self.chunks[idx],
                }
            )
        return results

    def build_context(self, query: str, top_k: int = 4) -> str:
        """Format retrieved chunks as context for the LLM or narrative builder."""
        hits = self.retrieve(query, top_k=top_k)
        if not hits:
            return ""

        lines = ["--- Retrieved Manual Excerpts ---"]
        for i, hit in enumerate(hits, 1):
            lines.append(f"\n[Source {i}: {hit['filename']} | relevance={hit['score']}]")
            lines.append(hit["text"])
        lines.append("--- End Manual Excerpts ---")
        return "\n".join(lines)

    @property
    def is_empty(self) -> bool:
        return len(self.chunks) == 0
