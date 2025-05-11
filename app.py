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

# Initialize chat history and query state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# Title and instructions
st.title("🔍 Smart Laptop Search")

# User input for the search query
query = st.text_input("Type your laptop need (e.g., Budget laptop for remote work):", value=st.session_state.search_query)

# Save the query in session state for future use
if query != st.session_state.search_query:
    st.session_state.search_query = query

if query:
    st.write("🔎 Searching...")

    # Show a spinner while waiting for search results
    with st.spinner("Searching for laptops..."):
        try:
            results = search_laptops(query)

            if results is None or results.empty:
                st.error("❌ Sorry, no relevant laptops found. Please refine your query or try different keywords.")
                st.stop()

            st.success(f"Hi {st.session_state.user_name}, here are the top laptops:")

            # Display the top 5 results
            top_results = results.head(5)  # Show top 5 laptops
            
            # No default selection, let the user choose
            selected = st.radio(
                "🎯 Select one to get detailed comparison:",
                top_results["desc"].tolist()
            )

            # Ask a question about the selected laptop
            if selected:
                st.subheader("💡 Ask anything about this laptop:")
                user_q = st.text_input("Your question:")

                if user_q:
                    product_row = results[results["desc"] == selected].iloc[0]
                    answer = ask_laptop_question(product_row, user_q, results)

                    if answer:
                        st.info(answer)
                    else:
                        st.warning("❓ Sorry, I couldn't answer your question. Try rephrasing it.")

                    # Save the chat history
                    st.session_state.chat_history.append((user_q, answer))

            # Display the chat history
            if st.session_state.chat_history:
                st.subheader("📜 Previous Q&A:")
                for i, (q, a) in enumerate(st.session_state.chat_history, 1):
                    with st.expander(f"Q{i}: {q}"):
                        st.markdown(a)

            # Save user log for tracking purposes (CSV)
            if selected:
                with open("user_log.csv", "a", encoding="utf-8") as f:
                    f.write(f"{st.session_state.user_name},{query},{selected}\n")

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.stop()
