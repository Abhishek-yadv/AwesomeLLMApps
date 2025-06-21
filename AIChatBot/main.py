import streamlit as st
from groq import Groq
import time

# Set page config
st.set_page_config(
    layout="wide", page_title="AI Chat Assistant", page_icon="🤖")

# Custom CSS for a modern, sleek design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    
    body {
        font-family: 'Roboto', sans-serif;
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    .stApp {
        background-color: #1E1E1E;
    }
    .css-1d391kg {
        background-color: #2C2C2C;
    }
    .stTextInput > div > div > input, .stTextArea textarea {
        background-color: #3A3A3A;
        color: #FFFFFF;
        border: 1px solid #4CAF50;
        border-radius: 5px;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #45a049;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #2C3E50;
        align-self: flex-end;
        max-width: 80%;
    }
    .assistant-message {
        background-color: #34495E;
        align-self: flex-start;
        max-width: 80%;
    }
    .message-content {
        margin-top: 0.5rem;
    }
    .st-emotion-cache-16idsys p {
        font-size: 1.1rem;
        line-height: 1.5;
    }
    .user-input-area {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #2C2C2C;
        padding: 1rem;
        z-index: 1000;
    }
    .chat-container {
        margin-bottom: 100px;
    }
    .role-label {
        font-weight: bold;
        font-size: 1.2rem;
        background: linear-gradient(45deg, #FF4500, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 5px;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.title("🤖 AI Chat Assistant")
st.markdown("Powered by Groq's advanced language models")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter your Groq API Key:", type="password")
    model = st.selectbox("Select Model:", [
                         "llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"], index=0)

    temperature = st.slider("Temperature", min_value=0.1,
                            max_value=1.0, value=0.7, step=0.1)

    max_tokens = st.number_input(
        "Max Tokens", min_value=64, max_value=4096, value=1024, step=64)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat container
chat_container = st.container()

# Display chat messages
with chat_container:
    for message in st.session_state.messages:
        with st.container():
            st.markdown(
                f"<div class='chat-message {message['role']}-message'>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='role-label'>{message['role'].title()}</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='message-content'>{message['content']}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# User input area
user_input = st.text_area("Type your message here:", key="user_input")
send_button = st.button("Send")

# Handle send button click
if send_button and user_input:
    if not api_key:
        st.sidebar.error("Please enter your Groq API key in the sidebar.")
    else:
        # Add user message to chat history
        st.session_state.messages.append(
            {"role": "user", "content": user_input})

        # Create Groq client
        client = Groq(api_key=api_key)

        with st.spinner("AI is thinking..."):
            try:
                # Prepare messages for API call
                api_messages = [
                    {"role": "system", "content": "You are a helpful assistant."}]
                for msg in st.session_state.messages:
                    role = "assistant" if msg["role"] == "assistant" else "user"
                    api_messages.append(
                        {"role": role, "content": msg["content"]})

                # Generate AI response
                chat_completion = client.chat.completions.create(
                    messages=api_messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=1.0,
                    stream=True,
                )

                # Stream the response
                full_response = ""
                message_placeholder = st.empty()
                for chunk in chat_completion:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                        time.sleep(0.01)

                # Add the full response to chat history
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response})
                message_placeholder.markdown(full_response)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

        # Clear user input
        st.experimental_rerun()

# Add a button to clear chat history
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.experimental_rerun()
