import streamlit as st
import httpx

API_URL = "http://127.1.0.0:8000/api/v1/fetch/insights"

# Page configuration
st.set_page_config(
    page_title="Shopify Insights Fetcher",
    page_icon="🛍️",
    layout="centered",
    initial_sidebar_state="collapsed",
)


st.markdown("""
    <style>
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 8px;
            margin-top: 10px;
        }
        .stButton>button:hover {
            background-color: #45a049;
            color: white;
        }
        .stTextInput>div>div>input {
            padding: 10px;
            border-radius: 6px;
        }
        .stMarkdown {
            font-size: 17px;
        }
        pre {
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🔍 Shopify Store Insights</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Instantly extract insights from any Shopify store</p>", unsafe_allow_html=True)
st.markdown("---")

# Input field
shop_url = st.text_input("🔗 Enter Shopify Store URL", "https://example.myshopify.com")


if st.button(" Fetch Insights"):
    with st.spinner(" Fetching insights from the store..."):
        try:
            response = httpx.post(API_URL, json={"website_url": shop_url}, timeout=30)
            response.raise_for_status()
            insights = response.json()
            st.success(" Insights fetched successfully!")
            st.markdown("### 🧠 Insights:")
            st.json(insights)
        except httpx.HTTPStatusError as e:
            st.error(f" HTTP error {e.response.status_code}:\n{e.response.text}")
        except Exception as e:
            st.error(f" Unexpected error: {e}")


st.markdown("---")
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.markdown("Need API reference?")
with col2:
    if st.button("📄 Open API Docs"):
        st.markdown("[Click here to open Swagger UI](http://127.1.0.0:8000/docs)", unsafe_allow_html=True)
