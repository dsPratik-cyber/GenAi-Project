# 💻 Smart Laptop Finder (with Gemini AI)

An intelligent product search app where users can type natural language queries like  
**"Budget laptop for remote work"** and get tailored recommendations.

Powered by:
- 🧠 Google Gemini 1.5 Flash for intelligent Q&A
- 🗃️ CSV data for laptop listings
- 🧾 Chat memory to track user questions
- 🌐 Streamlit for UI

---

## 🚀 Features

### 🔍 Smart Search
- Users type queries like "gaming laptop with good battery".
- System filters top 10 relevant laptops using a `search_laptops()` function.

### 📌 Laptop Selection + Q&A
- User selects a laptop from the results.
- Can ask natural language questions like:
  - "Is this good for students?"
  - "How is the battery compared to others?"

### 💬 Chat Memory
- All questions and answers are stored in session memory.
- Shown in collapsible sections for context.

### 📝 User Logging
- Logs user name, query, and selected laptop to `user_log.csv`.

---

## 🧠 Tech Stack

| Component         | Description                                   |
|------------------|-----------------------------------------------|
| Streamlit        | Frontend UI                                   |
| Gemini 1.5 Flash | LLM for contextual question answering         |
| Pandas           | Data handling for laptop CSV                  |
| dotenv           | API key management                            |

---


