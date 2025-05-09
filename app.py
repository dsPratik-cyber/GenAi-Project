import streamlit as st
from search import search_laptops
from chatbot import ask_laptop_question
import pandas as pd
import os
import sys

os.environ["STREAMLIT_WATCHER_TYPE"] = "none"
sys.modules['torch.classes'] = None

st.set_page_config(page_title="Smart Laptop Finder", layout="centered")

# Ask user name
if "user_name" not in st.session_state or not st.session_state.user_name.strip():
    st.session_state.user_name = st.text_input("👋 Hello! What's your name?")
    if not st.session_state.user_name.strip():
        st.warning("Please enter your name to continue.")
        st.stop()

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("🔍 Smart Laptop Search")
query = st.text_input("Type your laptop need (e.g., Budget laptop for remote work):")

if query:
    st.write("🔎 Searching...")
    results = search_laptops(query)

    if results is None:
        st.error("❌ Sorry, we only support **laptop-related** queries right now.\n\nTry asking for something like:\n- Budget laptop for school\n- Lightweight laptop for travel\n- High performance notebook for gaming")
        st.stop()

    st.success(f"Hi {st.session_state.user_name}, here are the top {len(results)} laptops:")

    selected = st.radio("🎯 Select one to get detailed comparison:", results["desc"].tolist(), index=0)

    # Ask question
    st.subheader("💡 Ask anything about these laptops:")
    user_q = st.text_input("Your question:")

    if user_q:
        product_row = results[results["desc"] == selected].iloc[0]
        answer = ask_laptop_question(product_row, user_q, results)

        st.info(answer)

        # Save chat
        st.session_state.chat_history.append((user_q, answer))

    if st.session_state.chat_history:
        st.subheader("📜 Previous Q&A:")
        for i, (q, a) in enumerate(st.session_state.chat_history, 1):
            with st.expander(f"Q{i}: {q}"):
                st.markdown(a)

    # Save user log
    if selected:
        with open("user_log.csv", "a", encoding="utf-8") as f:
            f.write(f"{st.session_state.user_name},{query},{selected}\n")
