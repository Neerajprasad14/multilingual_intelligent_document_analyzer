# Intelligent Document Analyzer using RAG

A local RAG application that accepts PDF, DOCX and TXT documents and provides:

- Executive summary
- Detailed key points
- Evidence-based advantages
- Disadvantages and risks
- Practical action points
- Question answering over the uploaded document
- Source/chunk references

## Architecture

Document -> Text Extraction -> Chunking -> Embeddings -> ChromaDB
                                                |
                                                v
User Query -> Retrieval -> Relevant Chunks -> Ollama LLM -> Answer

## Requirements

- Python 3.10+
- 8 GB RAM minimum; 16 GB recommended
- Ollama
- Internet connection for the first download of Python packages/models

## Setup

### 1. Create virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install packages

```bash
pip install -r requirements.txt
```

### 3. Install Ollama

Install Ollama from its official website, then download a model:

```bash
ollama pull llama3.2:3b
```

For a stronger machine/model, you can use another Ollama model and enter its name in the Streamlit sidebar.

Test:

```bash
ollama run llama3.2:3b
```

### 4. Run

```bash
streamlit run app.py
```

Open the URL shown by Streamlit, upload a PDF/DOCX/TXT document and click **Analyze Document**.

## Run with Docker

Docker Compose starts the Streamlit app and PostgreSQL. Ollama stays on your host so it can use your existing local model.

```bash
ollama pull llama3.2:3b
docker compose up --build
```

Open `http://localhost:8501`. Tables are created automatically. Set `OLLAMA_MODEL` or `OLLAMA_BASE_URL` before starting Compose if needed.

## Important note

The "advantages" and "disadvantages" are evidence-based document analysis, not professional legal, financial or medical advice. For contracts or high-stakes documents, verify important conclusions with a qualified professional.

## Project structure

```text
intelligent_document_analyzer_rag/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── app/
│   ├── __init__.py
│   ├── ingest.py
│   ├── vector_store.py
│   ├── llm.py
│   └── rag.py
│
└── data/
    ├── uploads/
    └── chroma/
```
