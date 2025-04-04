import chromadb

# Initialize persistent Chroma client
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="autosocial_data")

def seed_data():
    collection.add(
        ids=["event1"],
        documents=["NeuralHive hosted a Reinforcement Learning workshop on Q-Learning and DeepSeek in Feb 2025."],
        metadatas=[{"category": "workshop", "date": "2025-02-16"}]
    )

def get_collection():
    return collection

if __name__ == "__main__":
    seed_data()
