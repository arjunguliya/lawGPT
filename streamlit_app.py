import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from streamlit.web.server.websocket_headers import _get_websocket_headers
import hmac
import requests
from flask import Flask, request, jsonify
import threading

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(page_title="LawGPT API", page_icon="⚖️")

# Get OpenAI API key from Streamlit secrets
api_key = ""
if hasattr(st, "secrets") and "openai" in st.secrets:
    api_key = st.secrets["openai"]["api_key"]

# Add API key input in the sidebar
with st.sidebar:
    st.title("LawGPT API")
    user_api_key = st.text_input("OpenAI API Key", type="password")
    if user_api_key:
        api_key = user_api_key
    
    st.divider()
    st.markdown("This is the backend API for LawGPT")

# Function to handle the query
def process_query(query):
    try:
        # Check if API key is available
        if not api_key:
            return {
                "answer": "Error: Please provide an OpenAI API key in the sidebar or through environment variables.",
                "status": "error"
            }
        
        # Create client for this request
        client = OpenAI(api_key=api_key)
            
        # Call the OpenAI API with the client
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

# Handle query parameters for direct access
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

# Create a Flask API endpoint
app = Flask(__name__)

@app.route('/api/query', methods=['POST', 'OPTIONS'])
def api_query():
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'success'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
        
    # Handle POST request
    data = request.json
    if not data or 'query' not in data:
        return jsonify({'error': 'Query is required'}), 400
        
    result = process_query(data['query'])
    
    # Add CORS headers
    response = jsonify(result)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# Start the Flask server in a separate thread
def run_flask_app():
    from waitress import serve
    serve(app, host='0.0.0.0', port=8501)

# Start Flask in a background thread
threading.Thread(target=run_flask_app, daemon=True).start()

# Add API documentation
st.divider()
st.header("API Documentation")

api_docs = """
### API Endpoints

This application provides both a visual interface and a REST API endpoint:

**POST /api/query**

Request body:
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

You can use this endpoint directly from your frontend application.
"""

st.markdown(api_docs)

# Instructions for frontend developers
st.subheader("Connecting to the API")
st.code("""
// Example API call in JavaScript
const fetchLegalAdvice = async (query) => {
  try {
    const response = await fetch('https://your-streamlit-app-url.streamlit.app/api/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });
    
    return await response.json();
  } catch (error) {
    console.error('Error:', error);
    return { status: 'error', answer: 'Failed to connect to the API' };
  }
};
""", language="javascript")

# Instructions for setting up the API key
st.warning("⚠️ Important: Make sure to add your OpenAI API key in the sidebar to use this app, or add it to Streamlit secrets!")
