# Shopify Store Insights Fetcher

A **Streamlit + FastAPI** application to extract deep insights from any Shopify store — without using the official Shopify API.

## Features

### Core Shopify Insights

- 📦 Full Product Catalog
- 🌟 Hero/Featured Products
- 📄 Privacy & Return/Refund Policies
- ❓ Auto-extracted FAQs
- 🔗 Social Media Links (Instagram, Facebook, TikTok, etc.)
- 📧 Contact Info (emails, phones, address)
- 🧠 About the Brand (brand description, context)
- 🔍 Important Links (Track Order, Blog, Contact Us, etc.)

### 🛠 Technical Stack

- [FastAPI](https://fastapi.tiangolo.com/) backend with RESTful APIs
- [Streamlit](https://streamlit.io/) for the frontend UI
- Pydantic models for request/response validation
- Structured logging and modular codebase
- Interactive API docs (Swagger UI)

---

## Streamlit UI Preview

![alt text](demo_images/image.png)

![alt text](demo_images/image-1.png)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Heisenberg208/Shopify_insights_fetcher.git
cd shopify-insights-fetcher
```

---

### 2. Set Up a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
# On Windows: 
venv\Scripts\activate       
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Run the FastAPI Backend

```bash
python main.py
```

- Swagger Docs: [http://127.1.0.0:8000/docs](http://127.1.0.0:8000/docs)

---

### 5. Run the Streamlit Frontend (UI)

```bash
streamlit run streamlit_app.py
```
