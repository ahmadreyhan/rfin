# Import package(s)
import streamlit as st
import requests
from st_pages import show_pages, Page, hide_pages

# Set page configuration
st.set_page_config(page_title="RFin", layout="wide", 
                   page_icon="pages/assets/rf_logo.png",
                   initial_sidebar_state="auto",
                   menu_items={'About': "RFin is a Simple IDX Stocks Dashboard"})

def login(username, password):
    url = 'http://127.0.0.1:8000/api/login'
    data = {'username': username, 'password': password}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        st.session_state['access'] = response.json().get('access')
        st.success(f"Login successful. Welcome {username}")
    else:
        st.error("Invalid credentials")

def signup(email, username, password, first_name, last_name):
    url = 'http://127.0.0.1:8000/api/signup'
    data = {'email': email, 'username': username, 'password': password, 'first_name': first_name, 'last_name': last_name}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        st.success('User created successfully, please login!')
    else:
        st.error('Error creating user')

show_pages(
    [
        Page("app.py", "Login Page", icon="🏠"),
        Page("pages/rfin_mini_dashboard.py", "RFin Mini Dashboard", icon="📊"),
        Page("pages/rfin_chat_ai.py", "RFin AI-ChatBot", icon="💬"),
    ]
)

if 'access' not in st.session_state:
    hide_pages(["RFin Mini Dashboard", "RFin AI-ChatBot"])
    st.title("RFin - IDX Mini Dashboard") 
    st.write("Welcome to the RFin! Please log in or sign up to get started.")
    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])
    with login_tab:
        with st.form("login-form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type='password')
            submit = st.form_submit_button(label="Log In")
            if submit:
                if login(username, password):
                    st.sidebar.success(f"Welcome, {username}!")
                    st.switch_page("pages/rfin_mini_dashboard.py")
    with signup_tab:
        with st.form("signup-form"):        
            email = st.text_input("Email")
            username = st.text_input("Username")
            password = st.text_input("Password", type='password')
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            submit = st.form_submit_button(label="Sign Up")
            if submit:
                if email == '' or username == '' or password == '':
                    st.error("Email, Username, Password must be filled!")
                else:
                    signup(email, username, password, first_name, last_name)

if 'access' in st.session_state:
    st.switch_page("pages/rfin_mini_dashboard.py")