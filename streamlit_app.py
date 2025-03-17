import streamlit as st
from flask import request, jsonify
import openai
import os
from dotenv import load_dotenv

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

# Add API documentation
st.divider()
st.header("API Documentation")

api_docs = """
### POST /api/query
Send a POST request with JSON body:
```json
{
    "query": "Your legal question here"
}
```

Response:
```json
{
    "answer": "The response to your legal question",
    "status": "success"
}
```
"""

st.markdown(api_docs)

# Add CORS headers for API access
def set_cors_headers():
    st.markdown(
        """
        <script>
        // This enables CORS for API requests
        const meta = document.createElement('meta');
        meta.httpEquiv = 'Access-Control-Allow-Origin';
        meta.content = '*';
        document.head.appendChild(meta);
        </script>
        """, 
        unsafe_allow_html=True
    )

set_cors_headers()
