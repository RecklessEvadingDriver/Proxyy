"""
Example demonstrating usage of free proxies from the internet
"""

from proxyy import RotatingProxy, ProxyConfig, get_free_proxies, FreeProxyFetcher


def basic_free_proxy_example():
    """
    Simple example: Fetch free proxies and use them.
    """
    print("=== Basic Free Proxy Example ===\n")
    
    # Fetch free proxies (without testing - faster but some may not work)
    print("Fetching free proxies from the internet...")
    proxies = get_free_proxies(max_proxies=20, test_proxies=False)
    
    print(f"✓ Fetched {len(proxies)} free proxies")
    
    # Show some examples
    print("\nSample proxies:")
    for i, proxy in enumerate(proxies[:5], 1):
        print(f"  {i}. {proxy.host}:{proxy.port}")
    
    # Create configuration with free proxies
    config = ProxyConfig(
        rotate_user_agent=True,
        rotate_ip=True,
        rotation_strategy="random",
        proxies=proxies,
        max_retries=3,
    )
    
    # Use the proxy
    with RotatingProxy(config) as proxy:
        stats = proxy.get_stats()
        print(f"\n✓ Proxy initialized with stats: {stats}")


def tested_free_proxy_example():
    """
    Example: Fetch and test free proxies before use (slower but more reliable).
    """
    print("\n=== Tested Free Proxy Example ===\n")
    
    print("Fetching and testing free proxies (this may take a while)...")
    proxies = get_free_proxies(max_proxies=10, test_proxies=True)
    
    print(f"✓ Found {len(proxies)} working proxies")
    
    if proxies:
        # Show working proxies
        print("\nWorking proxies:")
        for i, proxy in enumerate(proxies, 1):
            print(f"  {i}. {proxy.host}:{proxy.port}")
        
        # Create configuration
        config = ProxyConfig(
            rotate_user_agent=True,
            rotate_ip=True,
            rotation_strategy="round-robin",
            proxies=proxies,
            max_retries=2,
        )
        
        with RotatingProxy(config) as proxy:
            print(f"\n✓ Proxy ready with {len(proxies)} working proxies")
            print(f"Stats: {proxy.get_stats()}")
    else:
        print("⚠ No working proxies found (this is common with free proxies)")


def custom_fetcher_example():
    """
    Example: Use FreeProxyFetcher with custom settings.
    """
    print("\n=== Custom Fetcher Example ===\n")
    
    # Create custom fetcher
    fetcher = FreeProxyFetcher(
        timeout=15,  # Longer timeout
        max_proxies=30  # Get up to 30 proxies
    )
    
    try:
        # Fetch from specific source
        print("Fetching from a specific source...")
        url = "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all"
        proxies = fetcher.fetch_from_url(url)
        print(f"✓ Fetched {len(proxies)} proxies from proxyscrape")
        
        # Or fetch from all sources
        print("\nFetching from all sources...")
        all_proxies = fetcher.fetch_all()
        print(f"✓ Total proxies from all sources: {len(all_proxies)}")
        
        # Show sample
        if all_proxies:
            print("\nSample proxies:")
            for i, proxy in enumerate(all_proxies[:3], 1):
                print(f"  {i}. {proxy.host}:{proxy.port} ({proxy.protocol})")
    
    finally:
        fetcher.close()


def complete_workflow_example():
    """
    Complete workflow: Fetch free proxies, combine with user-agent rotation.
    """
    print("\n=== Complete Workflow Example ===\n")
    
    print("Step 1: Fetching free proxies...")
    proxies = get_free_proxies(max_proxies=15, test_proxies=False)
    print(f"✓ Got {len(proxies)} proxies")
    
    print("\nStep 2: Creating proxy configuration...")
    config = ProxyConfig(
        # Enable both rotations
        rotate_user_agent=True,
        rotate_ip=True,
        
        # Use random strategy for maximum unpredictability
        rotation_strategy="random",
        
        # Use fetched proxies
        proxies=proxies,
        
        # Reliability settings
        max_retries=3,
        timeout=15,
        
        # Rate limiting (respect servers)
        rate_limit=1.0,  # 1 request per second
    )
    print("✓ Configuration created")
    
    print("\nStep 3: Initializing RotatingProxy...")
    with RotatingProxy(config) as proxy:
        stats = proxy.get_stats()
        print(f"✓ Proxy ready!")
        print(f"  - Total proxies: {stats['total_proxies']}")
        print(f"  - Healthy proxies: {stats['healthy_proxies']}")
        print(f"  - User-agents: {stats['total_user_agents']}")
        print(f"  - Strategy: {stats['rotation_strategy']}")
        
        print("\nStep 4: Ready to make requests!")
        print("  Example: response = proxy.get('https://api.example.com/data')")


def direct_integration_example():
    """
    Example: Directly integrate free proxy fetching into your application.
    """
    print("\n=== Direct Integration Example ===\n")
    
    class MyAPIClient:
        """Example API client with automatic free proxy setup."""
        
        def __init__(self, max_proxies: int = 20):
            print(f"Initializing API client with free proxies...")
            
            # Fetch free proxies automatically
            proxies = get_free_proxies(max_proxies=max_proxies, test_proxies=False)
            print(f"✓ Loaded {len(proxies)} proxies")
            
            # Configure proxy
            config = ProxyConfig(
                rotate_user_agent=True,
                rotate_ip=True,
                rotation_strategy="random",
                proxies=proxies,
                max_retries=3,
            )
            
            # Initialize proxy
            self.proxy = RotatingProxy(config)
            print("✓ API client ready")
        
        def get(self, url: str):
            """Make GET request."""
            return self.proxy.get(url)
        
        def post(self, url: str, **kwargs):
            """Make POST request."""
            return self.proxy.post(url, **kwargs)
        
        def get_stats(self):
            """Get proxy statistics."""
            return self.proxy.get_stats()
        
        def close(self):
            """Cleanup."""
            self.proxy.close()
    
    # Use the client
    client = MyAPIClient(max_proxies=10)
    try:
        stats = client.get_stats()
        print(f"\nClient stats: {stats}")
        print("✓ Client ready to use!")
    finally:
        client.close()


if __name__ == "__main__":
    print("=" * 70)
    print("FREE PROXY USAGE EXAMPLES")
    print("=" * 70)
    print()
    
    try:
        basic_free_proxy_example()
        
        # Uncomment to test these (they make network requests)
        # tested_free_proxy_example()
        # custom_fetcher_example()
        complete_workflow_example()
        direct_integration_example()
        
        print("\n" + "=" * 70)
        print("NOTE: These examples fetch real proxies from the internet.")
        print("Some proxies may not work due to their free/public nature.")
        print("Use test_proxies=True for higher reliability (but slower).")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nNote: Free proxy fetching requires internet access.")
        print("The library will work without internet using manual proxies.")
