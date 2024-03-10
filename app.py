import streamlit as st
import requests
import re
import pandas as pd
from dotenv import load_dotenv
import os
from llama_index.llms.openai import OpenAI
from llama_index.core import SummaryIndex, SimpleDirectoryReader, VectorStoreIndex
import json

# Specify the directory where you want to save the files. Ensure this directory exists.
save_dir = "."

# Ensure the directory exists
os.makedirs(save_dir, exist_ok=True)

# Load environment variables, if necessary
load_dotenv()

def extract_product_id(url):
    """Extracts and returns the Amazon product ID from a given URL."""
    match = re.search(r'/dp/([A-Z0-9]{10})', url)
    if match:
        return match.group(1)
    else:
        match = re.search(r'product/([A-Z0-9]{10})', url)
        if match:
            return match.group(1)
    return None

def query_product(product_id):
    """Queries Axesso API for a given product ID and returns the response."""
    url = "https://axesso-axesso-amazon-data-service-v1.p.rapidapi.com/amz/amazon-lookup-product"
    querystring = {"url": f"https://www.amazon.com/dp/{product_id}/"}
    headers = {
        "X-RapidAPI-Key": os.getenv("X-RapidAPI-Key"),
        "X-RapidAPI-Host": os.getenv("X-RapidAPI-Host")
    }
    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"No response or error occurred. Status code: {response.status_code}")
        return None


def compare_products_details(product1, product2):
    """Compares product details and returns a DataFrame with matching details."""
    # Convert product details to dictionaries for easier comparison
    details1 = {detail['name']: detail['value'] for detail in product1.get('productDetails', [])}
    details2 = {detail['name']: detail['value'] for detail in product2.get('productDetails', [])}
    
    # Find common detail names
    common_names = set(details1.keys()).intersection(set(details2.keys()))
    
    # Build comparison data
    data = []
    for name in common_names:
        data.append({
            'Detail Name': name,
            'Product 1': details1[name],
            'Product 2': details2[name]
        })
        
    # Create DataFrame
    return pd.DataFrame(data)

def save_json_to_file(json_data, file_name):
    """Save JSON data to a file in the specified directory."""
    file_path = os.path.join(save_dir, file_name)
    with open(file_path, 'w') as f:
        json.dump(json_data, f)
    return file_path

# Load the LLM
llm = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE"),
        model="gpt-3.5-turbo-0125",
        temperature=0.0,
        system_prompt='''
        You are an AI model trained to assist users to compare different products''',
    )

# Initialize session state for product details and chat messages if not already present
if 'product_details_1' not in st.session_state:
    st.session_state.product_details_1 = None
if 'product_details_2' not in st.session_state:
    st.session_state.product_details_2 = None
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ask me a question about the products!"}]

# Streamlit app layout
st.set_page_config(
    page_title="CompareWise: Amazon Product Comparison Tool",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None,
)

st.title("CompareWise")
st.write("Paste Amazon product URLs to get their details.")

col1, col2 = st.columns(2)

with col1:
    product_url_1 = st.text_area("Enter first product URL", height=100, key="url1")

with col2:
    product_url_2 = st.text_area("Enter second product URL", height=100, key="url2")

if st.button("Compare Products"):
    st.session_state.product_id_1 = extract_product_id(product_url_1)
    st.session_state.product_id_2 = extract_product_id(product_url_2)
    if st.session_state.product_id_1 and st.session_state.product_id_2:
        st.session_state.product_details_1 = query_product(st.session_state.product_id_1)
        st.session_state.product_details_2 = query_product(st.session_state.product_id_2)
    else:
        st.error("Invalid product IDs. Please check the URLs and try again.")

if st.session_state.product_details_1 and st.session_state.product_details_2:
    comparison_df = compare_products_details(st.session_state.product_details_1, st.session_state.product_details_2)
    comparison_df.set_index('Detail Name', inplace=True)
    st.write("Comparison of Product Details:")
    st.dataframe(comparison_df, use_container_width=True)
    # Save your JSON responses to temporary files
    # Assuming `product_details_1` and `product_details_2` contain your JSON data
    file_path_1 = save_json_to_file(st.session_state.product_details_1, f"{st.session_state.product_id_1}.json")
    file_path_2 = save_json_to_file(st.session_state.product_details_2, f"{st.session_state.product_id_2}.json")


    # Initialize JSONQueryEngines here after confirming product details are available
    reader = SimpleDirectoryReader(input_files=["product_details_1.json", "product_details_2.json"])

    documents = reader.load_data()
    index = VectorStoreIndex.from_documents(documents)

    if "chat_engine" not in st.session_state.keys():  # Initialize the chat engine
        st.session_state.chat_engine = index.as_chat_engine(
            chat_mode="condense_question", verbose=False, llm=llm
        )

with st.sidebar:
    st.write("## Product Chat")
    if prompt := st.chat_input(
        "Your question"
    ):  # Prompt for user input and save to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

    for message in st.session_state.messages:  # Display the prior chat messages
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # If last message is not from assistant, generate a new response
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.chat_engine.stream_chat(prompt)
                st.write_stream(response.response_gen)
                message = {"role": "assistant", "content": response.response}
                st.session_state.messages.append(message)  # Add response to message history