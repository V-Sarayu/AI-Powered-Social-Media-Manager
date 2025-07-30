import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-lite')

class CompanyRAG:
    def __init__(self, model_name="all-MiniLM-L6-v2", json_path="data/company_details.json"):
        self.embedding_model = SentenceTransformer(model_name)
        self.company_info = {}
        self.document_store = []
        self.index = None  
        self.embeddings = None  
        self.load_company_json(json_path)

    def load_company_json(self, json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            self.company_info = json.load(f)
        self._process_company_info()

    def _process_company_info(self):
        self.document_store = []
        for section, content in self.company_info.items():
            if section == "keywords" and isinstance(content, list):
                self.document_store.append({
                    "content": "Company keywords: "+", ".join(content),
                    "metadata": {"section": section}
                })
            elif isinstance(content, str):
                for paragraph in content.split('\n\n'):
                    if paragraph.strip():
                        self.document_store.append({
                            "content": paragraph.strip(),
                            "metadata": {"section": section}
                        })
        self._build_index()

    def add_trending_hashtags(self, hashtags):
        if not hashtags:
            return
        self.document_store.append({
            "content": "Trending hashtags: "+", ".join(hashtags),
            "metadata": {"section": "trending_hashtags"}
        })
        self._build_index()

    def _build_index(self):
        if not self.document_store:
            return
        docs = [doc["content"] for doc in self.document_store]
        self.embeddings = np.array(self.embedding_model.encode(docs)).astype('float32')
        dim = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(self.embeddings)

    def search(self, query, k=3):
        if not self.index or not self.document_store:
            return []
        q_emb = np.array(self.embedding_model.encode([query])).astype('float32')
        dists, ids = self.index.search(q_emb, k=min(k, len(self.document_store)))
        return [self.document_store[i] for i in ids[0]]

    def generate_content(self, event, hashtags=None, yt_trends=None):
        docs_context = "\n".join(doc["content"] for doc in self.search(event['about'] + " " + event['name']))
        tags = ", ".join(hashtags) if hashtags else ""
        yt_text = "\n".join(f"- {t['title']} ({t['video_url']}) {', '.join(t['hashtags'])}" for t in yt_trends) if yt_trends else ""
        prompt = f"""You are a social media strategist for a student club.
Club context: {docs_context}
Event details: {event}
Instagram hashtags: {tags}
YouTube trends:
{yt_text}

1. Suggest 3 poster content ideas for this event.
2. Suggest 2 trending reel ideas (with themes).
3. Suggest 3 suitable audio tracks with reasons.
4. Merge Instagram & YouTube hashtags into one set."""
        resp = model.generate_content(prompt)
        return resp.text if hasattr(resp, "text") else str(resp)
