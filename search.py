from sentence_transformers import SentenceTransformer
import faiss
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re

# Load model and data
model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("laptop_index.faiss")
df = pickle.load(open("laptops.pkl", "rb"))

# Define supported contexts
supported_contexts = [
    "laptop", "notebook", "ultrabook", "macbook", "gaming", "business",
    "student", "budget", "high performance", "remote work", "lightweight",
    "travel", "school", "collage", "office", "under", "above"
]

# Precompute vectors for context validation
context_vectors = model.encode(supported_contexts)

def is_query_relevant(query, threshold=0.4):
    query_vec = model.encode([query])
    sims = cosine_similarity(query_vec, context_vectors)[0]
    return max(sims) > threshold

def extract_conditions(query):
    query = query.lower()
    conditions = {}

    # Price range
    if match := re.search(r'under ₹?(\d+)', query):
        conditions['max_price'] = int(match.group(1))
    if match := re.search(r'above ₹?(\d+)', query):
        conditions['min_price'] = int(match.group(1))

    # RAM
    if match := re.search(r'(\\d+)\\s*gb ram', query):
        ram_val = int(match.group(1))
        conditions['min_ram'] = ram_val
        conditions['max_ram'] = ram_val


    # Storage
    if match := re.search(r'(\d+)(tb|gb) (ssd|hdd|storage)', query):
        size = int(match.group(1))
        if match.group(2) == 'tb':
            size *= 1024
        conditions['min_storage'] = size

    # CPU
    if "i3" in query:
        conditions['cpu'] = "i3"
    elif "i5" in query:
        conditions['cpu'] = "i5"
    elif "i7" in query:
        conditions['cpu'] = "i7"

    # Weight
    if match := re.search(r'under (\d+(\.\d+)?)\s*kg', query):
        conditions['max_weight'] = float(match.group(1))

    return conditions

def filter_results(results, conditions):
    def satisfies(row):
        if 'max_price' in conditions and row['Product_price'] > conditions['max_price']:
            return False
        if 'min_price' in conditions and row['Product_price'] < conditions['min_price']:
            return False
        if 'min_ram' in conditions:
            try:
                ram_str = str(row['Ram']).lower().replace('gb', '').replace(' ', '').strip()
                ram = int(re.search(r'\d+', ram_str).group())
                if ram < conditions['min_ram']:
                    return False
            except:
                return False
        if 'min_storage' in conditions:
            try:
                mem = row['Memory']
                size = int(re.search(r'\d+', mem).group())
                if 'TB' in mem.upper():
                    size *= 1024
                if size < conditions['min_storage']:
                    return False
            except:
                return False
        if 'cpu' in conditions and conditions['cpu'].lower() not in row['Cpu'].lower():
            return False
        if 'max_weight' in conditions:
            try:
                weight = float(str(row['Product_Weight']).replace('kg', '').strip())
                if weight > conditions['max_weight']:
                    return False
            except:
                return False
        return True

    return results[results.apply(satisfies, axis=1)]

def search_laptops(query, k=15):
    if not is_query_relevant(query):
        return None

    query_vec = model.encode([query])
    _, indices = index.search(np.array(query_vec), k)
    results = df.iloc[indices[0]]

    conditions = extract_conditions(query)
    filtered = filter_results(results, conditions)

    return filtered.head(10)
