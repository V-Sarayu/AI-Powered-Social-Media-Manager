import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import google.generativeai as genai

# API keys
GOOGLE_API_KEY = "AIzaSyAe4UGFU3pI9yZ7YtXtT7uaxTMQEmAD-rI"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-lite')

class CompanyRAG:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """Initialize the RAG system with a sentence embedding model."""
        self.embedding_model = SentenceTransformer(model_name)
        self.document_store = []
        self.index = None
        self.embeddings = None
        self.company_info = {}
        
    def load_company_json(self, json_path="company_details.json"):
        """
        Load company information from a JSON file.
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as file:
                self.company_info = json.load(file)
                print(f"Successfully loaded company information from {json_path}")
                
                # Process the loaded information into the document store
                self._process_company_info()
                return True
        except FileNotFoundError:
            print(f"Error: Company JSON file '{json_path}' not found.")
            return False
        except json.JSONDecodeError:
            print(f"Error: '{json_path}' contains invalid JSON format.")
            return False
    
    def _process_company_info(self):
        """Process the loaded company info into documents for the RAG system."""
        # Clear the existing document store
        self.document_store = []
        
        # Process each section of the company info
        for section, content in self.company_info.items():
            # Handle special case for keywords list
            if section == "keywords" and isinstance(content, list):
                keywords_text = "Company keywords: " + ", ".join(content)
                self.document_store.append({
                    "content": keywords_text,
                    "metadata": {"section": section}
                })
            # Handle normal string content
            elif isinstance(content, str):
                # Split long content into paragraphs
                paragraphs = content.split('\n\n')
                for paragraph in paragraphs:
                    if len(paragraph.strip()) > 20:  # Only add non-trivial paragraphs
                        self.document_store.append({
                            "content": paragraph.strip(),
                            "metadata": {"section": section}
                        })
        
        # Build the index with the updated document store
        self._build_index()
        
    def add_trending_hashtags(self, hashtags):
        """Add trending hashtags to the knowledge base."""
        chunks = [hashtags[i:i+10] for i in range(0, len(hashtags), 10)]
        for chunk in chunks:
            hashtag_text = "Trending hashtags: " + ", ".join(chunk)
            self.document_store.append({
                "content": hashtag_text,
                "metadata": {"section": "trending_hashtags"}
            })
        
        # Rebuild index after adding hashtags
        self._build_index()
    
    def _build_index(self):
        """Build the FAISS index with the current documents."""
        if not self.document_store:
            print("Warning: Document store is empty. No index created.")
            return
            
        contents = [doc["content"] for doc in self.document_store]
        self.embeddings = self.embedding_model.encode(contents)
        
        # Convert to float32 as required by FAISS
        self.embeddings = np.array(self.embeddings).astype('float32')
        
        # Build a new index
        embedding_dim = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.index.add(self.embeddings)
        print(f"Index built with {len(self.document_store)} documents")
    
    def search(self, query, k=3):
        """
        Search the knowledge base for content relevant to the query.
        Returns the k most relevant documents.
        """
        if not self.index or not self.document_store:
            print("Warning: Knowledge base is empty. Search returned no results.")
            return []
            
        query_embedding = self.embedding_model.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')
        
        distances, indices = self.index.search(query_embedding, k=min(k, len(self.document_store)))
        
        results = []
        for i in range(len(indices[0])):
            if indices[0][i] < len(self.document_store):
                results.append(self.document_store[indices[0][i]])
        
        return results
    
    def generate_content(self, project_description, target_audience, desired_tone, hashtags=None):
        """
        Generate content ideas using the RAG approach.
        1. Retrieve relevant company information based on the project description
        2. Include trending hashtags
        3. Generate content using Gemini with the retrieved context
        """
        # Retrieve relevant company information
        retrieved_docs = self.search(project_description, k=3)
        company_context = "\n".join([doc["content"] for doc in retrieved_docs])
        
        # Get company name for prompt
        company_name = self.company_info.get("name", "our organization")
        
        # Include trending hashtags if available
        hashtag_context = ""
        if hashtags:
            hashtag_docs = [doc for doc in self.document_store 
                           if doc["metadata"]["section"] == "trending_hashtags"]
            if hashtag_docs:
                hashtag_context = "\n".join([doc["content"] for doc in hashtag_docs[:2]])
        
        # Build the prompt with retrieved information
        prompt = f"""
        Generate creative marketing ideas for {company_name} for a project described as:
        "{project_description}"
        
        Target audience: {target_audience}
        Desired tone: {desired_tone}
        
        Here is relevant information about our company/organization:
        {company_context}
        
        {hashtag_context}
        
        Specifically, provide:
        - 3 creative social media post ideas that incorporate our company details and trending hashtags
        - 3 creative reel ideas that incorporate the trending hashtags and appeal to the target audience along with caption ideas.
        - 3 suggestions for trending or relevant audio that would suit the reel ideas. Include a brief reason for each suggestion.
        - 3 engaging poster ideas in extreme detail that can be used to generate an image using relevant hashtags.
        
        Make sure the content feels authentic to our organization's voice and leverages the trending hashtags appropriately.
        """
        
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating content with Gemini: {e}")
            return None
    
    def save_to_disk(self, filepath="company_rag.pkl"):
        """Save the RAG system to disk."""
        data = {
            "document_store": self.document_store,
            "embeddings": self.embeddings if self.embeddings is not None else None,
            "company_info": self.company_info
        }
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        print(f"RAG system saved to {filepath}")
    
    def load_from_disk(self, filepath="company_rag.pkl"):
        """Load the RAG system from disk."""
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            self.document_store = data["document_store"]
            self.embeddings = data["embeddings"]
            self.company_info = data.get("company_info", {})
            
            # If embeddings exist, rebuild the index
            if self.embeddings is not None:
                embedding_dim = self.embeddings.shape[1]
                self.index = faiss.IndexFlatL2(embedding_dim)
                self.index.add(self.embeddings)
                print(f"RAG system loaded from {filepath} with {len(self.document_store)} documents")
            else:
                print("Warning: No embeddings found in saved file. Index not rebuilt.")
            return True
        except FileNotFoundError:
            print(f"Error: Saved RAG file '{filepath}' not found.")
            return False
        except (pickle.PickleError, KeyError):
            print(f"Error: Could not load RAG data from '{filepath}'.")
            return False

# Example usage function
def main():
    print("=== Company RAG Content Generator ===\n")
    
    # Initialize the RAG system
    rag = CompanyRAG()
    
    # Check for existing saved RAG system
    if os.path.exists("company_rag.pkl"):
        print("Loading existing RAG system...")
        if not rag.load_from_disk():
            print("Failed to load existing system. Creating new one...")
    
    # Check if we need to load company info from JSON
    json_file = "company_details.json"
    load_from_json = True
    
    if rag.company_info:
        print(f"Company information already loaded for: {rag.company_info.get('name', 'Unknown')}")
        reload = input("Would you like to reload company information from JSON? (y/n): ").lower()
        load_from_json = reload == 'y'
    
    if load_from_json:
        json_path = input(f"Enter path to company JSON file (default: {json_file}): ").strip() or json_file
        if not rag.load_company_json(json_path):
            print("Failed to load company information from JSON.")
            return
    
    # Get project details
    project_description = input("Describe your social media post or campaign: ")
    target_audience = input("Who is the target audience for this specific post? ")
    desired_tone = input("What tone would you like for this post? (e.g., friendly, professional): ")
    
    # Option to add trending hashtags
    add_hashtags = input("Would you like to add trending hashtags? (y/n): ").lower() == 'y'
    if add_hashtags:
        hashtags_input = input("Enter trending hashtags (comma-separated): ")
        hashtags = [ht.strip() for ht in hashtags_input.split(",") if ht.strip()]
        if hashtags:
            rag.add_trending_hashtags(hashtags)
            print(f"Added {len(hashtags)} hashtags to the knowledge base.")
    
    # Generate content
    print("\nGenerating content ideas with your company context and any provided hashtags...")
    ideas = rag.generate_content(
        project_description=project_description,
        target_audience=target_audience,
        desired_tone=desired_tone
    )
    
    if ideas:
        print("\n=== Generated Content Ideas ===\n")
        print(ideas)
    else:
        print("\nFailed to generate ideas. Please check API keys and try again.")
    
    # Save the updated RAG system
    rag.save_to_disk()
    print("\nRAG system has been saved with any new hashtags added.")

if __name__ == "__main__":
    main()
