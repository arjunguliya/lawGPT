import streamlit as st
import openai
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set page config
st.set_page_config(page_title="LawGPT API", page_icon="⚖️")

# Add API key input in the sidebar
with st.sidebar:
    st.title("LawGPT API")
    api_key = st.text_input("OpenAI API Key", type="password")
    if api_key:
        openai.api_key = api_key
    
    st.divider()
    st.markdown("This is the backend API for LawGPT")

# Create API endpoints
st.title("LawGPT API")

# Add HTTP request handling
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to handle the query
def process_query(query):
    try:
        # Your existing code to process the query
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a legal assistant helping with legal questions."},
                {"role": "user", "content": query}
            ]
        )
        
        return {
            "answer": completion.choices[0].message.content,
            "status": "success"
        }
    except Exception as e:
        return {
            "answer": str(e),
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
            st.write(result["answer"])

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

# Add connection instructions
st.subheader("Frontend Connection")
st.code("""
// In your frontend React code
const API_URL = '""" + st.experimental_get_query_params().get("streamlit_server_url", [""])[0] + """';

const fetchLegalAdvice = async (query) => {
  // Redirect to Streamlit with the query
  window.location.href = `${API_URL}?query=${encodeURIComponent(query)}`;
};
""", language="javascript")

# Handle query parameters
query_params = st.experimental_get_query_params()
if "query" in query_params:
    query_from_url = query_params["query"][0]
    st.info(f"Processing query from URL parameter: {query_from_url}")
    with st.spinner("Processing..."):
        result = process_query(query_from_url)
        st.markdown("### Response:")
        st.write(result["answer"])
