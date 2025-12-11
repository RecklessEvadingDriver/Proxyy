"""
Main proxy module with rotating capabilities
"""

import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
import time
import logging

from .user_agent import UserAgentRotator
from .ip_rotation import IPRotator, ProxyInfo


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ProxyConfig:
    """
    Configuration for the RotatingProxy.
    """
    # Rotation settings
    rotate_user_agent: bool = True
    rotate_ip: bool = True
    rotation_strategy: str = "random"  # "random" or "round-robin"
    
    # Security settings
    verify_ssl: bool = True
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Rate limiting
    rate_limit: Optional[float] = None  # requests per second
    
    # Proxy pool
    proxies: List[ProxyInfo] = field(default_factory=list)
    
    # User-agent pool
    user_agents: Optional[List[str]] = None
    
    # Custom headers
    default_headers: Dict[str, str] = field(default_factory=dict)


class RotatingProxy:
    """
    A rotating proxy client that automatically rotates user-agents and IP addresses.
    Provides reliability through retries, rate limiting, and health checking.
    Can be used as a parameter or standalone client.
    """
    
    def __init__(self, config: Optional[ProxyConfig] = None):
        """
        Initialize the RotatingProxy.
        
        Args:
            config: ProxyConfig object with settings. If not provided, uses defaults.
        """
        self.config = config if config else ProxyConfig()
        
        # Initialize rotators
        self.ua_rotator = UserAgentRotator(self.config.user_agents)
        self.ip_rotator = IPRotator(self.config.proxies)
        
        # Rate limiting
        self._last_request_time = 0.0
        
        # Session for connection pooling (performance)
        self.session = requests.Session()
        
        # Apply default headers
        if self.config.default_headers:
            self.session.headers.update(self.config.default_headers)
    
    def _get_user_agent(self) -> str:
        """Get the next user-agent based on rotation strategy."""
        if self.config.rotation_strategy == "random":
            return self.ua_rotator.get_random()
        else:
            return self.ua_rotator.get_next()
    
    def _get_proxy(self) -> Optional[Dict[str, str]]:
        """Get the next proxy based on rotation strategy."""
        if not self.config.rotate_ip or not self.ip_rotator.proxies:
            return None
        
        if self.config.rotation_strategy == "random":
            proxy_info = self.ip_rotator.get_random()
        else:
            proxy_info = self.ip_rotator.get_next()
        
        return proxy_info.get_dict() if proxy_info else None
    
    def _apply_rate_limit(self) -> None:
        """Apply rate limiting if configured."""
        if self.config.rate_limit:
            min_interval = 1.0 / self.config.rate_limit
            elapsed = time.time() - self._last_request_time
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
        self._last_request_time = time.time()
    
    def _prepare_request_kwargs(self, **kwargs) -> Dict[str, Any]:
        """
        Prepare request kwargs with rotation and security settings.
        
        Args:
            **kwargs: Additional arguments to pass to requests.
        
        Returns:
            Dictionary of request arguments.
        """
        # Set user-agent if rotation enabled
        if self.config.rotate_user_agent:
            if "headers" not in kwargs:
                kwargs["headers"] = {}
            if "User-Agent" not in kwargs["headers"]:
                kwargs["headers"]["User-Agent"] = self._get_user_agent()
        
        # Set proxy if rotation enabled
        if self.config.rotate_ip and "proxies" not in kwargs:
            proxy = self._get_proxy()
            if proxy:
                kwargs["proxies"] = proxy
        
        # Set timeout
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.config.timeout
        
        # Set SSL verification
        if "verify" not in kwargs:
            kwargs["verify"] = self.config.verify_ssl
        
        return kwargs
    
    def request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> requests.Response:
        """
        Make an HTTP request with rotation and retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL to request
            **kwargs: Additional arguments to pass to requests
        
        Returns:
            requests.Response object
        
        Raises:
            requests.RequestException: If all retries fail
        """
        self._apply_rate_limit()
        
        last_exception = None
        current_proxy = None
        
        for attempt in range(self.config.max_retries):
            try:
                # Prepare request with rotation
                request_kwargs = self._prepare_request_kwargs(**kwargs)
                current_proxy = request_kwargs.get("proxies")
                
                # Log the request
                logger.debug(f"Attempt {attempt + 1}/{self.config.max_retries}: {method} {url}")
                
                # Make the request
                response = self.session.request(method, url, **request_kwargs)
                response.raise_for_status()
                
                return response
                
            except requests.RequestException as e:
                last_exception = e
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.config.max_retries}): {e}")
                
                # Mark proxy as failed if we used one
                if current_proxy and self.config.rotate_ip:
                    # Extract proxy from dict and mark as failed
                    for proxy_info in self.ip_rotator.proxies:
                        if proxy_info.get_dict() == current_proxy:
                            self.ip_rotator.mark_failed(proxy_info)
                            logger.info(f"Marked proxy as failed: {proxy_info.get_url()}")
                            break
                
                # Wait before retry
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay * (attempt + 1))
        
        # All retries failed
        raise last_exception
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """
        Make a GET request.
        
        Args:
            url: URL to request
            **kwargs: Additional arguments to pass to requests
        
        Returns:
            requests.Response object
        """
        return self.request("GET", url, **kwargs)
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """
        Make a POST request.
        
        Args:
            url: URL to request
            **kwargs: Additional arguments to pass to requests
        
        Returns:
            requests.Response object
        """
        return self.request("POST", url, **kwargs)
    
    def put(self, url: str, **kwargs) -> requests.Response:
        """
        Make a PUT request.
        
        Args:
            url: URL to request
            **kwargs: Additional arguments to pass to requests
        
        Returns:
            requests.Response object
        """
        return self.request("PUT", url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> requests.Response:
        """
        Make a DELETE request.
        
        Args:
            url: URL to request
            **kwargs: Additional arguments to pass to requests
        
        Returns:
            requests.Response object
        """
        return self.request("DELETE", url, **kwargs)
    
    def head(self, url: str, **kwargs) -> requests.Response:
        """
        Make a HEAD request.
        
        Args:
            url: URL to request
            **kwargs: Additional arguments to pass to requests
        
        Returns:
            requests.Response object
        """
        return self.request("HEAD", url, **kwargs)
    
    def options(self, url: str, **kwargs) -> requests.Response:
        """
        Make an OPTIONS request.
        
        Args:
            url: URL to request
            **kwargs: Additional arguments to pass to requests
        
        Returns:
            requests.Response object
        """
        return self.request("OPTIONS", url, **kwargs)
    
    def close(self) -> None:
        """Close the session and cleanup resources."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the proxy rotator.
        
        Returns:
            Dictionary with statistics.
        """
        return {
            "total_proxies": len(self.ip_rotator),
            "healthy_proxies": self.ip_rotator.healthy_count(),
            "total_user_agents": len(self.ua_rotator),
            "rotation_strategy": self.config.rotation_strategy,
            "rate_limit": self.config.rate_limit,
        }
