# test_shopify_api.py
import requests
import json
from pprint import pprint
import time

def test_shopify_insights_api():
    """Test the Shopify Insights API with various stores"""
    
    # API endpoint
    api_url = "http://localhost:8000/fetch-insights"
    
    # Test stores
    test_stores = [
        "https://memy.co.in",
        "https://hairoriginals.com",
        # Add more stores as needed
    ]
    
    print("🚀 Testing Shopify Insights Fetcher API")
    print("=" * 50)
    
    for store_url in test_stores:
        print(f"\n🔍 Testing: {store_url}")
        print("-" * 30)
        
        try:
            # Make API request
            response = requests.post(
                api_url,
                json={"website_url": store_url},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Extracted insights for {data.get('brand_name', 'Unknown Brand')}")
                
                # Display summary
                print(f"📊 Summary:")
                print(f"   - Total Products: {data.get('total_products', 0)}")
                print(f"   - Hero Products: {len(data.get('hero_products', []))}")
                print(f"   - FAQs: {len(data.get('faqs', []))}")
                print(f"   - Social Handles: {len(data.get('social_handles', []))}")
                print(f"   - Contact Emails: {len(data.get('contact_info', {}).get('emails', []))}")
                print(f"   - Important Links: {len(data.get('important_links', {}))}")
                
                # Show first few products with specifications
                products = data.get('product_catalog', [])
                if products:
                    print(f"\n📦 First 3 Products:")
                    for i, product in enumerate(products[:3]):
                        print(f"   {i+1}. {product.get('title', 'N/A')} - ${product.get('price', 'N/A')}")
                        
                        # Show specifications if available
                        specs = product.get('specifications', [])
                        if specs:
                            print(f"      Specifications:")
                            for spec in specs[:3]:  # Show first 3 specs
                                print(f"        - {spec.get('attribute', 'N/A')}: {spec.get('value', 'N/A')}")
                        
                        # Show clean description
                        clean_desc = product.get('clean_description', '')
                        if clean_desc:
                            print(f"      Description: {clean_desc[:100]}...")
                
                # Show FAQs
                faqs = data.get('faqs', [])
                if faqs:
                    print(f"\n❓ Sample FAQs:")
                    for i, faq in enumerate(faqs[:2]):
                        print(f"   Q: {faq.get('question', 'N/A')}")
                        print(f"   A: {faq.get('answer', 'N/A')[:100]}...")
                
                # Show social handles
                social_handles = data.get('social_handles', [])
                if social_handles:
                    print(f"\n📱 Social Handles:")
                    for handle in social_handles:
                        print(f"   {handle.get('platform', 'N/A')}: {handle.get('handle', 'N/A')}")
                
                # Show important links
                important_links = data.get('important_links', {})
                if important_links:
                    print(f"\n🔗 Important Links:")
                    for link_type, url in important_links.items():
                        print(f"   {link_type}: {url}")
                
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            print("⏰ Request timed out")
        except requests.exceptions.ConnectionError:
            print("🚫 Connection error - is the API running?")
        except Exception as e:
            print(f"💥 Unexpected error: {e}")
        
        print("\n" + "="*50)
        time.sleep(1)  # Be respectful with requests

def test_api_health():
    """Test API health and basic endpoints"""
    print("🏥 Testing API Health")
    print("-" * 20)
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
        
        # Test root endpoint
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"💥 API health check failed: {e}")

def test_single_store_detailed():
    """Test a single store with detailed output"""
    store_url = "https://memy.co.in"
    api_url = "http://localhost:8000/fetch-insights"
    
    print(f"🔍 Detailed Test for: {store_url}")
    print("=" * 50)
    
    try:
        response = requests.post(
            api_url,
            json={"website_url": store_url},
            timeout=45
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"Brand: {data.get('brand_name', 'N/A')}")
            print(f"Description: {data.get('brand_description', 'N/A')}")
            print(f"Total Products: {data.get('total_products', 0)}")
            print(f"Extracted at: {data.get('extracted_at', 'N/A')}")
            
            # Detailed product analysis
            products = data.get('product_catalog', [])
            if products:
                print(f"\n📦 Product Analysis:")
                product_types = {}
                for product in products:
                    p_type = product.get('product_type', 'Unknown')
                    product_types[p_type] = product_types.get(p_type, 0) + 1
                
                print(f"   Product Types Distribution:")
                for p_type, count in sorted(product_types.items(), key=lambda x: x[1], reverse=True):
                    print(f"     - {p_type}: {count}")
                
                # Show product with most specifications
                product_with_specs = None
                max_specs = 0
                for product in products:
                    specs_count = len(product.get('specifications', []))
                    if specs_count > max_specs:
                        max_specs = specs_count
                        product_with_specs = product
                
                if product_with_specs and max_specs > 0:
                    print(f"\n📋 Product with Most Specifications:")
                    print(f"   Title: {product_with_specs.get('title', 'N/A')}")
                    print(f"   Price: ${product_with_specs.get('price', 'N/A')}")
                    print(f"   Specifications ({max_specs}):")
                    for spec in product_with_specs.get('specifications', []):
                        print(f"     - {spec.get('attribute', 'N/A')}: {spec.get('value', 'N/A')}")
            
            # Contact information
            contact_info = data.get('contact_info', {})
            print(f"\n📞 Contact Information:")
            print(f"   Emails: {', '.join(contact_info.get('emails', []))}")
            print(f"   Phones: {', '.join(contact_info.get('phones', []))}")
            
            # Save detailed results to file
            with open(f"insights_{store_url.replace('https://', '').replace('/', '_')}.json", 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\n💾 Detailed results saved to file")
            
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    print("🧪 Shopify Insights API Test Suite")
    print("=" * 50)
    
    # Run health check first
    test_api_health()
    
    # Run basic tests
    test_shopify_insights_api()
    
    # Run detailed test
    test_single_store_detailed()
    
    print("\n🎉 Test suite completed!")