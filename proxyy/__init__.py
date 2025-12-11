"""
Proxyy - A rotating proxy library with user-agent and IP rotation
"""

__version__ = "1.0.0"
__author__ = "RecklessEvadingDriver"

from .proxy import RotatingProxy, ProxyConfig
from .user_agent import UserAgentRotator
from .ip_rotation import IPRotator, ProxyInfo

__all__ = ["RotatingProxy", "ProxyConfig", "UserAgentRotator", "IPRotator", "ProxyInfo"]
