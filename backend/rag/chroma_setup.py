from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.storage.storage_context import StorageContext
from chromadb import PersistentClient
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
persist_dir = os.path.join(BASE_DIR, "chroma_db")
data_dir = os.path.join(BASE_DIR, "club_data")
collection_name = "club_data"

# Load documents
documents = SimpleDirectoryReader(input_dir=data_dir).load_data()

# Embeddings and Chroma setup
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
client = PersistentClient(path=persist_dir)
collection = client.get_or_create_collection(collection_name)
vector_store = ChromaVectorStore(chroma_collection=collection)

# ✅ Version-compatible storage context
storage_context = StorageContext.from_defaults(vector_store=vector_store)


# Build and persist index
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context,
    embed_model=embed_model,
)

# ✅ Persist index manually
index.storage_context.persist(persist_dir=persist_dir)

print("✅ Chroma index created and saved to:", persist_dir)
