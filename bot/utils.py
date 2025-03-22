import re
import logging
from urllib.parse import urlparse, parse_qs

# Configure logging
logger = logging.getLogger(__name__)

# Regular expressions for AliExpress links
ALIEXPRESS_LINK_PATTERNS = [
    r'https?://(?:www\.)?(?:aliexpress\.com|(?:[a-z]{2}\.)?aliexpress\.com)/item/[\d\w]+\.html',
    r'https?://(?:www\.)?(?:aliexpress\.com|(?:[a-z]{2}\.)?aliexpress\.com)/\d+/\d+\.html',
    r'https?://(?:s\.)?click\.aliexpress\.com/[^\s]+',
    r'https?://(?:www\.)?aliexpress\.ru/item/[\d\w]+\.html'
]

def extract_aliexpress_links(text):
    """Extract AliExpress product links from text.
    
    Args:
        text (str): The text to extract links from
        
    Returns:
        list: A list of extracted AliExpress links
    """
    if not text:
        return []
    
    links = []
    for pattern in ALIEXPRESS_LINK_PATTERNS:
        matches = re.findall(pattern, text)
        links.extend(matches)
    
    return links

def is_valid_aliexpress_link(link):
    """Check if a link is a valid AliExpress product link.
    
    Args:
        link (str): The link to check
        
    Returns:
        bool: True if the link is valid, False otherwise
    """
    for pattern in ALIEXPRESS_LINK_PATTERNS:
        if re.match(pattern, link):
            return True
    return False

def extract_product_id(link):
    """Extract product ID from an AliExpress link.
    
    Args:
        link (str): The AliExpress link
        
    Returns:
        str: The product ID, or None if it couldn't be extracted
    """
    try:
        # Parse the URL
        parsed_url = urlparse(link)
        
        # Handle different AliExpress URL formats
        if 'item' in parsed_url.path:
            # Format: https://www.aliexpress.com/item/1234567890.html
            product_id = parsed_url.path.split('/item/')[1].split('.')[0]
            return product_id
        elif parsed_url.netloc == 's.click.aliexpress.com':
            # This is a redirected link, we need to follow it to get the actual product ID
            logger.warning("Redirected AliExpress link detected. Product ID extraction might be imprecise.")
            # Try to extract from query parameters
            query_params = parse_qs(parsed_url.query)
            if 'dl_target_url' in query_params:
                target_url = query_params['dl_target_url'][0]
                return extract_product_id(target_url)
        elif len(parsed_url.path.split('/')) >= 3:
            # Format: https://www.aliexpress.com/1234/1234567890.html
            segments = parsed_url.path.strip('/').split('/')
            if len(segments) >= 2 and segments[1].endswith('.html'):
                return segments[1].split('.')[0]
        
        logger.warning(f"Could not extract product ID from link: {link}")
        return None
    
    except Exception as e:
        logger.error(f"Error extracting product ID from link {link}: {e}")
        return None

def format_price(price):
    """Format a price value for display.
    
    Args:
        price (float): The price value
        
    Returns:
        str: The formatted price
    """
    return f"{price:.2f}"

def sanitize_product_title(title):
    """Sanitize a product title for display.
    
    Args:
        title (str): The product title
        
    Returns:
        str: The sanitized title
    """
    if not title:
        return "Unknown Product"
    
    # Limit the title length
    if len(title) > 100:
        title = title[:97] + "..."
    
    return title
