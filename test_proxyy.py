"""
Unit tests for the Proxyy library
Tests functionality without requiring network access
"""

import sys
sys.path.insert(0, '.')

from proxyy import RotatingProxy, ProxyConfig, ProxyInfo, UserAgentRotator, IPRotator


def test_user_agent_rotator():
    """Test UserAgentRotator functionality."""
    print("=== Testing UserAgentRotator ===")
    
    # Test initialization
    rotator = UserAgentRotator()
    assert len(rotator) == 20, "Should have 20 default user-agents"
    print(f"✓ Initialized with {len(rotator)} user-agents")
    
    # Test get_random
    ua1 = rotator.get_random()
    ua2 = rotator.get_random()
    assert isinstance(ua1, str), "Should return a string"
    assert len(ua1) > 0, "User-agent should not be empty"
    print(f"✓ Random UA 1: {ua1[:60]}...")
    print(f"✓ Random UA 2: {ua2[:60]}...")
    
    # Test get_next (round-robin)
    rotator.reset()
    uas = [rotator.get_next() for _ in range(3)]
    assert len(uas) == 3, "Should get 3 user-agents"
    print(f"✓ Round-robin rotation works: got {len(uas)} sequential UAs")
    
    # Test add/remove
    custom_ua = "Custom User Agent"
    rotator.add_user_agent(custom_ua)
    assert len(rotator) == 21, "Should have 21 user-agents after adding"
    print(f"✓ Added custom UA, now have {len(rotator)} UAs")
    
    rotator.remove_user_agent(custom_ua)
    assert len(rotator) == 20, "Should be back to 20 user-agents"
    print(f"✓ Removed custom UA, back to {len(rotator)} UAs")
    
    # Test custom list
    custom_list = ["UA1", "UA2", "UA3"]
    custom_rotator = UserAgentRotator(custom_list)
    assert len(custom_rotator) == 3, "Should have 3 custom user-agents"
    print(f"✓ Custom rotator with {len(custom_rotator)} UAs")
    
    print("✅ UserAgentRotator tests passed!\n")


def test_ip_rotator():
    """Test IPRotator functionality."""
    print("=== Testing IPRotator ===")
    
    # Create test proxies
    proxies = [
        ProxyInfo(host="proxy1.example.com", port=8080),
        ProxyInfo(host="proxy2.example.com", port=8080, protocol="https"),
        ProxyInfo(host="proxy3.example.com", port=1080, protocol="socks5", 
                 username="user", password="pass"),
    ]
    
    # Test initialization
    rotator = IPRotator(proxies)
    assert len(rotator) == 3, "Should have 3 proxies"
    print(f"✓ Initialized with {len(rotator)} proxies")
    
    # Test proxy URL generation
    proxy1 = proxies[0]
    assert proxy1.get_url() == "http://proxy1.example.com:8080"
    print(f"✓ Proxy URL (no auth): {proxy1.get_url()}")
    
    proxy3 = proxies[2]
    expected_url = "socks5://user:pass@proxy3.example.com:1080"
    assert proxy3.get_url() == expected_url
    print(f"✓ Proxy URL (with auth): {proxy3.get_url()}")
    
    # Test proxy dict
    proxy_dict = proxy1.get_dict()
    assert "http" in proxy_dict and "https" in proxy_dict
    print(f"✓ Proxy dict: {proxy_dict}")
    
    # Test get_random
    random_proxy = rotator.get_random()
    assert random_proxy in proxies, "Should return one of the proxies"
    print(f"✓ Random proxy: {random_proxy.host}")
    
    # Test get_next (round-robin)
    rotator.reset()
    next_proxies = [rotator.get_next() for _ in range(3)]
    assert len(next_proxies) == 3, "Should get 3 proxies"
    print(f"✓ Round-robin rotation: {[p.host for p in next_proxies]}")
    
    # Test health checking
    assert rotator.healthy_count() == 3, "All proxies should be healthy"
    print(f"✓ Healthy proxies: {rotator.healthy_count()}/{len(rotator)}")
    
    # Mark one as failed
    rotator.mark_failed(proxies[0])
    assert rotator.healthy_count() == 2, "Should have 2 healthy proxies"
    print(f"✓ After marking one failed: {rotator.healthy_count()}/{len(rotator)} healthy")
    
    # Test that failed proxy is skipped
    available = rotator.get_next()
    assert available != proxies[0], "Should not return failed proxy"
    print(f"✓ Failed proxy skipped, got: {available.host}")
    
    # Test reset
    rotator.reset()
    assert rotator.healthy_count() == 3, "All should be healthy after reset"
    print(f"✓ After reset: {rotator.healthy_count()}/{len(rotator)} healthy")
    
    # Test add/remove
    new_proxy = ProxyInfo(host="proxy4.example.com", port=8080)
    rotator.add_proxy(new_proxy)
    assert len(rotator) == 4, "Should have 4 proxies"
    print(f"✓ Added proxy, now have {len(rotator)} proxies")
    
    rotator.remove_proxy(new_proxy)
    assert len(rotator) == 3, "Should be back to 3 proxies"
    print(f"✓ Removed proxy, back to {len(rotator)} proxies")
    
    print("✅ IPRotator tests passed!\n")


def test_proxy_config():
    """Test ProxyConfig functionality."""
    print("=== Testing ProxyConfig ===")
    
    # Test default config
    config = ProxyConfig()
    assert config.rotate_user_agent == True
    assert config.rotate_ip == True
    assert config.rotation_strategy == "random"
    print("✓ Default config created")
    
    # Test custom config
    proxies = [ProxyInfo(host="test.com", port=8080)]
    custom_config = ProxyConfig(
        rotate_user_agent=True,
        rotate_ip=True,
        rotation_strategy="round-robin",
        verify_ssl=False,
        timeout=60,
        max_retries=5,
        rate_limit=10.0,
        proxies=proxies,
    )
    assert custom_config.rotation_strategy == "round-robin"
    assert custom_config.timeout == 60
    assert custom_config.max_retries == 5
    assert custom_config.rate_limit == 10.0
    assert len(custom_config.proxies) == 1
    print("✓ Custom config with all parameters")
    print(f"  - Strategy: {custom_config.rotation_strategy}")
    print(f"  - Timeout: {custom_config.timeout}s")
    print(f"  - Max retries: {custom_config.max_retries}")
    print(f"  - Rate limit: {custom_config.rate_limit} req/s")
    
    print("✅ ProxyConfig tests passed!\n")


def test_rotating_proxy():
    """Test RotatingProxy functionality (without network)."""
    print("=== Testing RotatingProxy ===")
    
    # Test initialization with default config
    proxy = RotatingProxy()
    assert proxy.config.rotate_user_agent == True
    print("✓ Default RotatingProxy initialized")
    
    # Test with custom config
    config = ProxyConfig(
        rotation_strategy="round-robin",
        max_retries=2,
    )
    proxy_custom = RotatingProxy(config)
    assert proxy_custom.config.rotation_strategy == "round-robin"
    print("✓ Custom RotatingProxy initialized")
    
    # Test user-agent generation
    ua1 = proxy._get_user_agent()
    ua2 = proxy._get_user_agent()
    assert isinstance(ua1, str) and len(ua1) > 0
    print(f"✓ User-agent generation: {ua1[:60]}...")
    
    # Test stats
    stats = proxy.get_stats()
    assert "total_proxies" in stats
    assert "healthy_proxies" in stats
    assert "total_user_agents" in stats
    print(f"✓ Stats: {stats}")
    
    # Test context manager
    with RotatingProxy() as ctx_proxy:
        assert ctx_proxy.session is not None
        print("✓ Context manager works")
    
    # Test cleanup
    proxy.close()
    proxy_custom.close()
    print("✓ Cleanup successful")
    
    print("✅ RotatingProxy tests passed!\n")


def test_rotation_strategies():
    """Test different rotation strategies."""
    print("=== Testing Rotation Strategies ===")
    
    # Test random strategy
    config_random = ProxyConfig(rotation_strategy="random")
    proxy_random = RotatingProxy(config_random)
    uas_random = [proxy_random._get_user_agent() for _ in range(5)]
    assert len(uas_random) == 5
    print(f"✓ Random strategy: generated {len(uas_random)} UAs")
    
    # Test round-robin strategy
    config_rr = ProxyConfig(rotation_strategy="round-robin")
    proxy_rr = RotatingProxy(config_rr)
    uas_rr = [proxy_rr._get_user_agent() for _ in range(5)]
    assert len(uas_rr) == 5
    print(f"✓ Round-robin strategy: generated {len(uas_rr)} UAs")
    
    proxy_random.close()
    proxy_rr.close()
    
    print("✅ Rotation strategy tests passed!\n")


def test_integration():
    """Test integration scenarios."""
    print("=== Testing Integration Scenarios ===")
    
    # Scenario 1: Use as a parameter
    def make_request(proxy: RotatingProxy):
        stats = proxy.get_stats()
        return stats
    
    with RotatingProxy() as proxy:
        result = make_request(proxy)
        assert "total_user_agents" in result
        print("✓ Scenario 1: Used as function parameter")
    
    # Scenario 2: Multiple proxy instances
    proxy1 = RotatingProxy(ProxyConfig(rotation_strategy="random"))
    proxy2 = RotatingProxy(ProxyConfig(rotation_strategy="round-robin"))
    
    assert proxy1.config.rotation_strategy != proxy2.config.rotation_strategy
    print("✓ Scenario 2: Multiple independent instances")
    
    proxy1.close()
    proxy2.close()
    
    # Scenario 3: Custom user-agents
    custom_uas = ["Custom UA 1", "Custom UA 2", "Custom UA 3"]
    config = ProxyConfig(user_agents=custom_uas)
    proxy = RotatingProxy(config)
    
    assert len(proxy.ua_rotator) == 3
    print(f"✓ Scenario 3: Custom user-agents ({len(proxy.ua_rotator)} UAs)")
    
    proxy.close()
    
    print("✅ Integration tests passed!\n")


if __name__ == "__main__":
    print("=" * 70)
    print("PROXYY LIBRARY TEST SUITE")
    print("=" * 70)
    print()
    
    try:
        test_user_agent_rotator()
        test_ip_rotator()
        test_proxy_config()
        test_rotating_proxy()
        test_rotation_strategies()
        test_integration()
        
        print("=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
