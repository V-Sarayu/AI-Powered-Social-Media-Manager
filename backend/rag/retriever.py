import os
from llama_index.core import (
    StorageContext,
    VectorStoreIndex,
    ServiceContext
)
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

# ========== CONFIGURATION ==========
# Get absolute path to chroma_db folder relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
persist_dir = os.path.join(BASE_DIR, "chroma_db")

# ========== LOAD CHROMA DB AND EMBEDDINGS ==========
chroma_client = chromadb.PersistentClient(path=persist_dir)
chroma_collection = chroma_client.get_or_create_collection("club_data")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# ========== STORAGE CONTEXT & INDEX (NO LLM) ==========
storage_context = StorageContext.from_defaults(
    persist_dir=persist_dir,
    vector_store=vector_store
)
service_context = ServiceContext.from_defaults(llm=None)
index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    embed_model=embed_model,
    service_context=service_context
)

# ========== RETRIEVER ==========
retriever = VectorIndexRetriever(
    index=index,
    embed_model=embed_model,
    similarity_top_k=2
)

# ========== INTERACTIVE QUERY LOOP ==========
print("Type your query (or 'exit' to quit):\n")
while True:
    query = input(">>> Query: ").strip()
    if query.lower() in ['exit', 'quit']:
        print("Goodbye!")
        break

    try:
        results = retriever.retrieve(query)
        if not results:
            print("\nNo relevant chunks found.\n")
            continue

        print("\n🔍 Top relevant chunks:\n")
        for i, node in enumerate(results, 1):
            print(f"[{i}] {node.get_content().strip()}\n")
    except Exception as e:
        print(f"Error during retrieval: {e}")
