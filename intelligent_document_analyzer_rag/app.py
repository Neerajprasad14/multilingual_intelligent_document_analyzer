import streamlit as st
from pathlib import Path
from app.ingest import process_document
from app.rag import RAGAnalyzer

st.set_page_config(page_title="Intelligent Document Analyzer", page_icon="📄", layout="wide")

st.title("📄 Intelligent Document Analyzer")
st.caption("RAG-powered document summarization, detailed analysis, advantages, disadvantages and action points")

with st.sidebar:
    st.header("⚙️ Settings")
    ollama_model = st.text_input("Ollama model", "llama3.2:3b")
    top_k = st.slider("Retrieved chunks", 2, 10, 5)
    chunk_size = st.slider("Chunk size", 400, 1500, 900, 100)
    overlap = st.slider("Chunk overlap", 50, 300, 150, 25)

uploaded = st.file_uploader(
    "Upload a PDF, DOCX or TXT document",
    type=["pdf", "docx", "txt"]
)

if uploaded:
    if "analyzer" not in st.session_state:
        st.session_state.analyzer = None
    if "doc_id" not in st.session_state:
        st.session_state.doc_id = None

    data_dir = Path("data/uploads")
    data_dir.mkdir(parents=True, exist_ok=True)
    file_path = data_dir / uploaded.name
    file_path.write_bytes(uploaded.getbuffer())

    if st.button("🚀 Analyze Document", type="primary"):
        with st.spinner("Reading, chunking and indexing the document..."):
            doc_id, chunks = process_document(
                str(file_path),
                chunk_size=chunk_size,
                overlap=overlap
            )
            st.session_state.analyzer = RAGAnalyzer(
                doc_id=doc_id,
                chunks=chunks,
                model=ollama_model,
                top_k=top_k
            )
            st.session_state.doc_id = doc_id

        st.success(f"Indexed {len(chunks)} document chunks.")

if st.session_state.get("analyzer"):
    analyzer = st.session_state.analyzer

    tabs = st.tabs([
        "📝 Summary",
        "🔎 Detailed Points",
        "✅ Advantages",
        "⚠️ Disadvantages",
        "🎯 Action Points",
        "💬 Ask Document"
    ])

    with tabs[0]:
        if st.button("Generate Summary"):
            with st.spinner("Generating document summary..."):
                st.markdown(analyzer.summary())

    with tabs[1]:
        if st.button("Analyze Key Points"):
            with st.spinner("Analyzing important points..."):
                st.markdown(analyzer.analyze_key_points())

    with tabs[2]:
        if st.button("Find Advantages"):
            with st.spinner("Finding evidence-based advantages..."):
                st.markdown(analyzer.analyze_advantages())

    with tabs[3]:
        if st.button("Find Disadvantages / Risks"):
            with st.spinner("Finding disadvantages and risks..."):
                st.markdown(analyzer.analyze_disadvantages())

    with tabs[4]:
        if st.button("Generate Action Points"):
            with st.spinner("Generating recommended actions..."):
                st.markdown(analyzer.action_points())

    with tabs[5]:
        question = st.text_input("Ask a question about the uploaded document")
        if st.button("Ask"):
            if question.strip():
                with st.spinner("Searching the document and generating an answer..."):
                    answer, sources = analyzer.ask(question)
                st.markdown(answer)
                if sources:
                    st.divider()
                    st.caption("Sources used")
                    for source in sources:
                        st.write(source)
else:
    st.info("Upload a document and click Analyze Document to begin.")
