from app.vector_store import VectorStore
from app.llm import OllamaLLM


class RAGAnalyzer:
    def __init__(self, doc_id, chunks, model="llama3.2:3b", top_k=5):
        self.doc_id = doc_id
        self.chunks = chunks
        self.top_k = top_k
        self.llm = OllamaLLM(model=model)
        self.store = VectorStore()

        self.store.add_chunks(doc_id, chunks)

    def _retrieve(self, query, k=None):
        return self.store.search(
            query=query,
            doc_id=self.doc_id,
            top_k=k or self.top_k
        )

    @staticmethod
    def _context(results):
        blocks = []
        for item in results:
            source = item["metadata"].get("source", "document")
            chunk_id = item["metadata"].get("chunk_id", "?")
            blocks.append(
                f"[Source: {source}, Chunk: {chunk_id}]\n{item['text']}"
            )
        return "\n\n".join(blocks)

    def _ask_with_context(self, instruction, query, k=None):
        results = self._retrieve(query, k)
        context = self._context(results)

        prompt = f"""
You are an intelligent document analysis assistant.

IMPORTANT RULES:
1. Use only the supplied document context.
2. Do not invent facts, clauses, numbers, dates or conclusions.
3. If the context does not contain enough evidence, explicitly say so.
4. Distinguish facts stated in the document from your interpretation.
5. When identifying advantages or disadvantages, explain WHY they matter.
6. For "to us", evaluate from the perspective of the document reader/user,
   but do not assume personal facts that are not in the document.
7. Mention source chunk numbers like [Chunk 3] when making important claims.

TASK:
{instruction}

DOCUMENT CONTEXT:
{context}
"""
        return self.llm.generate(prompt), results

    def summary(self):
        # Hierarchical summarization so a long document is not sent to the LLM at once.
        partials = []

        batch_size = 6
        for i in range(0, len(self.chunks), batch_size):
            batch = self.chunks[i:i + batch_size]
            context = "\n\n".join(
                f"[Chunk {c['id']}]\n{c['text']}" for c in batch
            )

            prompt = f"""
Summarize the following section of a document.
Keep important facts, obligations, dates, amounts, decisions and conditions.
Do not invent information.

SECTION:
{context}
"""
            partials.append(self.llm.generate(prompt))

        if len(partials) == 1:
            return partials[0]

        combined = "\n\n".join(
            f"[Section Summary {i+1}]\n{s}"
            for i, s in enumerate(partials)
        )

        return self.llm.generate(f"""
Create a final executive summary from the section summaries below.

Include:
- What the document is about
- Main purpose
- Most important points
- Important obligations/requirements
- Important dates, amounts or conditions
- Overall conclusion

Do not add facts not present in the summaries.

{combined}
""")

    def analyze_key_points(self):
        answer, _ = self._ask_with_context(
            """
Give a detailed analysis of the most important points in the document.

Use this format:
### 1. Point
- What it says
- Why it matters
- Practical implication
- Source

Cover the most significant points rather than repeating minor details.
""",
            "important key points requirements obligations conditions decisions",
            k=min(10, len(self.chunks))
        )
        return answer

    def analyze_advantages(self):
        answer, _ = self._ask_with_context(
            """
Identify the advantages/benefits that are actually supported by the document.

For each advantage provide:
1. Advantage
2. Evidence from the document
3. Why it benefits the reader/user
4. Any limitation or condition attached to the benefit

Do not call something an advantage merely because it sounds positive.
""",
            "benefits advantages positive outcomes rights protections savings opportunities favorable terms",
            k=min(8, len(self.chunks))
        )
        return answer

    def analyze_disadvantages(self):
        answer, _ = self._ask_with_context(
            """
Identify disadvantages, risks, costs, restrictions, obligations, unfavorable
conditions, ambiguities and potential concerns.

For each item provide:
1. Risk/disadvantage
2. Evidence
3. Why it could negatively affect the reader/user
4. Severity: Low / Medium / High
5. What should be checked or clarified

Do not invent risks that are not reasonably supported by the document.
""",
            "risks disadvantages costs penalties restrictions obligations unfavorable conditions termination liability exclusions",
            k=min(10, len(self.chunks))
        )
        return answer

    def action_points(self):
        answer, _ = self._ask_with_context(
            """
Create a practical action checklist based only on the document.

Separate:
- Must do
- Should review
- Questions to clarify
- Deadlines / dates
- Documents or evidence needed

Clearly state when the document does not provide a deadline.
""",
            "actions deadlines requirements documents signatures payment renewal termination next steps",
            k=min(10, len(self.chunks))
        )
        return answer

    def ask(self, question):
        answer, results = self._ask_with_context(
            f"""
Answer the user's question clearly and directly.

USER QUESTION:
{question}

If the answer is not supported by the retrieved context, say:
"The uploaded document does not provide enough information to answer this."
""",
            question,
            k=self.top_k
        )

        sources = []
        for item in results:
            meta = item["metadata"]
            sources.append(
                f"{meta.get('source', 'document')} — Chunk {meta.get('chunk_id', '?')}"
            )

        return answer, sources
