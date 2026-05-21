from app.services.rag_service import retrieve_relevant_chunks


def main():
    query = "When artemis 2 will reach the moon?"
    results = retrieve_relevant_chunks(query, top_k=3)

    for i, chunk in enumerate(results, start=1):
        print(f"\n--- Result {i} ---")
        print("Source:", chunk["source"])
        print("Score:", chunk["score"])
        print("Text:", chunk["text"])


if __name__ == "__main__":
    main()
