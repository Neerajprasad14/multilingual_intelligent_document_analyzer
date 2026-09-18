@echo off
py -3.12 -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r intelligent_document_analyzer_rag/requirements.txt
ollama pull llama3.2:3b
streamlit run intelligent_document_analyzer_rag/app.py
pause
