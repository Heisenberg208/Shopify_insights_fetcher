from fastapi import  HTTPException
from typing import List, Optional, Dict, Any
import requests
from bs4 import BeautifulSoup
import json
import re
from utils.logger import logger
from urllib.parse import urljoin, urlparse
import google.generativeai as genai

from datetime import datetime

from models.insights_models import FAQ, BrandInsights, ContactInfo, Product, SocialHandle


class ShopifyScraperService:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        })

        self.gemini_model = genai.GenerativeModel('gemini-pro')
    
    def extract_insights(self, website_url: str) -> BrandInsights:
        """Main method to extract all insights from a Shopify store"""
        try:
            base_url = self._normalize_url(website_url)
            
            # Initialize insights object
            insights = BrandInsights(
                website_url=website_url,
                extracted_at=datetime.now().isoformat()
            )
            
            # Extract basic info and home page content
            home_soup = self._get_page_soup(base_url)
            if not home_soup:
                raise HTTPException(status_code=401, detail="Website not found or not accessible")
            
            # Extract brand name and description
            insights.brand_name = self._extract_brand_name(home_soup, base_url)
            insights.brand_description = self._extract_brand_description(home_soup)
            
            # Extract product catalog
            insights.product_catalog = self._extract_product_catalog(base_url)
            insights.total_products = len(insights.product_catalog)
            
            # Extract hero products from home page
            insights.hero_products = self._extract_hero_products(home_soup, base_url)
            
            # Extract policies
            insights.privacy_policy = self._extract_policy(base_url, "privacy")
            insights.return_refund_policy = self._extract_policy(base_url, "refund")
            
            # Extract FAQs
            insights.faqs = self._extract_faqs(base_url, home_soup)
            
            # Extract social handles
            insights.social_handles = self._extract_social_handles(home_soup)
            
            # Extract contact information
            insights.contact_info = self._extract_contact_info(home_soup, base_url)
            
            # Extract important links
            insights.important_links = self._extract_important_links(home_soup, base_url)
            
            return insights
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while scraping {website_url}: {e}")
            raise HTTPException(status_code=401, detail="Website not found or not accessible")
        except Exception as e:
            logger.error(f"Internal error while scraping {website_url}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error occurred")
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL to ensure proper format"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url.rstrip('/')
    
    def _get_page_soup(self, url: str) -> Optional[BeautifulSoup]:
        """Get BeautifulSoup object for a given URL"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return None
    
    def _extract_brand_name(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Extract brand name from various sources"""
        # Try title tag
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
            if title and title.lower() not in ['home', 'homepage']:
                return title.split(' - ')[0].split(' | ')[0]
        
        # Try logo alt text
        logo = soup.find('img', class_=re.compile(r'logo', re.I))
        if logo and logo.get('alt'):
            return logo['alt']
        
        # Try site name meta tag
        site_name = soup.find('meta', property='og:site_name')
        if site_name:
            return site_name.get('content')
        
        # Fallback to domain name
        domain = urlparse(base_url).netloc
        return domain.replace('www.', '').split('.')[0].title()

    def clean_html_description(html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator="\n")
        return re.sub(r'\n{2,}', '\n\n', text.strip())

    def _extract_brand_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract brand description from meta tags or content"""
        # Try meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content')
        
        # Try og:description
        og_desc = soup.find('meta', property='og:description')
        if og_desc:
            return og_desc.get('content')
        
        # Try to find about section
        about_section = soup.find(['section', 'div'], class_=re.compile(r'about|story|brand', re.I))
        if about_section:
            text = about_section.get_text().strip()
            if len(text) > 50:
                return text[:500] + "..." if len(text) > 500 else text
        
        return None
    
    def _extract_product_catalog(self, base_url: str) -> List[Product]:
        """Extract product catalog from /products.json"""
        products = []
        try:
            products_url = urljoin(base_url, '/products.json')
            response = self.session.get(products_url, timeout=10)
            response.raise_for_status()
            
            products_data = response.json()
            
            for product_data in products_data.get('products', []):
                # Extract images
                images = []
                for image in product_data.get('images', []):
                    if isinstance(image, dict) and 'src' in image:
                        images.append(image['src'])
                    elif isinstance(image, str):
                        images.append(image)
                
                # Extract price from variants
                price = None
                if product_data.get('variants'):
                    first_variant = product_data['variants'][0]
                    price = first_variant.get('price', 'N/A')
                
                product = Product(
                    id=product_data.get('id'),
                    title=product_data.get('title', ''),
                    handle=product_data.get('handle', ''),
                    description=BeautifulSoup(product_data.get('body_html', ''), 'html.parser').get_text(separator=' ').strip(),
                    price=price,
                    images=images,
                    tags=product_data.get('tags', []),
                    product_type=product_data.get('product_type'),
                    vendor=product_data.get('vendor'),
                    url=urljoin(base_url, f"/products/{product_data.get('handle', '')}")
                )
                products.append(product)
                
        except Exception as e:
            logger.warning(f"Failed to extract product catalog: {e}")
        
        return products
    
    def _extract_hero_products(self, soup: BeautifulSoup, base_url: str) -> List[Product]:
        """Extract hero/featured products from home page"""
        hero_products = []
        
        # Look for product links on homepage
        product_links = soup.find_all('a', href=re.compile(r'/products/'))
        
        for link in product_links[:6]:  # Limit to first 6 products
            href = link.get('href')
            if href:
                title = link.get_text().strip()
                if not title:
                    img = link.find('img')
                    if img:
                        title = img.get('alt', '')
                
                if title:
                    product = Product(
                        title=title,
                        handle=href.split('/')[-1],
                        url=urljoin(base_url, href)
                    )
                    hero_products.append(product)
        
        return hero_products
    def _discover_policy_links(self, soup: BeautifulSoup, keywords: List[str]) -> List[str]:
      """Discover links with relevant keywords from the homepage"""
      urls = []
      for link in soup.find_all('a', href=True):
          href = link['href']
          if any(keyword in href.lower() for keyword in keywords):
              urls.append(href)
      return urls

    
    def _extract_policy(self, base_url: str, policy_type: str) -> Optional[str]:
      keywords_map = {
          'privacy': ['privacy'],
          'refund': ['refund', 'return']
      }
      keywords = keywords_map.get(policy_type, [])
      homepage_soup = self._get_page_soup(base_url)
      candidate_links = self._discover_policy_links(homepage_soup, keywords)

      for href in candidate_links:
          policy_url = urljoin(base_url, href)
          soup = self._get_page_soup(policy_url)
          if soup:
              content = soup.find(['main', 'article', 'div'], class_=re.compile(r'content|policy|page', re.I))
              if content:
                  text = content.get_text().strip()
                  if len(text) > 100:
                      return text[:1000] + "..." if len(text) > 1000 else text
      return None

    
    def _extract_faqs(self, base_url: str, home_soup: BeautifulSoup) -> List[FAQ]:
        """Extract FAQs from the website"""
        faqs = []
        
        # Try different FAQ page URLs
        faq_urls = ['/pages/faq', '/pages/faqs', '/faq', '/faqs', '/pages/frequently-asked-questions']
        
        for url_path in faq_urls:
            try:
                faq_url = urljoin(base_url, url_path)
                soup = self._get_page_soup(faq_url)
                if soup:
                    faqs = self._parse_faqs_from_page(soup)
                    if faqs:
                        break
            except Exception as e:
                logger.warning(f"Failed to extract FAQs from {url_path}: {e}")
        
        # If no FAQs found, try home page
        if not faqs:
            faqs = self._parse_faqs_from_page(home_soup)
        
        return faqs
    
    def _parse_faqs_from_page(self, soup: BeautifulSoup) -> List[FAQ]:
        """Parse FAQs from a page"""
        faqs = []
        
        # Look for FAQ sections
        faq_sections = soup.find_all(['div', 'section'], class_=re.compile(r'faq|question|accordion', re.I))
        
        for section in faq_sections:
            # Look for question-answer pairs
            questions = section.find_all(['h3', 'h4', 'h5', 'dt', 'div'], class_=re.compile(r'question|title|header', re.I))
            
            for question in questions:
                q_text = question.get_text().strip()
                if q_text and len(q_text) > 10:
                    # Find corresponding answer
                    answer = question.find_next_sibling(['p', 'div', 'dd'])
                    if answer:
                        a_text = answer.get_text().strip()
                        if a_text:
                            faqs.append(FAQ(question=q_text, answer=a_text))
        
        return faqs[:10]  # Limit to 10 FAQs
    
    def _extract_social_handles(self, soup: BeautifulSoup) -> List[SocialHandle]:
        """Extract social media handles"""
        social_handles = []
        
        # Common social media patterns
        social_patterns = {
            'instagram': r'instagram\.com/([^/\s]+)',
            'facebook': r'facebook\.com/([^/\s]+)',
            'twitter': r'twitter\.com/([^/\s]+)',
            'tiktok': r'tiktok\.com/@([^/\s]+)',
            'youtube': r'youtube\.com/([^/\s]+)',
            'linkedin': r'linkedin\.com/company/([^/\s]+)'
        }
        
        # Find all links
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            for platform, pattern in social_patterns.items():
                match = re.search(pattern, href, re.I)
                if match:
                    handle = match.group(1)
                    social_handles.append(SocialHandle(
                        platform=platform,
                        url=href,
                        handle=handle
                    ))
        
        # Remove duplicates
        seen = set()
        unique_handles = []
        for handle in social_handles:
            if handle.platform not in seen:
                seen.add(handle.platform)
                unique_handles.append(handle)
        
        return unique_handles
    
    def _extract_contact_info(self, soup: BeautifulSoup, base_url: str) -> ContactInfo:
        """Extract contact information"""
        contact_info = ContactInfo()
        
        # Extract from main page
        page_text = soup.get_text()
        
        # Email patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, page_text)
        contact_info.emails = list(set(emails))
        
        # Phone patterns
        phone_pattern = r'(\+?1?[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, page_text)
        contact_info.phones = [''.join(phone).strip() for phone in phones if phone]
        
        # Try contact page
        try:
            contact_url = urljoin(base_url, '/pages/contact')
            contact_soup = self._get_page_soup(contact_url)
            if contact_soup:
                contact_text = contact_soup.get_text()
                additional_emails = re.findall(email_pattern, contact_text)
                contact_info.emails.extend(additional_emails)
                contact_info.emails = list(set(contact_info.emails))
        except Exception as e:
            logger.warning(f"Failed to extract contact info: {e}")
        
        return contact_info
    
    def _extract_important_links(self, soup: BeautifulSoup, base_url: str) -> Dict[str, str]:
        """Extract important links"""
        important_links = {}
        
        # Common important link patterns
        link_patterns = {
            'Order Tracking': ['/pages/track-order', '/track-order', '/track', '/order-tracking'],
            'Contact Us': ['/pages/contact', '/contact', '/contact-us'],
            'About Us': ['/pages/about', '/about', '/about-us'],
            'Blog': ['/blogs', '/blog', '/news'],
            'Shipping': ['/pages/shipping', '/shipping', '/shipping-policy'],
            'Size Guide': ['/pages/size-guide', '/size-guide', '/sizing'],
            'Customer Service': ['/pages/customer-service', '/customer-service', '/support']
        }
        
        # Find all links
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            link_text = link.get_text().strip().lower()
            
            # Check against patterns
            for category, patterns in link_patterns.items():
                if any(pattern in href.lower() for pattern in patterns) or any(pattern.replace('/', '').replace('-', ' ') in link_text for pattern in patterns):
                    important_links[category] = urljoin(base_url, href)
                    break
        
        return important_links