# Heroku Deployment Guide for Proxyy

## Quick Deploy to Heroku

### Option 1: One-Click Deploy
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

### Option 2: Manual Deployment

#### Prerequisites
- Git installed
- Heroku CLI installed ([Download here](https://devcenter.heroku.com/articles/heroku-cli))
- Heroku account (free tier works!)

#### Step-by-Step Deployment

1. **Clone or navigate to the repository**
   ```bash
   cd Proxyy
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create a new Heroku app**
   ```bash
   heroku create your-proxy-name
   # Or let Heroku generate a name:
   heroku create
   ```

4. **Deploy to Heroku**
   ```bash
   git push heroku main
   # If you're on a different branch:
   git push heroku your-branch:main
   ```

5. **Your proxy is now live!**
   ```
   https://your-app-name.herokuapp.com
   ```

## Using Your Heroku Proxy

Once deployed, your proxy URL will be: `https://your-app-name.herokuapp.com`

### Example Usage

**Python:**
```python
import requests

PROXY_URL = "https://your-app-name.herokuapp.com"

# Make request through proxy
response = requests.get(f"{PROXY_URL}/http://httpbin.org/ip")
print(response.json())

# Check health
health = requests.get(f"{PROXY_URL}/health").json()
print(health)

# Get statistics
stats = requests.get(f"{PROXY_URL}/stats").json()
print(f"Active proxies: {stats['healthy_proxies']}")
print(f"User-agents: {stats['total_user_agents']}")
```

**cURL:**
```bash
# Make request
curl https://your-app-name.herokuapp.com/http://httpbin.org/ip

# Check health
curl https://your-app-name.herokuapp.com/health

# Get stats
curl https://your-app-name.herokuapp.com/stats
```

**JavaScript/Node.js:**
```javascript
const axios = require('axios');

const PROXY_URL = 'https://your-app-name.herokuapp.com';

// Make request
axios.get(`${PROXY_URL}/http://httpbin.org/get`)
  .then(response => console.log(response.data));

// Check health
axios.get(`${PROXY_URL}/health`)
  .then(response => console.log(response.data));
```

## Configuration

The Heroku deployment automatically:
- ✅ Fetches free proxies from the internet
- ✅ Rotates user-agents (20+ browser profiles)
- ✅ Rotates IP addresses through fetched proxies
- ✅ Uses random rotation strategy
- ✅ Handles up to 30 free proxies

### Customizing Configuration

Edit the `Procfile` to change settings:

```
web: python start_server.py --host 0.0.0.0 --port $PORT --free-proxies --max-proxies 50 --strategy round-robin --rate-limit 2.0
```

Available options:
- `--max-proxies N` - Maximum free proxies to fetch (default: 30)
- `--strategy random|round-robin` - Rotation strategy (default: random)
- `--rate-limit N` - Rate limit in requests/second (optional)

## Monitoring

### View Logs
```bash
heroku logs --tail
```

### Check Dyno Status
```bash
heroku ps
```

### Restart App
```bash
heroku restart
```

## Endpoints

| Endpoint | Purpose | Example |
|----------|---------|---------|
| `/http://url` | Route request through proxy | `GET /http://example.com/api` |
| `/https://url` | Route HTTPS request through proxy | `GET /https://api.example.com` |
| `/health` | Health check endpoint | `GET /health` |
| `/stats` | Proxy statistics | `GET /stats` |

## Features

✅ **Free Tier Compatible**: Works on Heroku's free tier  
✅ **Automatic Free Proxies**: Fetches proxies from multiple sources  
✅ **User-Agent Rotation**: 20+ diverse browser profiles  
✅ **IP Rotation**: Routes through multiple proxy backends  
✅ **Health Checking**: Auto-removes failed proxies  
✅ **Statistics**: Real-time stats endpoint  
✅ **HTTPS Support**: Handles both HTTP and HTTPS requests  

## Scaling

### Free Tier
- 1 web dyno (550-1000 free hours/month)
- Sleeps after 30 minutes of inactivity
- Wakes up on first request

### Upgrade for Production
```bash
# Scale to hobby dyno (never sleeps)
heroku ps:scale web=1:hobby

# Scale to multiple dynos
heroku ps:scale web=2:standard-1x
```

## Environment Variables (Optional)

Set custom environment variables if needed:

```bash
heroku config:set MAX_PROXIES=50
heroku config:set ROTATION_STRATEGY=random
heroku config:set RATE_LIMIT=2.0
```

Then update `start_server.py` to read from environment variables.

## Troubleshooting

### App Crashes
```bash
# Check logs
heroku logs --tail

# Restart
heroku restart
```

### Slow Response
- Free proxies can be slow/unreliable
- Consider using paid proxy services for production
- Increase `--max-proxies` to have more backup options

### Timeout Errors
- Heroku has 30-second request timeout
- Some free proxies may be too slow
- The server will auto-retry with different proxies

### Dyno Sleeping (Free Tier)
- Free dynos sleep after 30 min inactivity
- Upgrade to hobby ($7/month) for always-on
- Or use a service like UptimeRobot to ping every 25 minutes

## Cost

- **Free Tier**: $0/month (with limitations)
- **Hobby**: $7/month (no sleeping, SSL included)
- **Standard**: $25-50/month (better performance)

## Security Notes

1. **Public Access**: Your proxy URL is public by default
2. **Rate Limiting**: Consider adding authentication for production
3. **Free Proxies**: Are public and may be monitored
4. **HTTPS**: Heroku provides free SSL certificates

## Production Recommendations

1. **Use Hobby or Standard Dyno**: Prevents sleeping
2. **Add Authentication**: Protect your proxy endpoint
3. **Monitor Usage**: Check logs and stats regularly
4. **Consider Paid Proxies**: More reliable than free ones
5. **Set Rate Limits**: Prevent abuse

## Support

For issues:
1. Check `heroku logs --tail`
2. Verify configuration in `Procfile`
3. Open an issue on GitHub

## Quick Reference

```bash
# Deploy
heroku create && git push heroku main

# View logs
heroku logs --tail

# Check status
heroku ps

# Restart
heroku restart

# Open in browser
heroku open

# Scale
heroku ps:scale web=1

# View config
heroku config
```

---

**Your proxy is ready to use at**: `https://your-app-name.herokuapp.com`
