# Proxyy

A high-performance, secure Python proxy library with automatic user-agent and IP address rotation. Perfect for web scraping, API testing, and privacy-focused applications.

## Features

🔄 **Smart Rotation**
- Automatic user-agent rotation with 20+ diverse browser profiles
- IP address rotation through multiple proxy backends
- **Automatic free proxy fetching from the internet**
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
- **One-line free proxy integration**
- **Host as HTTP server with URL access**

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

### Using Free Proxies from the Internet (NEW!)

```python
from proxyy import RotatingProxy, ProxyConfig, get_free_proxies

# Automatically fetch free proxies from the internet
free_proxies = get_free_proxies(max_proxies=20)
print(f"Fetched {len(free_proxies)} free proxies")

# Create configuration with free proxies
config = ProxyConfig(
    rotate_user_agent=True,
    rotate_ip=True,
    proxies=free_proxies,
)

# Use them!
with RotatingProxy(config) as proxy:
    response = proxy.get("https://api.example.com/data")
    print(response.json())
```

### Host as HTTP Proxy Server (NEW!)

Host Proxyy as an HTTP server and route requests through it via URL:

```bash
# Start server with free proxies
python start_server.py --free-proxies --port 8080

# Or without free proxies (user-agent rotation only)
python start_server.py --port 8080
```

Then make requests from **any language or tool**:

```python
import requests

# Method 1: Direct URL routing
response = requests.get("http://localhost:8080/http://httpbin.org/ip")

# Method 2: Standard proxy configuration
proxies = {"http": "http://localhost:8080", "https": "http://localhost:8080"}
response = requests.get("http://example.com", proxies=proxies)

# Check health
health = requests.get("http://localhost:8080/health").json()

# Get statistics
stats = requests.get("http://localhost:8080/stats").json()
```

```bash
# Use from curl
curl http://localhost:8080/http://httpbin.org/ip

# Check server health
curl http://localhost:8080/health

# Get statistics
curl http://localhost:8080/stats
```

Deploy anywhere (Heroku, AWS, GCP, etc.) and access from any device!

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

## Free Proxy Integration

Proxyy can automatically fetch free proxies from public sources on the internet.

### Quick Free Proxy Usage

```python
from proxyy import get_free_proxies, RotatingProxy, ProxyConfig

# Fetch free proxies (fast, but some may not work)
proxies = get_free_proxies(max_proxies=50)

# Use them
config = ProxyConfig(proxies=proxies, rotate_ip=True, rotate_user_agent=True)
with RotatingProxy(config) as proxy:
    response = proxy.get("https://api.example.com/data")
```

### Tested Free Proxies (Recommended)

```python
from proxyy import get_free_proxies, RotatingProxy, ProxyConfig

# Fetch and test proxies (slower but more reliable)
proxies = get_free_proxies(max_proxies=20, test_proxies=True)
print(f"Found {len(proxies)} working proxies")

config = ProxyConfig(proxies=proxies, rotate_ip=True)
with RotatingProxy(config) as proxy:
    response = proxy.get("https://api.example.com/data")
```

### Custom Free Proxy Fetcher

```python
from proxyy import FreeProxyFetcher

# Create custom fetcher
fetcher = FreeProxyFetcher(
    timeout=15,
    max_proxies=100
)

try:
    # Fetch from all sources
    proxies = fetcher.fetch_all()
    print(f"Fetched {len(proxies)} proxies")
    
    # Or fetch and test
    working_proxies = fetcher.fetch_and_test()
    print(f"Found {len(working_proxies)} working proxies")
    
finally:
    fetcher.close()
```

### Free Proxy Sources

The library automatically fetches from multiple public sources:
- ProxyScrape API
- GitHub proxy lists (TheSpeedX, ShiftyTR, monosans, clarketm)
- Proxy-list.download API

**Note:** Free proxies can be unreliable. Use `test_proxies=True` for better results, or provide your own proxy list for production use.

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

## Hosted Proxy Server

Host Proxyy as an HTTP server accessible via URL - perfect for deployment!

### Starting the Server

```bash
# Basic usage - user-agent rotation only
python start_server.py

# With free proxies from internet
python start_server.py --free-proxies

# Custom port
python start_server.py --port 9000 --free-proxies

# With rate limiting
python start_server.py --free-proxies --rate-limit 2.0

# Round-robin rotation
python start_server.py --free-proxies --strategy round-robin

# All options
python start_server.py --host 0.0.0.0 --port 8080 --free-proxies --max-proxies 100 --strategy random --rate-limit 1.5
```

### Server Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--host` | 0.0.0.0 | Host to bind to (0.0.0.0 = all interfaces) |
| `--port` | 8080 | Port to listen on |
| `--free-proxies` | False | Fetch and use free proxies |
| `--max-proxies` | 50 | Maximum number of free proxies to fetch |
| `--strategy` | random | Rotation strategy (random or round-robin) |
| `--rate-limit` | None | Rate limit in requests/second |

### Using the Hosted Proxy

**Python:**
```python
import requests

# Direct URL routing
url = "http://localhost:8080/http://httpbin.org/get"
response = requests.get(url)

# Or use as standard proxy
proxies = {
    'http': 'http://localhost:8080',
    'https': 'http://localhost:8080'
}
response = requests.get('http://example.com', proxies=proxies)
```

**cURL:**
```bash
# Direct request
curl http://localhost:8080/http://httpbin.org/ip

# Using as proxy
curl -x http://localhost:8080 http://httpbin.org/ip
```

**Node.js:**
```javascript
const axios = require('axios');

// Direct URL routing
axios.get('http://localhost:8080/http://httpbin.org/get')
  .then(response => console.log(response.data));

// Using as proxy
axios.get('http://example.com', {
  proxy: {
    host: 'localhost',
    port: 8080
  }
});
```

**Any Language/Tool:**
Just configure your HTTP client to use `http://localhost:8080` as the proxy!

### Server Endpoints

| Endpoint | Description |
|----------|-------------|
| `/http://target-url` | Route request to target URL through proxy |
| `/health` | Health check endpoint (returns JSON) |
| `/stats` | Proxy statistics (returns JSON with proxy pool info) |

### Deployment

Deploy to any cloud platform:

**Heroku:**
```bash
# Add Procfile
echo "web: python start_server.py --host 0.0.0.0 --port \$PORT --free-proxies" > Procfile
git push heroku main
```

**Docker:**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "start_server.py", "--host", "0.0.0.0", "--port", "8080", "--free-proxies"]
```

**AWS/GCP/Azure:**
Deploy as a container or web service with the start command:
```bash
python start_server.py --host 0.0.0.0 --port 8080 --free-proxies
```

Then access from anywhere: `http://your-domain.com/http://target-url`

### Programmatic Server Control

```python
from proxyy import ProxyServer, ProxyConfig

# Create custom configuration
config = ProxyConfig(
    rotate_user_agent=True,
    rotate_ip=True,
    rotation_strategy='random',
    rate_limit=2.0
)

# Initialize server
server = ProxyServer(
    host='0.0.0.0',
    port=8080,
    config=config,
    use_free_proxies=True,
    max_free_proxies=50
)

# Start server (blocking)
server.start()

# Or use run_server convenience function
from proxyy import run_server

run_server(
    host='0.0.0.0',
    port=8080,
    use_free_proxies=True,
    rotation_strategy='random'
)
```

## Examples

See the `examples/` directory for more usage examples:
- `basic_usage.py` - Basic features and configuration
- `as_parameter.py` - Using as a parameter in functions and classes
- `free_proxy_usage.py` - Using free proxies from the internet
- `hosted_proxy_usage.py` - Using the hosted proxy server

Run examples:
```bash
python examples/basic_usage.py
python examples/as_parameter.py
python examples/free_proxy_usage.py

# For hosted proxy example, first start the server:
python start_server.py --free-proxies
# Then in another terminal:
python examples/hosted_proxy_usage.py
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