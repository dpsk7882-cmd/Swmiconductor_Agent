"""📄 PDF Knowledge Base page."""

from __future__ import annotations

import streamlit as st

from utils.components import empty_state, platform_header
from utils.data_sync import sync_registry
from utils.navigation import PAGE_TITLES
from utils.session import get_engine
from utils.uploads import get_uploads


def render_pdf_kb_page() -> None:
    title, subtitle = PAGE_TITLES["pdf_kb"]
    platform_header(title, subtitle)

    sync_registry()
    engine = get_engine()
    pdfs = [u for u in get_uploads() if u["file_kind"] == "pdf"]

    if not pdfs:
        empty_state("📄", "No Manuals Loaded", "Upload PDF SOPs, recipes, or equipment manuals in the sidebar.")
        return

    st.markdown("#### 📚 Indexed Documents")
    for pdf in pdfs:
        with st.container(border=True):
            st.markdown(f"**{pdf['icon']} {pdf['filename']}**")
            st.caption(f"{pdf['label']} · {pdf['size_bytes'] / 1024:.1f} KB")

    st.divider()
    st.markdown("#### 🔍 Search Knowledge Base")
    query = st.text_input("Search manuals", placeholder="e.g. chamber temperature spec, PM procedure...")
    if query:
        hits = engine.query_manual(query)
        if not hits:
            st.info("No relevant excerpts found. Try different keywords.")
        for i, hit in enumerate(hits, 1):
            with st.expander(f"📄 {hit['filename']} — relevance {hit['score']}"):
                st.markdown(hit["text"][:2000])
