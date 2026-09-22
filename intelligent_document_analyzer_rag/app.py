import os
from pathlib import Path

import streamlit as st

from app.ingest import process_document
from app.rag import RAGAnalyzer
from database import initialize_database, recent_documents, save_analysis, save_document

st.set_page_config(page_title="Aether Document Intelligence", page_icon=":material/auto_awesome:", layout="wide", initial_sidebar_state="expanded")

# The requested dimensional treatment is deliberately limited to durable layout surfaces.
st.html("""
<style>
    .stApp { background: radial-gradient(circle at 78% 8%, #243761 0, transparent 28%), radial-gradient(circle at 12% 32%, #211b48 0, transparent 24%), #0B1020; }
    [data-testid="stVerticalBlockBorderWrapper"] { background: linear-gradient(145deg, rgba(31,42,74,.94), rgba(15,21,42,.96)); box-shadow: 12px 14px 28px rgba(0,0,0,.28), -2px -2px 10px rgba(105,125,182,.08); transition: transform .2s ease, box-shadow .2s ease; }
    [data-testid="stVerticalBlockBorderWrapper"]:hover { transform: translateY(-3px); box-shadow: 16px 19px 34px rgba(0,0,0,.34), -2px -2px 12px rgba(139,92,246,.14); }
    [data-testid="stMetric"] { background: rgba(21,27,49,.72); border: 1px solid #2B3658; border-radius: 14px; padding: 12px 16px; box-shadow: inset 0 1px rgba(255,255,255,.04), 0 10px 20px rgba(0,0,0,.16); }
</style>
""")


def init_state():
    for key, value in {"analyzer": None, "doc_id": None, "filename": None, "chunk_count": 0, "messages": [], "database_ready": None}.items():
        st.session_state.setdefault(key, value)


def persist_output(kind, content):
    try:
        save_analysis(st.session_state.doc_id, kind, content)
    except Exception:
        pass


def run_analysis(label, operation):
    with st.status("Preparing evidence-based analysis...", expanded=True) as status:
        st.write("Retrieving the most relevant document context")
        result = operation()
        status.update(label="Analysis complete", state="complete", expanded=False)
    persist_output(label.lower().replace(" ", "_"), result)
    st.markdown(result)


init_state()
try:
    if st.session_state.database_ready is None:
        initialize_database()
        st.session_state.database_ready = True
except Exception:
    st.session_state.database_ready = False

with st.sidebar:
    st.markdown("## Aether")
    st.caption("DOCUMENT INTELLIGENCE WORKSPACE")
    st.badge("Database connected" if st.session_state.database_ready else "Database unavailable", icon=":material/database:" if st.session_state.database_ready else ":material/cloud_off:", color="green" if st.session_state.database_ready else "orange")
    st.space("medium")
    st.subheader("Analysis settings", icon=":material/tune:")
    ollama_model = st.text_input("Ollama model", value=os.getenv("OLLAMA_MODEL", "llama3.2:3b"))
    top_k = st.slider("Evidence depth", 2, 10, 5)
    with st.expander("Chunking options", icon=":material/data_object:"):
        chunk_size = st.slider("Chunk size", 400, 1500, 900, 100)
        overlap = st.slider("Chunk overlap", 50, 300, 150, 25)
    if st.session_state.database_ready:
        st.space("medium")
        st.subheader("Recent workspace", icon=":material/history:")
        try:
            for record in recent_documents():
                st.caption(f"{record.filename} · {record.chunk_count} chunks")
        except Exception:
            st.caption("Recent documents will appear here.")

st.title("Understand every document with clarity", icon=":material/auto_awesome:")
st.caption("A focused RAG workspace for evidence-led summaries, risk review, and decisions.")

hero_left, hero_right = st.columns([1.65, 1], vertical_alignment="center")
with hero_left:
    with st.container(border=True):
        st.subheader("Start a new analysis", icon=":material/upload_file:")
        uploaded = st.file_uploader("Drop a PDF, DOCX, or TXT document", type=["pdf", "docx", "txt"])
        if uploaded:
            st.caption(f"Ready to index · {uploaded.name} · {uploaded.size / 1024:.1f} KB")
            if st.button("Index document", type="primary", icon=":material/rocket_launch:", width="stretch"):
                try:
                    data_dir = Path("data/uploads")
                    data_dir.mkdir(parents=True, exist_ok=True)
                    file_path = data_dir / uploaded.name
                    file_path.write_bytes(uploaded.getbuffer())
                    with st.status("Building your searchable document workspace...", expanded=True) as status:
                        st.write("Extracting text and structuring content")
                        doc_id, chunks = process_document(str(file_path), chunk_size, overlap)
                        st.write("Creating semantic index")
                        st.session_state.analyzer = RAGAnalyzer(doc_id, chunks, ollama_model, top_k)
                        status.update(label="Document indexed", state="complete", expanded=False)
                    st.session_state.doc_id, st.session_state.filename = doc_id, uploaded.name
                    st.session_state.chunk_count, st.session_state.messages = len(chunks), []
                    if st.session_state.database_ready:
                        save_document(doc_id, uploaded.name, len(chunks))
                    st.toast("Your document is ready for analysis.", icon=":material/check_circle:")
                except Exception as error:
                    st.error(f"Could not index this document: {error}", icon=":material/error:")
with hero_right:
    with st.container(border=True):
        st.subheader("Built for decisive review", icon=":material/diamond:")
        st.markdown("**Evidence first.** Every answer is grounded in the indexed source chunks.")
        st.markdown("**Persistent workspace.** Document metadata and completed analyses are stored in PostgreSQL.")
        st.markdown("**Private by design.** Run the RAG stack with your local Ollama model.")

if st.session_state.analyzer:
    st.space("small")
    metric_a, metric_b, metric_c = st.columns(3)
    metric_a.metric("Active document", st.session_state.filename)
    metric_b.metric("Indexed evidence", f"{st.session_state.chunk_count} chunks")
    metric_c.metric("Retrieval depth", f"Top {top_k}")
    st.header("Analysis studio", icon=":material/insights:")
    summary_tab, points_tab, value_tab, risk_tab, action_tab, chat_tab = st.tabs(["Executive summary", "Key points", "Advantages", "Risks", "Action plan", "Ask the document"])
    analyzer = st.session_state.analyzer
    with summary_tab:
        st.caption("A concise brief for confident, informed decisions.")
        if st.button("Create executive summary", icon=":material/summarize:", key="summary"):
            run_analysis("Summary", analyzer.summary)
    with points_tab:
        st.caption("The commitments, conditions, and implications that matter most.")
        if st.button("Surface key points", icon=":material/manage_search:", key="points"):
            run_analysis("Key points", analyzer.analyze_key_points)
    with value_tab:
        st.caption("Benefits that are directly supported by the source material.")
        if st.button("Find advantages", icon=":material/trending_up:", key="advantages"):
            run_analysis("Advantages", analyzer.analyze_advantages)
    with risk_tab:
        st.caption("Restrictions, costs, and items worth clarifying before you proceed.")
        if st.button("Review risks", icon=":material/gpp_maybe:", key="risks"):
            run_analysis("Risks", analyzer.analyze_disadvantages)
    with action_tab:
        st.caption("Turn the document into a practical next-step checklist.")
        if st.button("Create action plan", icon=":material/task_alt:", key="actions"):
            run_analysis("Action plan", analyzer.action_points)
    with chat_tab:
        st.caption("Ask a precise question; answers cite the source chunks used.")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message.get("sources"):
                    st.caption(" · ".join(message["sources"]))
        if prompt := st.chat_input("Ask anything about this document", submit_mode="disable"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant", avatar=":material/auto_awesome:"):
                with st.status("Finding the strongest evidence...", expanded=False) as status:
                    answer, sources = analyzer.ask(prompt)
                    status.update(label="Evidence retrieved", state="complete")
                st.markdown(answer)
                st.caption(" · ".join(sources))
            st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
            persist_output("question_answer", f"Question: {prompt}\n\nAnswer: {answer}")
else:
    st.space("small")
    st.info("Upload a document, index it once, then use the analysis studio to interrogate its evidence.", icon=":material/lightbulb:")
