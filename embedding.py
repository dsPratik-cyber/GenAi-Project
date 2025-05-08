import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
from huggingface_hub import login
import os


login(token=os.getenv("HF_HOME"))



df = pd.read_csv(r"C:\Users\91888\Desktop\Smart Search\Data\laptop_data.csv")

# Create searchable description
df["desc"] = df.apply(lambda row: f"{row['Product_Name']} , {row['Product_Subcategory']}, {row['Ram']} RAM, {row['Memory']}, {row['Cpu']}, {row['Gpu']},{row['Product_Weight']}, Price ₹{row['Product_price']}", axis=1)

# Save original
df.to_csv("laptops_clean.csv", index=False)

# Embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(df["desc"].tolist(), show_progress_bar=True)

# Save model and index
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(np.array(embeddings))

faiss.write_index(index, "laptop_index.faiss")
pickle.dump(df, open("laptops.pkl", "wb"))
