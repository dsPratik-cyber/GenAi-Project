from sentence_transformers import SentenceTransformer
import faiss
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("laptop_index.faiss")
df = pickle.load(open("laptops.pkl", "rb"))

# Define context topics your dataset supports
supported_contexts = ["laptop", "notebook", "ultrabook", "macbook", "gaming", "business", "student", "budget", "high performance", "remote work", "lightweight", "travel","school", "collage","office"]

# Precompute supported context vectors
context_vectors = model.encode(supported_contexts)

def is_query_relevant(query, threshold=0.4):
    query_vec = model.encode([query])
    sims = cosine_similarity(query_vec, context_vectors)[0]
    max_score = max(sims)
    return max_score > threshold

def search_laptops(query, k=10):
    if not is_query_relevant(query):
        return None  # Let UI handle this gracefully

    query_vec = model.encode([query])
    _, indices = index.search(np.array(query_vec), k)
    results = df.iloc[indices[0]]
    return results

