"""
Example demonstrating how to use Proxyy as a parameter with requests
"""

from proxyy import RotatingProxy, ProxyConfig
import requests


def as_parameter_example():
    """
    Demonstrates using RotatingProxy as a parameter/wrapper.
    """
    print("=== Using Proxyy as Parameter ===")
    
    # Create proxy instance
    proxy = RotatingProxy()
    
    # Option 1: Use the proxy's request methods directly
    print("\n1. Using proxy methods directly:")
    response = proxy.get("https://httpbin.org/get")
    print(f"Status: {response.status_code}")
    
    # Option 2: Get proxy settings and use with requests
    print("\n2. Getting proxy configuration:")
    # Prepare request parameters
    kwargs = proxy._prepare_request_kwargs()
    print(f"Headers: {kwargs.get('headers', {}).get('User-Agent', 'N/A')[:50]}...")
    
    # Option 3: Use session from proxy
    print("\n3. Using proxy session:")
    # The proxy has a session with connection pooling
    # You can use it directly if needed
    response = proxy.session.get(
        "https://httpbin.org/get",
        headers={"User-Agent": proxy._get_user_agent()}
    )
    print(f"Status via session: {response.status_code}")
    
    proxy.close()


def function_parameter_example():
    """
    Pass proxy to a function that makes requests.
    """
    print("\n=== Passing Proxy to Functions ===")
    
    def fetch_data(url: str, proxy: RotatingProxy):
        """
        Function that accepts a proxy as parameter.
        """
        try:
            response = proxy.get(url)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    # Create proxy
    with RotatingProxy() as proxy:
        # Pass to function
        data = fetch_data("https://httpbin.org/user-agent", proxy)
        print(f"Fetched data: {data}")
        
        # Use multiple times
        for i in range(3):
            data = fetch_data("https://httpbin.org/headers", proxy)
            ua = data.get("headers", {}).get("User-Agent", "N/A")
            print(f"Request {i + 1} UA: {ua[:60]}...")


def class_integration_example():
    """
    Integrate proxy into a class.
    """
    print("\n=== Class Integration ===")
    
    class APIClient:
        """Example API client using Proxyy."""
        
        def __init__(self, base_url: str, proxy_config: ProxyConfig = None):
            self.base_url = base_url
            self.proxy = RotatingProxy(proxy_config)
        
        def get(self, endpoint: str):
            """Make GET request to endpoint."""
            url = f"{self.base_url}{endpoint}"
            return self.proxy.get(url)
        
        def post(self, endpoint: str, **kwargs):
            """Make POST request to endpoint."""
            url = f"{self.base_url}{endpoint}"
            return self.proxy.post(url, **kwargs)
        
        def close(self):
            """Cleanup."""
            self.proxy.close()
    
    # Use the API client
    client = APIClient("https://httpbin.org")
    try:
        response = client.get("/get")
        print(f"API Response status: {response.status_code}")
        
        response = client.post("/post", json={"test": "data"})
        print(f"POST Response status: {response.status_code}")
        
        print(f"Client proxy stats: {client.proxy.get_stats()}")
    finally:
        client.close()


if __name__ == "__main__":
    as_parameter_example()
    function_parameter_example()
    class_integration_example()
    print("\n=== All parameter examples completed ===")
