import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(page_title="LawGPT API", page_icon="⚖️")

# Get OpenAI API key from environment or secrets
api_key = os.getenv("OPENAI_API_KEY", "")
if not api_key and hasattr(st, "secrets") and "openai" in st.secrets:
    api_key = st.secrets["openai"]["api_key"]


# Add API key input in the sidebar
with st.sidebar:
    st.title("LawGPT API")
    user_api_key = st.text_input("OpenAI API Key", type="password")
    if user_api_key:
        api_key = user_api_key
    
    st.divider()
    st.markdown("This is the backend API for LawGPT")

# Initialize OpenAI client only if we have an API key
client = None
if api_key:
    client = OpenAI(api_key=api_key)

# Create API endpoints
st.title("LawGPT API")

# Function to handle the query
def process_query(query):
    try:
        # Check if API key is available
        if not api_key:
            return {
                "answer": "Error: Please provide an OpenAI API key in the sidebar or through environment variables.",
                "status": "error"
            }
        
        # Create client if not already created
        nonlocal client
        if client is None:
            client = OpenAI(api_key=api_key)
            
        # Call the OpenAI API with the new client
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a legal assistant helping with legal questions. Provide accurate and helpful information, but make it clear when someone should consult with a qualified legal professional."},
                {"role": "user", "content": query}
            ]
        )
        
        # Extract the response using the new format
        return {
            "answer": completion.choices[0].message.content,
            "status": "success"
        }
    except Exception as e:
        return {
            "answer": f"Error: {str(e)}",
            "status": "error"
        }

# Create a form for manual testing
with st.form("query_form"):
    query = st.text_area("Enter your legal question:")
    submit_button = st.form_submit_button("Submit")
    
    if submit_button and query:
        with st.spinner("Processing..."):
            result = process_query(query)
            st.markdown("### Response:")
            if result["status"] == "success":
                st.write(result["answer"])
            else:
                st.error(result["answer"])

# Handle query parameters - simplified to avoid redirect loops
query_params = st.experimental_get_query_params()
if "query" in query_params and query_params["query"][0]:
    query_from_url = query_params["query"][0]
    
    # Use session state to prevent reprocessing
    if "processed_query" not in st.session_state or st.session_state.processed_query != query_from_url:
        st.session_state.processed_query = query_from_url
        st.info(f"Processing query from URL parameter: {query_from_url}")
        with st.spinner("Processing..."):
            result = process_query(query_from_url)
            st.markdown("### Response:")
            if result["status"] == "success":
                st.write(result["answer"])
            else:
                st.error(result["answer"])

# API simulation section
st.divider()
st.header("API Simulation")
st.markdown("This section allows you to test the API as if you were calling it from your frontend.")

with st.expander("Try API Call"):
    api_query = st.text_area("Query JSON:", value='{"query": "What are my legal rights as a tenant?"}')
    
    if st.button("Send Request"):
        try:
            query_data = json.loads(api_query)
            if "query" in query_data:
                with st.spinner("Processing API request..."):
                    result = process_query(query_data["query"])
                    st.json(result)
            else:
                st.error("JSON must contain a 'query' field")
        except json.JSONDecodeError:
            st.error("Invalid JSON format")

# Add API documentation
st.divider()
st.header("API Documentation")

api_docs = """
### How to use this API

Since this is hosted on Streamlit, which isn't designed for pure API usage, you have two options:

1. **Direct user interaction**: Send users directly to this page to ask questions
2. **Iframe integration**: Embed this Streamlit app in your frontend using an iframe

For frontend integration, update your API service to use this URL.
"""

st.markdown(api_docs)

# Instructions for setting up the API key
st.warning("⚠️ Important: Make sure to add your OpenAI API key in the sidebar to use this app!")

# Simplified frontend connection instructions
st.subheader("Frontend Connection")
st.code("""
// In your frontend React code
const API_URL = 'https://your-streamlit-app-url.streamlit.app';

const fetchLegalAdvice = async (query) => {
  return {
    queryUrl: `${API_URL}?query=${encodeURIComponent(query)}`
  };
};
""", language="javascript")
