#!/usr/bin/env python3
"""
Start the Proxyy rotating proxy server
"""

from proxyy.server import run_server
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Proxyy Rotating Proxy Server - Host a proxy with rotation capabilities',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start server with default settings (no backend proxies)
  python start_server.py
  
  # Start server with free proxies from internet
  python start_server.py --free-proxies
  
  # Start server with rate limiting
  python start_server.py --free-proxies --rate-limit 2.0
  
  # Start server on custom port
  python start_server.py --port 9000 --free-proxies
  
  # Use round-robin rotation
  python start_server.py --free-proxies --strategy round-robin

Usage:
  Send requests to: http://localhost:8080/http://target-url
  Health check: http://localhost:8080/health
  Statistics: http://localhost:8080/stats
        """
    )
    
    parser.add_argument('--host', default='0.0.0.0', 
                       help='Host to bind to (default: 0.0.0.0 = all interfaces)')
    parser.add_argument('--port', type=int, default=8080, 
                       help='Port to listen on (default: 8080)')
    parser.add_argument('--free-proxies', action='store_true', 
                       help='Fetch and use free proxies from internet')
    parser.add_argument('--max-proxies', type=int, default=50, 
                       help='Maximum free proxies to fetch (default: 50)')
    parser.add_argument('--strategy', default='random', 
                       choices=['random', 'round-robin'], 
                       help='Rotation strategy (default: random)')
    parser.add_argument('--rate-limit', type=float, 
                       help='Rate limit in requests/second (optional)')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("PROXYY ROTATING PROXY SERVER")
    print("=" * 70)
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Free Proxies: {'Yes' if args.free_proxies else 'No'}")
    if args.free_proxies:
        print(f"Max Free Proxies: {args.max_proxies}")
    print(f"Strategy: {args.strategy}")
    if args.rate_limit:
        print(f"Rate Limit: {args.rate_limit} req/s")
    print("=" * 70)
    print()
    
    run_server(
        host=args.host,
        port=args.port,
        use_free_proxies=args.free_proxies,
        max_free_proxies=args.max_proxies,
        rotation_strategy=args.strategy,
        rate_limit=args.rate_limit
    )
