from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any


# Pydantic Models
class Product(BaseModel):
    id: Optional[int] = None
    title: str
    handle: str
    description: Optional[str] = None
    price: Optional[str] = None
    images: List[str] = []
    tags: List[str] = []
    product_type: Optional[str] = None
    vendor: Optional[str] = None
    url: Optional[str] = None

class FAQ(BaseModel):
    question: str
    answer: str

class SocialHandle(BaseModel):
    platform: str
    url: str
    handle: Optional[str] = None

class ContactInfo(BaseModel):
    emails: List[str] = []
    phones: List[str] = []
    address: Optional[str] = None

class BrandInsights(BaseModel):
    website_url: str
    brand_name: Optional[str] = None
    brand_description: Optional[str] = None
    product_catalog: List[Product] = []
    hero_products: List[Product] = []
    privacy_policy: Optional[str] = None
    return_refund_policy: Optional[str] = None
    faqs: List[FAQ] = []
    social_handles: List[SocialHandle] = []
    contact_info: ContactInfo = ContactInfo()
    important_links: Dict[str, str] = {}
    extracted_at: str
    total_products: int = 0
    status: str = "success"

class InsightsRequest(BaseModel):
    website_url: HttpUrl