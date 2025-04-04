import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from rag.retriever import query_events


if __name__ == "__main__":
    query = "generate content for a reinforcement learning workshop"
    results = query_events(query)

    print("🔍 Top relevant results:")
    for i, doc in enumerate(results, 1):
        print(f"{i}. {doc}")
