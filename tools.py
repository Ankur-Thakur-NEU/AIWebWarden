import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import time
import random
from urllib.parse import urljoin, urlparse

def web_search(query, max_results=5):
    """Search the web for a query and return top results."""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=max_results)]
        
        if not results:
            return "No search results found for the query."
        
        formatted_results = []
        for r in results:
            formatted_results.append(
                f"Title: {r.get('title', 'No title')}\n"
                f"Link: {r.get('href', 'No link')}\n"
                f"Snippet: {r.get('body', 'No snippet')}\n"
                f"{'='*50}"
            )
        
        return "\n".join(formatted_results)
    
    except Exception as e:
        return f"Error during web search: {str(e)}"

def scrape_url(url, max_chars=2000):
    """Scrape and extract text from a URL with robust error handling."""
    try:
        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return f"Invalid URL format: {url}"
        
        # Set up headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Add random delay to be respectful
        time.sleep(random.uniform(0.5, 1.5))
        
        # Make request with timeout
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Extract text from paragraphs, headings, and list items
        text_elements = []
        
        # Get main content elements
        for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'div']):
            text = tag.get_text(strip=True)
            if text and len(text) > 20:  # Filter out very short text
                text_elements.append(text)
        
        # Join and clean text
        full_text = ' '.join(text_elements)
        
        # Clean up whitespace
        full_text = ' '.join(full_text.split())
        
        # Limit length
        if len(full_text) > max_chars:
            full_text = full_text[:max_chars] + "... [Content truncated]"
        
        if not full_text.strip():
            return f"No readable content found at {url}"
        
        return full_text
    
    except requests.exceptions.Timeout:
        return f"Timeout error when accessing {url}"
    except requests.exceptions.ConnectionError:
        return f"Connection error when accessing {url}"
    except requests.exceptions.HTTPError as e:
        return f"HTTP error {e.response.status_code} when accessing {url}"
    except requests.exceptions.RequestException as e:
        return f"Request error when accessing {url}: {str(e)}"
    except Exception as e:
        return f"Error scraping {url}: {str(e)}"

def search_and_scrape(query, max_results=3, scrape_top_n=2):
    """Combined function to search and scrape top results."""
    try:
        print(f"🔍 Searching for: {query}")
        
        # First, search the web
        with DDGS() as ddgs:
            search_results = [r for r in ddgs.text(query, max_results=max_results)]
        
        if not search_results:
            return "No search results found for the query."
        
        combined_info = []
        combined_info.append(f"Search Query: {query}")
        combined_info.append("="*60)
        
        # Process each search result
        for i, result in enumerate(search_results, 1):
            title = result.get('title', 'No title')
            url = result.get('href', 'No URL')
            snippet = result.get('body', 'No snippet')
            
            combined_info.append(f"\n{i}. {title}")
            combined_info.append(f"URL: {url}")
            combined_info.append(f"Snippet: {snippet}")
            
            # Scrape content from top results
            if i <= scrape_top_n:
                print(f"📄 Scraping content from result {i}...")
                scraped_content = scrape_url(url, max_chars=1000)
                combined_info.append(f"Full Content: {scraped_content}")
            
            combined_info.append("-" * 50)
        
        return "\n".join(combined_info)
    
    except Exception as e:
        return f"Error in search_and_scrape: {str(e)}"

def get_available_tools():
    """Return a list of available tools and their descriptions."""
    tools = {
        "web_search": {
            "description": "Search the web for a query and return top results with titles, links, and snippets",
            "parameters": ["query", "max_results (optional, default=5)"],
            "example": "web_search('best laptops 2024')"
        },
        "scrape_url": {
            "description": "Extract and return text content from a specific URL",
            "parameters": ["url", "max_chars (optional, default=2000)"],
            "example": "scrape_url('https://example.com')"
        },
        "search_and_scrape": {
            "description": "Search the web and automatically scrape content from top results",
            "parameters": ["query", "max_results (optional, default=3)", "scrape_top_n (optional, default=2)"],
            "example": "search_and_scrape('Python machine learning tutorials')"
        }
    }
    return tools

# Test functions
if __name__ == "__main__":
    print("🧪 Testing web search tools...")
    
    # Test web search
    print("\n1. Testing web_search:")
    search_result = web_search("Python programming", max_results=3)
    print(search_result[:500] + "..." if len(search_result) > 500 else search_result)
    
    # Test URL scraping (using a reliable test URL)
    print("\n2. Testing scrape_url:")
    scrape_result = scrape_url("https://httpbin.org/html", max_chars=500)
    print(scrape_result)
    
    # Test combined search and scrape
    print("\n3. Testing search_and_scrape:")
    combined_result = search_and_scrape("what is artificial intelligence", max_results=2, scrape_top_n=1)
    print(combined_result[:800] + "..." if len(combined_result) > 800 else combined_result)