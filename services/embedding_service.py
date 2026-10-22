import ollama


class EmbeddingService:
    def __init__(
        self,
        model_name: str = "nomic-embed-text",
    ) -> None:
        self.model_name = model_name

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        if not texts:
            return []

        # Nomic uses this prefix for documents in a
        # retrieval index.
        inputs = [
            f"search_document: {text}"
            for text in texts
        ]

        response = ollama.embed(
            model=self.model_name,
            input=inputs,
        )

        vectors = response["embeddings"]

        if len(vectors) != len(texts):
            raise RuntimeError(
                "Embedding count does not match text count."
            )

        dimensions = len(vectors[0])

        if any(len(vector) != dimensions for vector in vectors):
            raise RuntimeError(
                "Embedding dimensions are inconsistent."
            )

        return vectors

    def embed_query(self, query: str) -> list[float]:
        if not query.strip():
            raise ValueError("Query cannot be empty.")

        # The query prefix distinguishes a search query
        # from the documents being indexed.
        response = ollama.embed(
            model=self.model_name,
            input=f"search_query: {query}",
        )

        return response["embeddings"][0]