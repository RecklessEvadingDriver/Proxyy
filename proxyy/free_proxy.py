"""
Free proxy fetcher module - retrieves proxies from public sources
"""

import requests
import logging
from typing import List, Optional
from .ip_rotation import ProxyInfo

logger = logging.getLogger(__name__)


class FreeProxyFetcher:
    """
    Fetches free proxies from public sources on the internet.
    Supports multiple providers for better availability.
    """
    
    # Public free proxy APIs
    PROXY_SOURCES = [
        "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
        "https://www.proxy-list.download/api/v1/get?type=http",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    ]
    
    def __init__(self, timeout: int = 10, max_proxies: Optional[int] = None):
        """
        Initialize the FreeProxyFetcher.
        
        Args:
            timeout: Timeout for fetching proxies (seconds)
            max_proxies: Maximum number of proxies to return (None = all)
        """
        self.timeout = timeout
        self.max_proxies = max_proxies
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_from_url(self, url: str) -> List[ProxyInfo]:
        """
        Fetch proxies from a single URL.
        
        Args:
            url: URL to fetch proxies from
            
        Returns:
            List of ProxyInfo objects
        """
        proxies = []
        try:
            logger.info(f"Fetching proxies from {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse proxy list (format: IP:PORT or just IP:PORT per line)
            lines = response.text.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Handle different formats
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        host = parts[0].strip()
                        try:
                            port = int(parts[1].strip())
                            # Validate IP format
                            if self._is_valid_host(host) and 1 <= port <= 65535:
                                proxy = ProxyInfo(
                                    host=host,
                                    port=port,
                                    protocol="http"
                                )
                                proxies.append(proxy)
                        except ValueError:
                            continue
            
            logger.info(f"Fetched {len(proxies)} proxies from {url}")
            
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch proxies from {url}: {e}")
        except Exception as e:
            logger.error(f"Error parsing proxies from {url}: {e}")
        
        return proxies
    
    def _is_valid_host(self, host: str) -> bool:
        """
        Validate if host is a valid IP address or hostname.
        
        Args:
            host: Host string to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Basic validation - check for valid characters
        if not host or len(host) > 253:
            return False
        
        # Check if it's an IP address
        parts = host.split('.')
        if len(parts) == 4:
            try:
                return all(0 <= int(part) <= 255 for part in parts)
            except ValueError:
                pass
        
        # Check if it's a valid hostname
        return all(c.isalnum() or c in '.-' for c in host)
    
    def fetch_all(self) -> List[ProxyInfo]:
        """
        Fetch proxies from all configured sources.
        
        Returns:
            List of unique ProxyInfo objects
        """
        all_proxies = []
        seen = set()
        
        for source_url in self.PROXY_SOURCES:
            try:
                proxies = self.fetch_from_url(source_url)
                
                # Deduplicate
                for proxy in proxies:
                    proxy_key = f"{proxy.host}:{proxy.port}"
                    if proxy_key not in seen:
                        seen.add(proxy_key)
                        all_proxies.append(proxy)
                        
                        # Check if we've reached the limit
                        if self.max_proxies and len(all_proxies) >= self.max_proxies:
                            logger.info(f"Reached max_proxies limit: {self.max_proxies}")
                            return all_proxies
                            
            except Exception as e:
                logger.warning(f"Error fetching from source: {e}")
                continue
        
        logger.info(f"Total unique proxies fetched: {len(all_proxies)}")
        return all_proxies
    
    def fetch_and_test(self, test_url: str = "http://httpbin.org/ip", 
                      test_timeout: int = 5) -> List[ProxyInfo]:
        """
        Fetch proxies and test them for connectivity.
        
        Args:
            test_url: URL to test proxies against
            test_timeout: Timeout for testing each proxy
            
        Returns:
            List of working ProxyInfo objects
        """
        all_proxies = self.fetch_all()
        working_proxies = []
        
        logger.info(f"Testing {len(all_proxies)} proxies...")
        
        for proxy in all_proxies:
            try:
                proxy_dict = proxy.get_dict()
                response = self.session.get(
                    test_url,
                    proxies=proxy_dict,
                    timeout=test_timeout
                )
                if response.status_code == 200:
                    working_proxies.append(proxy)
                    logger.debug(f"✓ Working proxy: {proxy.host}:{proxy.port}")
            except Exception:
                # Proxy failed, skip it
                pass
            
            # Check limit
            if self.max_proxies and len(working_proxies) >= self.max_proxies:
                break
        
        logger.info(f"Found {len(working_proxies)} working proxies")
        return working_proxies
    
    def close(self):
        """Close the session."""
        self.session.close()


def get_free_proxies(max_proxies: Optional[int] = 50, 
                     test_proxies: bool = False) -> List[ProxyInfo]:
    """
    Convenience function to get free proxies.
    
    Args:
        max_proxies: Maximum number of proxies to return
        test_proxies: Whether to test proxies before returning (slower but more reliable)
        
    Returns:
        List of ProxyInfo objects
    """
    fetcher = FreeProxyFetcher(max_proxies=max_proxies)
    try:
        if test_proxies:
            return fetcher.fetch_and_test()
        else:
            return fetcher.fetch_all()
    finally:
        fetcher.close()
