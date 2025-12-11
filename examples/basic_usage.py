"""
Basic usage example of the Proxyy library
"""

from proxyy import RotatingProxy, ProxyConfig, ProxyInfo


def basic_example():
    """Simple example with user-agent rotation only."""
    print("=== Basic Example: User-Agent Rotation ===")
    
    # Create a proxy with default settings (user-agent rotation enabled)
    proxy = RotatingProxy()
    
    # Make a request
    try:
        response = proxy.get("https://httpbin.org/user-agent")
        print(f"Status: {response.status_code}")
        print(f"User-Agent: {response.json()}")
        
        # Make another request with a different user-agent
        response = proxy.get("https://httpbin.org/user-agent")
        print(f"Second request User-Agent: {response.json()}")
        
        # Get stats
        print(f"\nStats: {proxy.get_stats()}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        proxy.close()


def advanced_example():
    """Advanced example with custom configuration."""
    print("\n=== Advanced Example: Custom Configuration ===")
    
    # Create custom configuration
    config = ProxyConfig(
        rotate_user_agent=True,
        rotate_ip=False,  # No IP rotation in this example
        rotation_strategy="round-robin",  # or "random"
        verify_ssl=True,
        timeout=15,
        max_retries=2,
        rate_limit=1.0,  # 1 request per second
    )
    
    # Use as context manager for automatic cleanup
    with RotatingProxy(config) as proxy:
        try:
            # Make multiple requests
            for i in range(3):
                print(f"\nRequest {i + 1}:")
                response = proxy.get("https://httpbin.org/headers")
                headers = response.json()["headers"]
                print(f"User-Agent: {headers.get('User-Agent', 'N/A')}")
        except Exception as e:
            print(f"Error: {e}")


def proxy_rotation_example():
    """Example with IP/proxy rotation."""
    print("\n=== Proxy Rotation Example ===")
    
    # Define proxy backends (replace with your actual proxies)
    proxies = [
        ProxyInfo(host="proxy1.example.com", port=8080, protocol="http"),
        ProxyInfo(host="proxy2.example.com", port=8080, protocol="http"),
        # Add authentication if needed
        ProxyInfo(
            host="proxy3.example.com",
            port=8080,
            protocol="http",
            username="user",
            password="pass"
        ),
    ]
    
    # Create configuration with proxy rotation
    config = ProxyConfig(
        rotate_user_agent=True,
        rotate_ip=True,
        rotation_strategy="random",
        proxies=proxies,
        max_retries=3,
    )
    
    with RotatingProxy(config) as proxy:
        try:
            # This would rotate through the proxy list
            response = proxy.get("https://httpbin.org/ip")
            print(f"Response: {response.json()}")
            
            print(f"\nStats: {proxy.get_stats()}")
        except Exception as e:
            print(f"Error: {e}")
            print("Note: This example requires valid proxy servers")


def post_request_example():
    """Example of making POST requests."""
    print("\n=== POST Request Example ===")
    
    with RotatingProxy() as proxy:
        try:
            data = {"key": "value", "name": "test"}
            response = proxy.post("https://httpbin.org/post", json=data)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    basic_example()
    advanced_example()
    # proxy_rotation_example()  # Uncomment if you have valid proxies
    post_request_example()
    print("\n=== All examples completed ===")
