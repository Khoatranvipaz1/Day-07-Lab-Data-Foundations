from src import Document, EmbeddingStore, KnowledgeBaseAgent


def _demo_llm(prompt: str) -> str:
    return "Demo answer based on retrieved context."


def main() -> None:
    store = EmbeddingStore()
    store.add_documents([
        Document("demo", "Vector stores retrieve text by embedding similarity.", {})
    ])
    agent = KnowledgeBaseAgent(store, _demo_llm)
    print(agent.answer("What does a vector store do?"))


if __name__ == "__main__":
    main()
