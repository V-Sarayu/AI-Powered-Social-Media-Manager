from retriever import get_retriever

retriever = get_retriever()

while True:
    query = input("Ask something about your club info: ").strip()
    if query.lower() in {"exit", "quit"}:
        break

    nodes = retriever.retrieve(query)
    print("\nTop Matches:")
    for i, node in enumerate(nodes, 1):
        print(f"{i}. {node.text}\n")
