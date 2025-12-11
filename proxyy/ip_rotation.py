"""
IP rotation module for managing multiple proxy backends
"""

import random
from typing import List, Optional, Dict
from dataclasses import dataclass
import time


@dataclass
class ProxyInfo:
    """
    Information about a proxy server.
    """
    host: str
    port: int
    protocol: str = "http"  # http, https, socks4, socks5
    username: Optional[str] = None
    password: Optional[str] = None
    
    def get_url(self) -> str:
        """
        Get the full proxy URL.
        
        Returns:
            Full proxy URL string.
        """
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"
    
    def get_dict(self) -> Dict[str, str]:
        """
        Get proxy as a dictionary for requests library.
        
        Returns:
            Dictionary with proxy URLs for http and https.
        """
        proxy_url = self.get_url()
        return {
            "http": proxy_url,
            "https": proxy_url
        }


class IPRotator:
    """
    Manages rotation of IP addresses through multiple proxy servers.
    Supports health checking and automatic failover.
    """
    
    def __init__(self, proxies: Optional[List[ProxyInfo]] = None):
        """
        Initialize the IPRotator.
        
        Args:
            proxies: Optional list of ProxyInfo objects.
                    If not provided, operates in direct connection mode.
        """
        self.proxies = proxies if proxies else []
        self._current_index = 0
        self._failed_proxies: Dict[str, float] = {}  # proxy_url: failed_timestamp
        self._failure_timeout = 300  # 5 minutes before retry
        
    def add_proxy(self, proxy: ProxyInfo) -> None:
        """
        Add a proxy to the rotation pool.
        
        Args:
            proxy: ProxyInfo object to add.
        """
        if proxy not in self.proxies:
            self.proxies.append(proxy)
    
    def remove_proxy(self, proxy: ProxyInfo) -> None:
        """
        Remove a proxy from the rotation pool.
        
        Args:
            proxy: ProxyInfo object to remove.
        """
        if proxy in self.proxies:
            self.proxies.remove(proxy)
    
    def get_random(self) -> Optional[ProxyInfo]:
        """
        Get a random healthy proxy from the pool.
        
        Returns:
            A randomly selected healthy ProxyInfo object, or None if no proxies available.
        """
        available = self._get_healthy_proxies()
        if not available:
            return None
        return random.choice(available)
    
    def get_next(self) -> Optional[ProxyInfo]:
        """
        Get the next proxy in rotation (round-robin).
        
        Returns:
            The next healthy ProxyInfo object in the sequence, or None if no proxies available.
        """
        available = self._get_healthy_proxies()
        if not available:
            return None
        
        # Find next healthy proxy
        attempts = 0
        while attempts < len(self.proxies):
            proxy = self.proxies[self._current_index]
            self._current_index = (self._current_index + 1) % len(self.proxies)
            
            if proxy in available:
                return proxy
            attempts += 1
        
        return None
    
    def mark_failed(self, proxy: ProxyInfo) -> None:
        """
        Mark a proxy as failed for temporary removal from rotation.
        
        Args:
            proxy: The ProxyInfo object that failed.
        """
        self._failed_proxies[proxy.get_url()] = time.time()
    
    def _get_healthy_proxies(self) -> List[ProxyInfo]:
        """
        Get list of healthy proxies (not recently failed).
        
        Returns:
            List of healthy ProxyInfo objects.
        """
        current_time = time.time()
        healthy = []
        
        # Clean up old failures
        expired_failures = [
            url for url, timestamp in self._failed_proxies.items()
            if current_time - timestamp > self._failure_timeout
        ]
        for url in expired_failures:
            del self._failed_proxies[url]
        
        # Return proxies not in failed list
        for proxy in self.proxies:
            if proxy.get_url() not in self._failed_proxies:
                healthy.append(proxy)
        
        return healthy
    
    def reset(self) -> None:
        """Reset the rotation index and clear failed proxies."""
        self._current_index = 0
        self._failed_proxies.clear()
    
    def __len__(self) -> int:
        """Return the number of proxies in the pool."""
        return len(self.proxies)
    
    def healthy_count(self) -> int:
        """Return the number of healthy proxies."""
        return len(self._get_healthy_proxies())
