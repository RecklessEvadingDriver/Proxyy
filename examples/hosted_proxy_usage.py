"""
Example: Using the hosted Proxyy server to make requests
"""

import requests
import time


def basic_usage():
    """
    Basic usage of hosted proxy server.
    """
    print("=== Basic Usage of Hosted Proxy ===\n")
    
    # Proxy server URL (assumes server is running on localhost:8080)
    PROXY_URL = "http://localhost:8080"
    
    # Method 1: Direct URL routing through proxy
    print("Method 1: Direct URL routing")
    target_url = "http://httpbin.org/user-agent"
    response = requests.get(f"{PROXY_URL}/{target_url}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # Method 2: Using as standard HTTP proxy
    print("Method 2: Using as standard proxy")
    proxies = {
        'http': PROXY_URL,
        'https': PROXY_URL,
    }
    response = requests.get("http://httpbin.org/headers", proxies=proxies)
    print(f"Status: {response.status_code}")
    print(f"Headers: {response.json()['headers']}")
    print()


def health_check():
    """
    Check proxy server health.
    """
    print("=== Health Check ===\n")
    
    PROXY_URL = "http://localhost:8080"
    
    response = requests.get(f"{PROXY_URL}/health")
    print(f"Health Status: {response.json()}")
    print()


def get_stats():
    """
    Get proxy server statistics.
    """
    print("=== Server Statistics ===\n")
    
    PROXY_URL = "http://localhost:8080"
    
    response = requests.get(f"{PROXY_URL}/stats")
    stats = response.json()
    
    print("Server Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()


def multiple_requests():
    """
    Make multiple requests to see rotation in action.
    """
    print("=== Multiple Requests (Rotation Demo) ===\n")
    
    PROXY_URL = "http://localhost:8080"
    
    print("Making 5 requests to observe user-agent rotation:")
    for i in range(5):
        target_url = "http://httpbin.org/user-agent"
        response = requests.get(f"{PROXY_URL}/{target_url}")
        
        if response.status_code == 200:
            ua = response.json().get('user-agent', 'N/A')
            print(f"Request {i+1}: {ua[:70]}...")
        else:
            print(f"Request {i+1}: Failed with status {response.status_code}")
        
        time.sleep(0.5)
    print()


def post_request():
    """
    Make POST request through proxy.
    """
    print("=== POST Request ===\n")
    
    PROXY_URL = "http://localhost:8080"
    target_url = "http://httpbin.org/post"
    
    data = {
        "name": "Test User",
        "action": "POST through Proxyy",
        "timestamp": time.time()
    }
    
    response = requests.post(
        f"{PROXY_URL}/{target_url}",
        json=data
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Posted data: {result['json']}")
    print()


def error_handling():
    """
    Demonstrate error handling.
    """
    print("=== Error Handling ===\n")
    
    PROXY_URL = "http://localhost:8080"
    
    # Test invalid URL
    print("Test 1: Invalid URL format")
    try:
        response = requests.get(f"{PROXY_URL}/invalid-url")
        print(f"Status: {response.status_code}")
        print(f"Error: {response.json()}")
    except Exception as e:
        print(f"Exception: {e}")
    print()
    
    # Test unreachable host
    print("Test 2: Unreachable target")
    try:
        response = requests.get(
            f"{PROXY_URL}/http://nonexistent-domain-12345.com",
            timeout=5
        )
        print(f"Status: {response.status_code}")
    except Exception as e:
        print(f"Exception (expected): {type(e).__name__}")
    print()


def integration_example():
    """
    Complete integration example.
    """
    print("=== Complete Integration Example ===\n")
    
    class APIClient:
        """API client that uses the hosted proxy."""
        
        def __init__(self, proxy_url: str = "http://localhost:8080"):
            self.proxy_url = proxy_url
            self.session = requests.Session()
        
        def get(self, url: str):
            """Make GET request through proxy."""
            return self.session.get(f"{self.proxy_url}/{url}")
        
        def post(self, url: str, **kwargs):
            """Make POST request through proxy."""
            return self.session.post(f"{self.proxy_url}/{url}", **kwargs)
        
        def health_check(self):
            """Check proxy health."""
            response = self.session.get(f"{self.proxy_url}/health")
            return response.json()
        
        def get_stats(self):
            """Get proxy stats."""
            response = self.session.get(f"{self.proxy_url}/stats")
            return response.json()
    
    # Use the client
    client = APIClient()
    
    # Check health
    health = client.health_check()
    print(f"Proxy health: {health['status']}")
    
    # Get stats
    stats = client.get_stats()
    print(f"User-agents available: {stats.get('total_user_agents', 'N/A')}")
    
    # Make a request
    response = client.get("http://httpbin.org/get")
    print(f"Request status: {response.status_code}")
    
    print("\n✓ Integration example complete!")


def usage_instructions():
    """
    Print usage instructions.
    """
    print("\n" + "=" * 70)
    print("HOW TO USE THE HOSTED PROXY")
    print("=" * 70)
    print("""
1. Start the proxy server:
   python start_server.py --free-proxies

2. Make requests through the proxy:
   
   a) Direct URL routing:
      http://localhost:8080/http://target-url
      
   b) Standard proxy configuration:
      proxies = {'http': 'http://localhost:8080', 'https': 'http://localhost:8080'}
      requests.get(url, proxies=proxies)

3. Special endpoints:
   - Health check: http://localhost:8080/health
   - Statistics: http://localhost:8080/stats

4. From any programming language:
   - curl: curl http://localhost:8080/http://httpbin.org/ip
   - Python: requests.get('http://localhost:8080/http://example.com')
   - Node.js: axios.get('http://localhost:8080/http://example.com')
   - Any HTTP client that supports proxies

5. Deploy to cloud:
   - Deploy on Heroku, AWS, Google Cloud, etc.
   - Access from anywhere: http://your-domain.com/http://target-url
    """)
    print("=" * 70)


if __name__ == "__main__":
    print("=" * 70)
    print("HOSTED PROXY USAGE EXAMPLES")
    print("=" * 70)
    print("\nNOTE: These examples require the proxy server to be running.")
    print("Start server: python start_server.py")
    print("=" * 70)
    print()
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8080/health", timeout=2)
        if response.status_code == 200:
            print("✓ Proxy server is running!\n")
            
            # Run examples
            health_check()
            get_stats()
            basic_usage()
            multiple_requests()
            post_request()
            error_handling()
            integration_example()
        else:
            print("⚠ Server responded but with unexpected status")
    except requests.exceptions.RequestException:
        print("✗ Proxy server is not running!")
        print("\nTo run these examples:")
        print("1. Start server: python start_server.py --free-proxies")
        print("2. Run this script again: python examples/hosted_proxy_usage.py")
    
    usage_instructions()
