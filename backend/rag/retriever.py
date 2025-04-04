from rag.chroma_setup import get_collection


def query_events(user_query, k=3):
    collection = get_collection()
    results = collection.query(
        query_texts=[user_query],
        n_results=k
    )
    return results["documents"]
