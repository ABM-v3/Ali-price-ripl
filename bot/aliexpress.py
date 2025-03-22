import logging
import aiohttp
import json
import hashlib
import time
from urllib.parse import urlencode
import asyncio

from config import ALIEXPRESS_APP_KEY, ALIEXPRESS_APP_SECRET, MAX_REQUESTS_PER_MINUTE
from bot.utils import extract_product_id

# Configure logging
logger = logging.getLogger(__name__)

# AliExpress API endpoints
ALIEXPRESS_API_URL = "https://api.aliexpress.com/rest"
AE_AFFILIATE_LINK_GENERATE = "aliexpress.affiliate.link.generate"
AE_DS_PRODUCT_GET = "aliexpress.ds.product.get"

# Rate limiting
request_timestamps = []
async def respect_rate_limit():
    """Ensure we don't exceed the rate limit."""
    global request_timestamps
    current_time = time.time()
    
    # Remove timestamps older than 60 seconds
    request_timestamps = [ts for ts in request_timestamps if current_time - ts < 60]
    
    # If we've hit the limit, wait
    if len(request_timestamps) >= MAX_REQUESTS_PER_MINUTE:
        wait_time = 60 - (current_time - request_timestamps[0])
        if wait_time > 0:
            logger.warning(f"Rate limit reached. Waiting for {wait_time:.2f} seconds")
            await asyncio.sleep(wait_time)
    
    # Add current timestamp
    request_timestamps.append(time.time())

def generate_signature(params):
    """Generate signature for AliExpress API.
    
    Args:
        params (dict): API parameters
        
    Returns:
        str: The generated signature
    """
    # Sort parameters alphabetically by key
    sorted_params = sorted(params.items())
    
    # Concatenate all parameters
    concatenated = ALIEXPRESS_APP_SECRET
    for key, value in sorted_params:
        concatenated += key + str(value)
    concatenated += ALIEXPRESS_APP_SECRET
    
    # Generate MD5 hash
    return hashlib.md5(concatenated.encode()).hexdigest().upper()

async def make_api_request(method, params):
    """Make a request to the AliExpress API.
    
    Args:
        method (str): API method name
        params (dict): API parameters
        
    Returns:
        dict: API response, or None if the request failed
    """
    # Respect rate limits
    await respect_rate_limit()
    
    # Common parameters
    common_params = {
        "app_key": ALIEXPRESS_APP_KEY,
        "method": method,
        "format": "json",
        "v": "2.0",
        "sign_method": "md5",
        "timestamp": str(int(time.time() * 1000))
    }
    
    # Merge with method-specific parameters
    all_params = {**common_params, **params}
    
    # Generate signature
    all_params["sign"] = generate_signature(all_params)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(ALIEXPRESS_API_URL, data=all_params) as response:
                if response.status != 200:
                    logger.error(f"API request failed with status {response.status}: {await response.text()}")
                    return None
                
                response_data = await response.json()
                
                # Check for API errors
                if 'error_response' in response_data:
                    error = response_data['error_response']
                    logger.error(f"API error: {error.get('code', 'Unknown')} - {error.get('msg', 'Unknown error')}")
                    return None
                
                return response_data
    
    except Exception as e:
        logger.error(f"Error making API request: {e}")
        return None

async def get_product_details(product_url):
    """Get product details from AliExpress API.
    
    Args:
        product_url (str): The AliExpress product URL
        
    Returns:
        dict: Product details, or None if the request failed
    """
    product_id = extract_product_id(product_url)
    if not product_id:
        logger.error(f"Could not extract product ID from URL: {product_url}")
        return None
    
    # Prepare API parameters
    params = {
        "product_ids": product_id,
        "ship_to_country": "US",  # Default shipping country
        "fields": "title,sale_price,original_price,discount,evaluation_rate,target_app_sale_price,target_original_price,ship_to_country,delivery_time,logistics_cost"
    }
    
    # Make API request
    response = await make_api_request(AE_DS_PRODUCT_GET, params)
    if not response:
        return None
    
    try:
        # Parse response
        result_key = f"{AE_DS_PRODUCT_GET}_response"
        if result_key not in response:
            logger.error(f"Unexpected response format: {response}")
            return None
        
        result = response[result_key]
        if 'result' not in result or not result['result']:
            logger.error(f"No results in response: {result}")
            return None
        
        products = json.loads(result['result'])
        if not products or 'products' not in products or not products['products']:
            logger.error(f"No products found: {products}")
            return None
        
        product = products['products'][0]
        
        # Extract relevant information
        price = float(product.get('target_app_sale_price', {}).get('amount', 0))
        original_price = float(product.get('target_original_price', {}).get('amount', 0))
        
        result = {
            'title': product.get('title', 'Unknown Product'),
            'price': price,
            'product_id': product_id
        }
        
        # Add optional information if available
        if original_price > 0 and original_price > price:
            result['original_price'] = original_price
        
        if 'evaluation_rate' in product:
            result['rating'] = float(product['evaluation_rate'])
        
        if 'logistics_cost' in product:
            shipping_cost = float(product.get('logistics_cost', {}).get('amount', 0))
            result['shipping_cost'] = shipping_cost
        
        return result
    
    except Exception as e:
        logger.error(f"Error parsing product details: {e}")
        return None

async def convert_to_affiliate_link(product_url):
    """Convert a regular AliExpress link to an affiliate link.
    
    Args:
        product_url (str): The AliExpress product URL
        
    Returns:
        str: The affiliate link, or the original URL if conversion failed
    """
    # Prepare API parameters
    params = {
        "source": "aliexpress",
        "app_signature": "alibestprice",
        "tracking_id": "alibestprice",
        "urls": product_url
    }
    
    # Make API request
    response = await make_api_request(AE_AFFILIATE_LINK_GENERATE, params)
    if not response:
        logger.warning(f"Failed to generate affiliate link. Returning original URL: {product_url}")
        return product_url
    
    try:
        # Parse response
        result_key = f"{AE_AFFILIATE_LINK_GENERATE}_response"
        if result_key not in response:
            logger.error(f"Unexpected response format: {response}")
            return product_url
        
        result = response[result_key]
        if 'result' not in result or not result['result']:
            logger.error(f"No results in response: {result}")
            return product_url
        
        links = json.loads(result['result'])
        if not links or 'promotion_links' not in links or not links['promotion_links']:
            logger.error(f"No promotion links found: {links}")
            return product_url
        
        # Return the first promotion link
        promotion_link = links['promotion_links'][0].get('promotion_link')
        if promotion_link:
            return promotion_link
        
        return product_url
    
    except Exception as e:
        logger.error(f"Error parsing affiliate link response: {e}")
        return product_url
