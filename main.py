# main.py
from fastapi import FastAPI, HTTPException
from services.scrapper import ShopifyScraperService
from utils.logger import logger
from urllib.parse import urljoin, urlparse
import google.generativeai as genai
import os
from datetime import datetime

from models.insights_models import  BrandInsights, InsightsRequest


# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI(
    title="Shopify Store Insights Fetcher",
    description="Fetch comprehensive insights from Shopify stores",
    version="1.0.0"
)

scraper_service = ShopifyScraperService()

@app.post("/fetch-insights", response_model=BrandInsights)
async def fetch_insights(request: InsightsRequest):
    """
    Fetch comprehensive insights from a Shopify store
    """
    try:
        insights = scraper_service.extract_insights(str(request.website_url))
        return insights
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error occurred")

@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "Shopify Store Insights Fetcher API",
        "version": "1.0.0",
        "endpoints": {
            "POST /fetch-insights": "Fetch insights from a Shopify store",
            "GET /": "API information"
        },
        "usage": {
            "endpoint": "/fetch-insights",
            "method": "POST",
            "body": {
                "website_url": "https://example.myshopify.com"
            }
        }
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.1.0.0", port=8000)