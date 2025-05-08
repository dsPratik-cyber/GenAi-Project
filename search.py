import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("laptop_index.faiss")
df = pickle.load(open("laptops.pkl", "rb"))

def search_laptops(query, k=10):
    query_vec = model.encode([query])
    _, indices = index.search(np.array(query_vec), k)
    results = df.iloc[indices[0]]
    return results
