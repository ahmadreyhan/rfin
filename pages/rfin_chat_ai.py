# Import package(s)
import streamlit as st
from chat_ai.chat_ai import ChatAgent

# Set page configuration
st.set_page_config(page_title="RFin", layout="wide", 
                   page_icon="pages/assets/rf_logo.png",
                   initial_sidebar_state="collapsed",
                   menu_items={'About': "RFin is a Simple IDX Stocks Dashboard"})

if 'access' not in st.session_state:
    st.switch_page("app.py")
    hide_pages(["RFin Mini Dashboard", "RFin AI-ChatBot"])

st.title("💬 RFin Bot")
example_questions = [
    "IDX Historical Market Cap from December 23rd, 2023 until January 15th, 2024",
    "What are the top 3 companies by transaction volume over the last 7 days?",
    "Name 5 top gainers in the banks subsector last week"
]

with st.chat_message("assistant"):
    st.write("Here are some example questions you can try:")
    for question in example_questions:
        st.write(f"- {question}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Send something about IDX to RFin"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        st.write("🧠 Thinking...")
        chat_agent = ChatAgent(chat_input=prompt)
        response = chat_agent._execute_agent()
        st.write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

if st.sidebar.button("Log Out"):
    del st.session_state["access"]
    st.switch_page("app.py")
    hide_pages(["RFin Mini Dashboard", "RFin AI-ChatBot"])