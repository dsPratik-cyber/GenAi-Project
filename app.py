import streamlit as st
from search import search_laptops
from chatbot import ask_laptop_question, generate_laptop_description
import pandas as pd
import os
import sys

# Set environment variables
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"
sys.modules['torch.classes'] = None

# Configure Streamlit page
st.set_page_config(page_title="Smart Laptop Finder", layout="centered")

# Ask user name
if "user_name" not in st.session_state or not st.session_state.get("user_name", "").strip():
    st.session_state.user_name = st.text_input("👋 Hello! What's your name?")
    if not st.session_state.user_name.strip():
        st.warning("Please enter your name to continue.")
        st.stop()

# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "selected_product" not in st.session_state:
    st.session_state.selected_product = None
if "product_row" not in st.session_state:
    st.session_state.product_row = None
if "results" not in st.session_state:
    st.session_state.results = None

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

            if selected:
                st.session_state.selected_product = selected
                st.session_state.product_row = results[results["desc"] == selected].iloc[0]
                st.session_state.results = results

                # Generate and display AI-based description
                description = generate_laptop_description(selected)
                st.markdown(f"**📝 AI-generated Description:** {description}")

                # Display chat history
                st.subheader("💬 Chat with the assistant:")
                for i, (q, a) in enumerate(st.session_state.chat_history, 1):
                    with st.chat_message("user"):
                        st.markdown(q)
                    with st.chat_message("assistant"):
                        st.markdown(a)

                # Chat input for user questions
                user_q = st.chat_input("Ask a question about this laptop:")
                if user_q:
                    answer = ask_laptop_question(st.session_state.product_row, user_q, st.session_state.results)
                    st.session_state.chat_history.append((user_q, answer))
                    with st.chat_message("user"):
                        st.markdown(user_q)
                    with st.chat_message("assistant"):
                        st.markdown(answer)

                # Save user log for tracking purposes (CSV)
                with open("user_log.csv", "a", encoding="utf-8") as f:
                    f.write(f"{st.session_state.user_name},{query},{selected}\n")

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.stop()
