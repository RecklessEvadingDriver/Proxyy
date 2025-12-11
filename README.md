# Proxyy

A high-performance, secure Python proxy library with automatic user-agent and IP address rotation. Perfect for web scraping, API testing, and privacy-focused applications.

## Features

🔄 **Smart Rotation**
- Automatic user-agent rotation with 20+ diverse browser profiles
- IP address rotation through multiple proxy backends
- Configurable rotation strategies (random or round-robin)

⚡ **Performance**
- Connection pooling for faster requests
- Configurable rate limiting
- Automatic retry with exponential backoff
- Health checking and automatic failover

🔒 **Security**
- SSL/TLS verification support
- Request validation
- Authentication support for proxy backends
- Secure credential handling

🎯 **Easy Integration**
- Use as a standalone client
- Pass as a parameter to functions
- Context manager support
- Compatible with requests library patterns

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage with User-Agent Rotation

```python
from proxyy import RotatingProxy

# Create a proxy client with default settings
proxy = RotatingProxy()

# Make requests - user-agent rotates automatically
response = proxy.get("https://httpbin.org/user-agent")
print(response.json())

# Clean up
proxy.close()
```

### Using Context Manager

```python
from proxyy import RotatingProxy

with RotatingProxy() as proxy:
    response = proxy.get("https://api.example.com/data")
    print(response.json())
```

### Advanced Configuration

```python
from proxyy import RotatingProxy, ProxyConfig, ProxyInfo

# Define proxy backends
proxies = [
    ProxyInfo(host="proxy1.example.com", port=8080, protocol="http"),
    ProxyInfo(host="proxy2.example.com", port=8080, protocol="http"),
    ProxyInfo(
        host="proxy3.example.com",
        port=8080,
        protocol="http",
        username="user",
        password="pass"
    ),
]

# Create configuration
config = ProxyConfig(
    rotate_user_agent=True,
    rotate_ip=True,
    rotation_strategy="random",  # or "round-robin"
    proxies=proxies,
    verify_ssl=True,
    timeout=30,
    max_retries=3,
    rate_limit=2.0,  # 2 requests per second
)

# Use with configuration
with RotatingProxy(config) as proxy:
    response = proxy.get("https://api.example.com/data")
    print(f"Status: {response.status_code}")
    print(f"Stats: {proxy.get_stats()}")
```

### As a Parameter

```python
from proxyy import RotatingProxy

def fetch_data(url: str, proxy: RotatingProxy):
    """Function that accepts proxy as parameter."""
    response = proxy.get(url)
    return response.json()

# Create and pass proxy
with RotatingProxy() as proxy:
    data = fetch_data("https://api.example.com/data", proxy)
    print(data)
```

### Making Different Request Types

```python
from proxyy import RotatingProxy

with RotatingProxy() as proxy:
    # GET request
    response = proxy.get("https://api.example.com/data")
    
    # POST request
    response = proxy.post(
        "https://api.example.com/data",
        json={"key": "value"}
    )
    
    # PUT request
    response = proxy.put(
        "https://api.example.com/data/123",
        json={"key": "updated"}
    )
    
    # DELETE request
    response = proxy.delete("https://api.example.com/data/123")
```

## Configuration Options

### ProxyConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `rotate_user_agent` | bool | True | Enable user-agent rotation |
| `rotate_ip` | bool | True | Enable IP/proxy rotation |
| `rotation_strategy` | str | "random" | Rotation strategy: "random" or "round-robin" |
| `verify_ssl` | bool | True | Verify SSL certificates |
| `timeout` | int | 30 | Request timeout in seconds |
| `max_retries` | int | 3 | Maximum number of retry attempts |
| `retry_delay` | float | 1.0 | Base delay between retries (exponential backoff) |
| `rate_limit` | float | None | Maximum requests per second |
| `proxies` | List[ProxyInfo] | [] | List of proxy backends |
| `user_agents` | List[str] | None | Custom user-agent list (uses defaults if None) |
| `default_headers` | Dict | {} | Default headers for all requests |

### ProxyInfo Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `host` | str | Proxy server hostname |
| `port` | int | Proxy server port |
| `protocol` | str | Protocol: "http", "https", "socks4", or "socks5" |
| `username` | str | Optional username for authentication |
| `password` | str | Optional password for authentication |

## Rotation Strategies

### Random Strategy
Selects a random user-agent and proxy for each request. Best for maximum unpredictability.

```python
config = ProxyConfig(rotation_strategy="random")
```

### Round-Robin Strategy
Cycles through user-agents and proxies in order. Best for even distribution.

```python
config = ProxyConfig(rotation_strategy="round-robin")
```

## Security Features

### SSL Verification
By default, SSL certificates are verified. Disable only if necessary:

```python
config = ProxyConfig(verify_ssl=False)  # Not recommended
```

### Rate Limiting
Prevent overwhelming servers or triggering rate limits:

```python
config = ProxyConfig(rate_limit=2.0)  # 2 requests per second
```

### Automatic Retry with Backoff
Failed requests are automatically retried with exponential backoff:

```python
config = ProxyConfig(
    max_retries=3,
    retry_delay=1.0  # First retry after 1s, then 2s, then 3s
)
```

### Proxy Health Checking
Failed proxies are automatically marked and temporarily removed from rotation:

```python
# Failed proxies are unavailable for 5 minutes by default
# Automatic health recovery after timeout
```

## User-Agent Pool

The library includes 20+ diverse user-agents covering:
- Chrome (Windows, macOS, Linux)
- Firefox (Windows, macOS, Linux)
- Safari (macOS, iOS)
- Edge (Windows)
- Mobile browsers (Android, iOS)

You can also provide custom user-agents:

```python
custom_agents = [
    "Mozilla/5.0 (Custom) ...",
    "Mozilla/5.0 (Another Custom) ...",
]

config = ProxyConfig(user_agents=custom_agents)
```

## Examples

See the `examples/` directory for more usage examples:
- `basic_usage.py` - Basic features and configuration
- `as_parameter.py` - Using as a parameter in functions and classes

Run examples:
```bash
python examples/basic_usage.py
python examples/as_parameter.py
```

## Statistics and Monitoring

Get real-time statistics about your proxy:

```python
stats = proxy.get_stats()
print(stats)
# {
#     'total_proxies': 3,
#     'healthy_proxies': 2,
#     'total_user_agents': 20,
#     'rotation_strategy': 'random',
#     'rate_limit': 2.0
# }
```

## Best Practices

1. **Use Context Managers**: Always use `with` statements for automatic cleanup
2. **Configure Timeouts**: Set appropriate timeouts for your use case
3. **Enable Rate Limiting**: Respect server resources and avoid bans
4. **Monitor Health**: Check `get_stats()` to monitor proxy health
5. **Handle Exceptions**: Always wrap requests in try-except blocks
6. **Verify SSL**: Keep SSL verification enabled unless absolutely necessary
7. **Use Retries**: Configure retries for unreliable networks

## Error Handling

```python
from proxyy import RotatingProxy
import requests

with RotatingProxy() as proxy:
    try:
        response = proxy.get("https://api.example.com/data")
        response.raise_for_status()
        data = response.json()
    except requests.HTTPError as e:
        print(f"HTTP error: {e}")
    except requests.ConnectionError as e:
        print(f"Connection error: {e}")
    except requests.Timeout as e:
        print(f"Timeout error: {e}")
    except requests.RequestException as e:
        print(f"Request failed: {e}")
```

## Requirements

- Python 3.7+
- requests >= 2.31.0
- aiohttp >= 3.9.0
- aiohttp-socks >= 0.8.0
- pyyaml >= 6.0
- user-agents >= 2.2.0

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.