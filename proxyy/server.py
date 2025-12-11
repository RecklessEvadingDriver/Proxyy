"""
HTTP Proxy Server - Host Proxyy as a web service
Allows routing requests through this proxy server
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.error
from socketserver import ThreadingMixIn
import logging
from typing import Optional
import json

from .proxy import RotatingProxy, ProxyConfig
from .free_proxy import get_free_proxies

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProxyRequestHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler that forwards requests through the rotating proxy.
    """
    
    # Maximum content length (10MB)
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    
    # Internal network ranges to block (SSRF prevention)
    BLOCKED_HOSTS = [
        '127.', '0.0.0.0', 'localhost',
        '10.', '172.16.', '172.17.', '172.18.', '172.19.',
        '172.20.', '172.21.', '172.22.', '172.23.', '172.24.',
        '172.25.', '172.26.', '172.27.', '172.28.', '172.29.',
        '172.30.', '172.31.', '192.168.', '169.254.',
    ]
    
    rotating_proxy: Optional[RotatingProxy] = None
    
    def log_message(self, format, *args):
        """Override to use logger instead of print."""
        logger.info(f"{self.client_address[0]} - {format % args}")
    
    def do_GET(self):
        """Handle GET requests."""
        self._handle_request('GET')
    
    def do_POST(self):
        """Handle POST requests."""
        self._handle_request('POST')
    
    def do_PUT(self):
        """Handle PUT requests."""
        self._handle_request('PUT')
    
    def do_DELETE(self):
        """Handle DELETE requests."""
        self._handle_request('DELETE')
    
    def do_HEAD(self):
        """Handle HEAD requests."""
        self._handle_request('HEAD')
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests."""
        self._handle_request('OPTIONS')
    
    def _handle_request(self, method: str):
        """
        Handle HTTP request by forwarding through rotating proxy.
        
        Args:
            method: HTTP method (GET, POST, etc.)
        """
        try:
            # Get the target URL from the path
            # Format: http://localhost:8080/http://example.com/api
            if self.path.startswith('/'):
                target_url = self.path[1:]  # Remove leading slash
            else:
                target_url = self.path
            
            # Handle special endpoints
            if target_url == 'health' or target_url == '/health':
                self._send_health_check()
                return
            elif target_url == 'stats' or target_url == '/stats':
                self._send_stats()
                return
            
            # Validate URL
            if not target_url.startswith('http://') and not target_url.startswith('https://'):
                self._send_error_response(400, "Invalid URL. Format: http://proxy-host:port/http://target-url")
                return
            
            # SSRF Protection: Block requests to internal networks
            try:
                from urllib.parse import urlparse
                parsed_url = urlparse(target_url)
                hostname = parsed_url.hostname or ''
                
                # Block internal/private IPs
                for blocked in self.BLOCKED_HOSTS:
                    if hostname.startswith(blocked):
                        self._send_error_response(403, "Access to internal networks is forbidden")
                        return
            except Exception:
                self._send_error_response(400, "Invalid URL format")
                return
            
            logger.info(f"Forwarding {method} request to: {target_url}")
            
            # Prepare request kwargs
            kwargs = {}
            
            # Get request headers (excluding hop-by-hop headers)
            headers = {}
            for header, value in self.headers.items():
                if header.lower() not in ['host', 'connection', 'proxy-connection', 
                                         'transfer-encoding', 'upgrade']:
                    headers[header] = value
            
            if headers:
                kwargs['headers'] = headers
            
            # Get request body for POST/PUT with size limit
            if method in ['POST', 'PUT', 'PATCH']:
                content_length = int(self.headers.get('Content-Length', 0))
                
                # DoS Protection: Limit request body size
                if content_length > self.MAX_CONTENT_LENGTH:
                    self._send_error_response(413, f"Request body too large. Maximum size: {self.MAX_CONTENT_LENGTH} bytes")
                    return
                
                if content_length > 0:
                    body = self.rfile.read(content_length)
                    kwargs['data'] = body
            
            # Forward request through rotating proxy
            if self.rotating_proxy:
                response = self.rotating_proxy.request(method, target_url, **kwargs)
                
                # Send response back to client
                self.send_response(response.status_code)
                
                # Send response headers
                for header, value in response.headers.items():
                    if header.lower() not in ['transfer-encoding', 'connection']:
                        self.send_header(header, value)
                self.end_headers()
                
                # Send response body
                self.wfile.write(response.content)
            else:
                self._send_error_response(500, "Proxy not initialized")
                
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            self._send_error_response(500, str(e))
    
    def _send_health_check(self):
        """Send health check response."""
        response = {
            "status": "healthy",
            "service": "Proxyy Rotating Proxy Server",
            "version": "1.0.0"
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def _send_stats(self):
        """Send proxy statistics."""
        if self.rotating_proxy:
            stats = self.rotating_proxy.get_stats()
        else:
            stats = {"error": "Proxy not initialized"}
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(stats).encode())
    
    def _send_error_response(self, code: int, message: str):
        """Send error response."""
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        error_response = {
            "error": message,
            "code": code
        }
        self.wfile.write(json.dumps(error_response).encode())


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Threaded HTTP server for handling multiple concurrent requests."""
    daemon_threads = True


class ProxyServer:
    """
    Main proxy server that can be hosted and accessed via URL.
    """
    
    def __init__(self, 
                 host: str = '0.0.0.0',
                 port: int = 8080,
                 config: Optional[ProxyConfig] = None,
                 use_free_proxies: bool = False,
                 max_free_proxies: int = 50):
        """
        Initialize the proxy server.
        
        Args:
            host: Host to bind to (0.0.0.0 for all interfaces)
            port: Port to listen on
            config: ProxyConfig for rotating proxy settings
            use_free_proxies: Whether to fetch and use free proxies
            max_free_proxies: Maximum number of free proxies to fetch
        """
        self.host = host
        self.port = port
        self.config = config if config else ProxyConfig()
        
        # Fetch free proxies if requested
        if use_free_proxies:
            logger.info(f"Fetching free proxies (max: {max_free_proxies})...")
            free_proxies = get_free_proxies(max_proxies=max_free_proxies, test_proxies=False)
            logger.info(f"Fetched {len(free_proxies)} free proxies")
            
            # Add to config
            if not self.config.proxies:
                self.config.proxies = []
            self.config.proxies.extend(free_proxies)
        
        # Initialize rotating proxy
        self.rotating_proxy = RotatingProxy(self.config)
        
        # Set rotating proxy in handler
        ProxyRequestHandler.rotating_proxy = self.rotating_proxy
        
        # Create server
        self.server = ThreadedHTTPServer((self.host, self.port), ProxyRequestHandler)
        
        logger.info(f"Proxy server initialized on {self.host}:{self.port}")
        if self.config.proxies:
            logger.info(f"Backend proxies: {len(self.config.proxies)}")
        logger.info(f"User-agents in pool: {len(self.rotating_proxy.ua_rotator)}")
    
    def start(self):
        """Start the proxy server."""
        logger.info(f"Starting proxy server on http://{self.host}:{self.port}")
        logger.info("Usage: http://localhost:8080/http://target-url")
        logger.info("Health check: http://localhost:8080/health")
        logger.info("Statistics: http://localhost:8080/stats")
        logger.info("Press Ctrl+C to stop")
        
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            logger.info("\nShutting down proxy server...")
            self.stop()
    
    def stop(self):
        """Stop the proxy server."""
        self.server.shutdown()
        self.server.server_close()
        self.rotating_proxy.close()
        logger.info("Proxy server stopped")


def run_server(host: str = '0.0.0.0',
               port: int = 8080,
               use_free_proxies: bool = True,
               max_free_proxies: int = 50,
               rotation_strategy: str = 'random',
               rate_limit: Optional[float] = None):
    """
    Convenience function to run the proxy server.
    
    Args:
        host: Host to bind to
        port: Port to listen on
        use_free_proxies: Whether to fetch and use free proxies
        max_free_proxies: Maximum number of free proxies to fetch
        rotation_strategy: Rotation strategy ('random' or 'round-robin')
        rate_limit: Rate limit in requests per second
    """
    config = ProxyConfig(
        rotate_user_agent=True,
        rotate_ip=use_free_proxies,
        rotation_strategy=rotation_strategy,
        rate_limit=rate_limit,
        max_retries=3,
    )
    
    server = ProxyServer(
        host=host,
        port=port,
        config=config,
        use_free_proxies=use_free_proxies,
        max_free_proxies=max_free_proxies
    )
    
    server.start()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Proxyy Rotating Proxy Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on (default: 8080)')
    parser.add_argument('--free-proxies', action='store_true', help='Use free proxies from internet')
    parser.add_argument('--max-proxies', type=int, default=50, help='Max free proxies to fetch (default: 50)')
    parser.add_argument('--strategy', default='random', choices=['random', 'round-robin'], 
                       help='Rotation strategy (default: random)')
    parser.add_argument('--rate-limit', type=float, help='Rate limit in requests/second')
    
    args = parser.parse_args()
    
    run_server(
        host=args.host,
        port=args.port,
        use_free_proxies=args.free_proxies,
        max_free_proxies=args.max_proxies,
        rotation_strategy=args.strategy,
        rate_limit=args.rate_limit
    )
