# Proxyy - Rotating Proxy Server

Deploy your own rotating proxy server with user-agent and IP rotation in minutes!

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## What Is This?

A proxy server that automatically:
- ✅ Rotates user-agents (20+ browser profiles)
- ✅ Rotates IP addresses (fetches free proxies from internet)
- ✅ Handles retries automatically
- ✅ Removes failed proxies
- ✅ Works with any programming language

## Quick Start - Deploy to Heroku

1. **Click the deploy button above** ☝️

2. **Your proxy is live!** 
   ```
   https://your-app-name.herokuapp.com
   ```

3. **Use it from anywhere:**

**Python:**
```python
import requests

PROXY = "https://your-app-name.herokuapp.com"
response = requests.get(f"{PROXY}/http://httpbin.org/ip")
print(response.json())
```

**cURL:**
```bash
curl https://your-app-name.herokuapp.com/http://httpbin.org/ip
```

**JavaScript:**
```javascript
const axios = require('axios');
axios.get('https://your-app-name.herokuapp.com/http://httpbin.org/get')
  .then(res => console.log(res.data));
```

**📖 [Complete Heroku Deployment Guide](HEROKU.md)**

## API Endpoints

| Endpoint | Purpose | Example |
|----------|---------|---------|
| `/http://url` | Route request through proxy | `/http://example.com/api` |
| `/https://url` | Route HTTPS request through proxy | `/https://api.example.com` |
| `/health` | Health check | `/health` |
| `/stats` | Proxy statistics | `/stats` |

## Usage Examples

### Python

```python
import requests

PROXY_URL = "https://your-app-name.herokuapp.com"

# Make request
response = requests.get(f"{PROXY_URL}/http://httpbin.org/ip")
print(response.json())

# POST request
data = {"key": "value"}
response = requests.post(f"{PROXY_URL}/http://httpbin.org/post", json=data)

# Check health
health = requests.get(f"{PROXY_URL}/health").json()
print(health)  # {"status": "healthy", ...}

# Get statistics
stats = requests.get(f"{PROXY_URL}/stats").json()
print(f"Active proxies: {stats['healthy_proxies']}")
print(f"Total user-agents: {stats['total_user_agents']}")
```

### cURL

```bash
# Make request
curl https://your-app-name.herokuapp.com/http://httpbin.org/ip

# Check health
curl https://your-app-name.herokuapp.com/health

# Get stats
curl https://your-app-name.herokuapp.com/stats
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const PROXY = 'https://your-app-name.herokuapp.com';

// Make request
axios.get(`${PROXY}/http://httpbin.org/get`)
  .then(response => console.log(response.data));

// Check health
axios.get(`${PROXY}/health`)
  .then(response => console.log(response.data));

// Get stats
axios.get(`${PROXY}/stats`)
  .then(response => console.log(response.data));
```

## Features

🔄 **User-Agent Rotation**
- 20+ browser profiles (Chrome, Firefox, Safari, Edge, Mobile)
- Random or round-robin rotation
- Realistic user-agents for better anonymity

🌐 **IP Rotation**
- Automatically fetches free proxies from multiple sources
- Health checking - removes failed proxies
- Supports up to 50+ proxies in rotation

⚡ **Performance & Reliability**
- Automatic retry on failures
- Connection pooling
- Multi-threaded request handling
- Rate limiting support

🔒 **Security**
- HTTPS support
- SSL/TLS verification
- Request validation

## Configuration

The Heroku deployment is configured via `Procfile`:

```
web: python start_server.py --host 0.0.0.0 --port $PORT --free-proxies --max-proxies 30
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--free-proxies` | False | Fetch free proxies from internet |
| `--max-proxies` | 30 | Maximum proxies to fetch |
| `--strategy` | random | Rotation strategy (random/round-robin) |
| `--rate-limit` | None | Rate limit (requests/second) |

### Customize Configuration

Edit `Procfile` to change settings:

```
web: python start_server.py --host 0.0.0.0 --port $PORT --free-proxies --max-proxies 50 --strategy round-robin
```

Then redeploy:
```bash
git add Procfile
git commit -m "Update configuration"
git push heroku main
```

## Monitoring (Heroku)

```bash
# View logs
heroku logs --tail

# Check status
heroku ps

# Restart app
heroku restart

# Open in browser
heroku open
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python start_server.py --free-proxies

# Test locally
curl http://localhost:8080/health
curl http://localhost:8080/http://httpbin.org/ip
```

## How It Works

1. **Request comes in** → `https://your-app.herokuapp.com/http://example.com`
2. **Server picks** → Random user-agent + random proxy
3. **Makes request** → Through selected proxy with rotated user-agent
4. **Returns response** → Back to your client

If a proxy fails, it's automatically removed and request is retried with a different proxy.

## Deployment Options

### Heroku (Recommended)
- ✅ Free tier available
- ✅ Easy deployment
- ✅ Auto SSL included
- ✅ One-click deploy button

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "start_server.py", "--host", "0.0.0.0", "--port", "8080", "--free-proxies"]
```

### Other Platforms
Works on AWS, GCP, Azure, DigitalOcean, etc. Just run:
```bash
python start_server.py --host 0.0.0.0 --port 8080 --free-proxies
```

## Python Library Usage

You can also use Proxyy as a Python library:

```python
from proxyy import RotatingProxy, ProxyConfig, get_free_proxies

# Get free proxies
proxies = get_free_proxies(max_proxies=20)
print(f"Fetched {len(proxies)} proxies")

# Configure
config = ProxyConfig(
    rotate_user_agent=True,
    rotate_ip=True,
    proxies=proxies
)

# Use it
with RotatingProxy(config) as proxy:
    response = proxy.get("http://example.com")
    print(response.text)
```

See `examples/` directory for more examples.

## Free Proxy Sources

Automatically fetches from:
- ProxyScrape API
- GitHub proxy lists (TheSpeedX, ShiftyTR, monosans, clarketm)
- Proxy-list.download API

**Note**: Free proxies can be unreliable. For production, consider using paid proxy services.

## Troubleshooting

**Slow responses?**
- Free proxies are often slow
- Increase max-proxies: `--max-proxies 100`
- Consider paid proxies for production

**App crashes?**
```bash
heroku logs --tail  # Check the logs
heroku restart       # Restart the app
```

**Heroku dyno sleeping?**
- Free tier sleeps after 30 min inactivity
- Upgrade to Hobby ($7/month) for always-on
- Or use UptimeRobot to ping every 25 minutes

## Cost

- **Heroku Free**: $0/month (with limitations)
- **Heroku Hobby**: $7/month (no sleeping)
- **Heroku Standard**: $25+/month (production)

## Files

- `start_server.py` - Main server script
- `Procfile` - Heroku configuration
- `runtime.txt` - Python version
- `requirements.txt` - Dependencies
- `proxyy/` - Core library
- `examples/` - Usage examples
- `HEROKU.md` - Detailed Heroku guide

## Requirements

- Python 3.7+
- requests >= 2.31.0
- aiohttp >= 3.9.0
- pyyaml >= 6.0

## License

MIT License - See LICENSE file

## Contributing

Contributions welcome! Open an issue or PR.

## Support

- 📖 [Heroku Deployment Guide](HEROKU.md)
- 💬 Open an issue on GitHub
- 📧 Contact via GitHub

---

**Ready to deploy?** → [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
