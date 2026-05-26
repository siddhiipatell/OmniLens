"""
OmniLens — Streamlit Frontend
"""
import io
import requests
import streamlit as st
from audiorecorder import audiorecorder

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="OmniLens", page_icon="🔍", layout="wide")

# ── Sidebar ──────────────────────────────────────────────────────────
st.sidebar.title("🔍 OmniLens")
st.sidebar.caption("Multi-modal RAG — PDFs, images, audio")

collection = st.sidebar.text_input("Collection", value="omnilens_default")

st.sidebar.divider()
st.sidebar.subheader("Ingest files")

uploaded = st.sidebar.file_uploader(
    "Upload PDF, image, or audio",
    type=["pdf", "png", "jpg", "jpeg", "webp", "mp3", "wav", "m4a"],
    accept_multiple_files=True,
)

if st.sidebar.button("Ingest", disabled=not uploaded):
    for f in uploaded:
        with st.sidebar.status(f"Indexing {f.name}…"):
            r = requests.post(
                f"{API_BASE}/ingest/",
                files={"file": (f.name, f.read(), f.type)},
                data={"collection": collection},
            )
            if r.ok:
                d = r.json()
                st.sidebar.success(f"{d['modality'].upper()} — {d['chunks_indexed']} chunks")
            else:
                st.sidebar.error(f"Failed: {r.text}")

# ── Main area ─────────────────────────────────────────────────────────
st.title("Ask OmniLens")
st.caption("Ask anything about your ingested documents, images, and recordings.")

tab_text, tab_voice = st.tabs(["Text query", "Voice query"])

# Text query tab
with tab_text:
    query = st.text_area("Your question", placeholder="What does the revenue chart show?", height=80)
    if st.button("Ask", type="primary", disabled=not query):
        with st.spinner("Retrieving and generating answer…"):
            r = requests.post(
                f"{API_BASE}/query/",
                json={"query": query, "collection": collection, "top_k": 5},
            )
        if r.ok:
            _render_answer(r.json())
        else:
            st.error(f"Query failed: {r.text}")

# Voice query tab
with tab_voice:
    st.caption("Record your question — it will be transcribed by Whisper then answered.")
    audio = audiorecorder("Start recording", "Stop recording")

    if len(audio) > 0:
        st.audio(audio.export().read(), format="audio/wav")
        if st.button("Submit voice query", type="primary"):
            buf = io.BytesIO()
            audio.export(buf, format="wav")
            buf.seek(0)
            with st.spinner("Transcribing + answering…"):
                r = requests.post(
                    f"{API_BASE}/query/voice",
                    files={"audio": ("query.wav", buf, "audio/wav")},
                    data={"collection": collection},
                )
            if r.ok:
                data = r.json()
                st.info(f"Transcribed query: *{data.get('transcribed_query', '')}*")
                _render_answer(data)
            else:
                st.error(f"Query failed: {r.text}")


def _render_answer(data: dict):
    st.subheader("Answer")
    st.markdown(data["answer"])

    st.divider()
    st.subheader("Sources used")
    for i, src in enumerate(data.get("sources", []), start=1):
        modality = src.get("modality", "")
        icon = {"pdf": "📄", "image": "🖼️", "audio": "🎙️"}.get(modality, "📎")
        label = f"{icon} Source {i} — {src.get('file', '')}"

        if modality == "pdf":
            label += f" (page {src.get('page', '?')})"
        elif modality == "audio":
            label += f" @ {src.get('timestamp', '?')}"

        with st.expander(label):
            st.text(src.get("chunk", ""))
            if modality == "image" and src.get("img_path"):
                st.caption(f"Image path: {src['img_path']}")
