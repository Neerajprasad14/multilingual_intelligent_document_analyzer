import chromadb
from sentence_transformers import SentenceTransformer


class VectorStore:
    def __init__(self, collection_name="document_chunks"):
        self.client = chromadb.PersistentClient(path="data/chroma")
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    def add_chunks(self, doc_id, chunks):
        ids = [f"{doc_id}_{c['id']}" for c in chunks]
        texts = [c["text"] for c in chunks]
        embeddings = self.embedder.encode(
            texts,
            normalize_embeddings=True
        ).tolist()

        metadatas = [{
            "doc_id": c["doc_id"],
            "source": c["source"],
            "chunk_id": c["id"]
        } for c in chunks]

        # Remove an earlier copy of the same document.
        try:
            self.collection.delete(where={"doc_id": doc_id})
        except Exception:
            pass

        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def search(self, query, doc_id, top_k=5):
        query_embedding = self.embedder.encode(
            [query],
            normalize_embeddings=True
        ).tolist()

        result = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            where={"doc_id": doc_id}
        )

        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]

        return [
            {
                "text": text,
                "metadata": metadata
            }
            for text, metadata in zip(documents, metadatas)
        ]
