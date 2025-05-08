import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def ask_laptop_question(product_info, user_question, all_laptops=None):
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
