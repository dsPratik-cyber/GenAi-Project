from sentence_transformers import SentenceTransformer
import faiss
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re
import google.generativeai as genai
import os
import pandas as pd

# Load Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# Load Sentence Transformer model, FAISS index, and DataFrame
model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("laptop_index.faiss")
df = pickle.load(open("laptops.pkl", "rb"))

# Predefined context categories
supported_contexts = [
    "laptop", "notebook", "ultrabook", "macbook", "gaming", "business",
    "student", "budget", "high performance", "remote work", "lightweight",
    "travel", "school", "college", "office", "under", "above"
]
context_vectors = model.encode(supported_contexts)

# Pre-compile regex patterns for faster matching
patterns = {
    'price_under': re.compile(r'under \u20b9?(\d+)'),
    'price_above': re.compile(r'above \u20b9?(\d+)'),
    'ram': re.compile(r'(\d+)\s*gb ram'),
    'storage': re.compile(r'(\d+)(tb|gb) (ssd|hdd|storage)'),
    'weight': re.compile(r'under (\d+(\.\d+)?)\s*kg')
}

# Relevance checker (modified for laptop-related queries only)
def is_query_relevant(query, threshold=0.4):
    query = query.lower()
    if "laptop" not in query and not any(ctx in query for ctx in supported_contexts if ctx != "under" and ctx != "above"):
        return False
    query_vec = model.encode([query])
    sims = cosine_similarity(query_vec, context_vectors)[0]
    return max(sims) > threshold

# Classic keyword-based condition extraction
def extract_conditions(query):
    query = query.lower()
    conditions = {}

    if match := patterns['price_under'].search(query):
        conditions['max_price'] = int(match.group(1))
    if match := patterns['price_above'].search(query):
        conditions['min_price'] = int(match.group(1))
    if match := patterns['ram'].search(query):
        conditions['exact_ram'] = int(match.group(1))
    if match := patterns['storage'].search(query):
        size = int(match.group(1))
        if match.group(2) == 'tb':
            size *= 1024
        conditions['min_storage'] = size
    if "i3" in query:
        conditions['cpu'] = "i3"
    elif "i5" in query:
        conditions['cpu'] = "i5"
    elif "i7" in query:
        conditions['cpu'] = "i7"
    if match := patterns['weight'].search(query):
        conditions['max_weight'] = float(match.group(1))

    return conditions

# Gemini LLM to extract structured filters from query
def extract_conditions_from_llm(query):
    prompt = f"""
You are a smart assistant that converts natural language queries into supported_contexts words with structured laptop filter conditions.
User query: "{query}"
Return a query important words with valid Python dictionary with any of the following keys if applicable:
- max_price
- min_price
- exact_ram
- min_storage
- cpu (e.g., "i5")
- max_weight

return query important word add laptop then with the dictionary .
"""
    try:
        response = gemini_model.generate_content(prompt)
        return eval(response.text.strip())
    except:
        return {}

# Filters a DataFrame based on given conditions
def filter_results(results, conditions):
    def satisfies(row):
        if 'max_price' in conditions and row['Product_price'] > conditions['max_price']:
            return False
        if 'min_price' in conditions and row['Product_price'] < conditions['min_price']:
            return False
        if 'exact_ram' in conditions:
            try:
                ram_str = str(row['Ram']).lower().replace('gb', '').replace(' ', '').strip()
                ram = int(re.search(r'\d+', ram_str).group())
                if ram != conditions['exact_ram']:
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

# Gemini-based refinement on retrieved laptops
def llm_filter_results(query, retrieved_df):
    laptop_list = retrieved_df.to_dict(orient="records")
    prompt = f"""
You are a smart assistant.
The user query is: "{query}"
From the list of laptops below, return only those that match the intent well.
Return a Python list of dictionaries with matched laptops.
Laptops: {laptop_list}
"""
    try:
        response = gemini_model.generate_content(prompt)
        filtered = eval(response.text.strip())
        return pd.DataFrame(filtered)
    except:
        return retrieved_df

# Final search pipeline
def search_laptops(query, k=15):
    if not is_query_relevant(query):
        return "This search engine is optimized for laptops only. Please try a query related to laptops."

    # Step 1: LLM + rule-based condition extraction
    llm_conditions = extract_conditions_from_llm(query)
    rule_conditions = extract_conditions(query)
    combined_conditions = {**rule_conditions, **llm_conditions}

    # Step 2: Pre-filter entire dataframe before retrieval
    prefiltered_df = filter_results(df, combined_conditions)
    if prefiltered_df.empty:
        prefiltered_df = df.copy()

    # Step 3: Semantic search on filtered subset
    query_vec = model.encode([query])
    if not hasattr(search_laptops, "sub_index"):
        # Load or create the FAISS index only once
        sub_index = faiss.IndexFlatL2(query_vec.shape[1])
        sub_vectors = model.encode(prefiltered_df['Product_Name'].tolist())
        sub_index.add(np.array(sub_vectors))
        search_laptops.sub_index = sub_index  # Cache FAISS index

    _, sub_indices = search_laptops.sub_index.search(np.array(query_vec), min(k, len(prefiltered_df)))
    retrieved_df = prefiltered_df.iloc[sub_indices[0]]

    # Step 4: Final Gemini-based refinement
    final_df = llm_filter_results(query, retrieved_df)

    return final_df.head(10)
