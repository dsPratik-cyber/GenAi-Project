import os
from dotenv import load_dotenv
import google.generativeai as genai
import pandas as pd

load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def ask_laptop_question(product_info, user_question, all_laptops=None):
    """
    Answers user questions about a selected laptop, optionally comparing it with other laptops.

    Parameters:
    - product_info (str): Description of the selected laptop.
    - user_question (str): The user's question.
    - all_laptops (pd.DataFrame, optional): DataFrame containing descriptions of other laptops.

    Returns:
    - str: The generated answer.
    """
    if all_laptops is not None:
        context = "\n\n".join(
            [f"{i+1}. {row['desc']}" for i, row in all_laptops.iterrows()]
        )
        prompt = f"""
You are a laptop expert assistant.

The user was shown these 10 laptops:
{context}

They selected this one:
{product_info}

Now they asked: "{user_question}"

Answer based on the selected laptop, but feel free to compare with others.
"""
    else:
        prompt = f"""
You are a helpful assistant. A user selected this laptop:

{product_info}

Now they asked: "{user_question}"
Respond with a helpful, honest answer.
"""
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_laptop_description(product_info):
    """
    Generates a concise, appealing description for a laptop.

    Parameters:
    - product_info (str): Description of the laptop.

    Returns:
    - str: The generated product description.
    """
    prompt = f"""
You are a product marketing expert.

Based on the following laptop details, write a short, appealing product description in 1–2 sentences.
Highlight key features like battery life, portability, performance, and ideal use-cases (like work, gaming, students, etc.).

Laptop details: {product_info}
"""
    response = model.generate_content(prompt)
    return response.text.strip()
