# Shopify Store Insights Fetcher

A robust FastAPI application that extracts comprehensive insights from Shopify stores without using the official Shopify API.

## Features

### Mandatory Features ✅

- **Product Catalog**: Complete list of products from `/products.json`
- **Hero Products**: Featured products from the homepage
- **Privacy Policy**: Automatically extracted policy content
- **Return/Refund Policy**: Policy information extraction
- **FAQs**: Frequently asked questions and answers
- **Social Handles**: Instagram, Facebook, Twitter, TikTok, etc.
- **Contact Information**: Email addresses and phone numbers
- **Brand Context**: About the brand information
- **Important Links**: Order tracking, Contact Us, Blogs, etc.

### Technical Features

- **Robust Error Handling**: Proper HTTP status codes (401, 500)
- **Clean Architecture**: Modular design with separation of concerns
- **Comprehensive Logging**: Detailed logging for debugging
- **Pydantic Models**: Type validation and serialization
- **RESTful API Design**: Clean and intuitive endpoints
- **CORS Support**: Cross-origin resource sharing enabled

## Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd shopify-insights-fetcher
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env and add your Gemini API key
   ```

5. **Run the application**

   ```sh
   python main.py
   ```

The API will be available at `http://localhost:8000`

## API Documentation

### Endpoints

#### POST /fetch-insights

Extract comprehensive insights from a Shopify store.

**Request Body:**

```json
{
  "website_url": "https://example.myshopify.com"
}
```

**Response:**

```json
{
  "website_url": "https://example.myshopify.com",
  "brand_name": "Example Brand",
  "brand_description": "Brand description...",
  "product_catalog": [
    {
      "id": 123456,
      "title": "Product Name",
      "handle": "product-name",
      "description": "Product description...",
      "price": "29.99",
      "images": ["https://example.com/image.jpg"],
      "tags": ["tag1", "tag2"],
      "product_type": "Clothing",
      "vendor": "Brand Name",
      "url": "https://example.com/products/product-name"
    }
  ],
  "hero_products": [...],
  "privacy_policy": "Privacy policy content...",
  "return_refund_policy": "Return policy content...",
  "faqs": [
    {
      "question": "Do you have COD as a payment option?",
      "answer": "Yes, we do have COD available."
    }
  ],
  "social_handles": [
    {
      "platform": "instagram",
      "url": "https://instagram.com/brand",
      "handle": "brand"
    }
  ],
  "contact_info": {
    "emails": ["contact@example.com"],
    "phones": ["+1-234-567-8900"],
    "address": "123 Main St, City, State"
  },
  "important_links": {
    "Contact Us": "https://example.com/contact",
    "Order Tracking": "https://example.com/track-order",
    "Blog": "https://example.com/blog"
  },
  "extracted_at": "2024-01-15T10:30:00",
  "total_products": 50,
  "status": "success"
}
```

#### GET /

API information and usage instructions.

#### GET /health

Health check endpoint.

## Testing

### Using curl

```bash
curl -X POST "http://localhost:8000/fetch-insights" \
  -H "Content-Type: application/json" \
  -d '{"website_url": "https://memy.co.in"}'
```

### Using Python requests

```python
import requests

response = requests.post(
    "http://localhost:8000/fetch-insights",
    json={"website_url": "https://memy.co.in"}
)
print(response.json())
```

### Interactive API Documentation

Visit `http://localhost:8000/docs` for Swagger UI documentation.

## Example Shopify Stores to Test

```sh
- https://memy.co.in
- https://hairoriginals.com
- https://colourpop.com
- https://gymshark.com
- https://allbirds.com
```

## Error Handling

The API returns appropriate HTTP status codes:

- **200**: Success
- **401**: Website not found or not accessible
- **422**: Invalid request format
- **500**: Internal server error

## Architecture

```sh
FastAPI App
│
├── main.py (FastAPI entry point)
├── Pydantic Models (Request/Response validation)
├── ShopifyScraperService (Core scraping logic)
├── HTML Extraction utilities
└── Error handling & logging
```

## Key Components

### ShopifyScraperService

- **Product Extraction**: Uses `/products.json` endpoint
- **Policy Extraction**: Searches common policy page URLs
- **FAQ Parsing**: Intelligent FAQ detection and parsing
- **Social Media**: Pattern matching for social handles
- **Contact Info**: Regex-based email and phone extraction

### Robust Error Handling

- Network timeouts and retries
- Invalid URL handling
- Missing content graceful degradation
- Detailed logging for debugging

## Contributing

1. Follow PEP 8 coding standards
2. Add comprehensive error handling
3. Include logging for debugging
4. Write clean, maintainable code
5. Add type hints for all functions

## License

This project is for educational and development purposes.
