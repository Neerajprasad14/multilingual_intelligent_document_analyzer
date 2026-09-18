from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/intelligent_document_analyzer"

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version()"))
        print("Connected successfully!")
        print(result.fetchone())

except Exception as e:
    print("Database connection failed!")
    print(e)

