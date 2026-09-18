from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/intelligent_document_analyzer"

engine = create_engine(DATABASE_URL)

print("Database connection configured successfully")