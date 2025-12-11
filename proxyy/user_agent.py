"""
User-Agent rotation module for diverse browser emulation
"""

import random
from typing import List, Optional


class UserAgentRotator:
    """
    Manages rotation of user-agent strings to simulate different browsers and devices.
    Provides a diverse pool of realistic user-agents for better anonymity.
    """
    
    # Diverse pool of recent user-agents across different browsers and platforms
    DEFAULT_USER_AGENTS = [
        # Chrome on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        
        # Chrome on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        
        # Firefox on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        
        # Firefox on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
        
        # Safari on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        
        # Edge on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
        
        # Chrome on Linux
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        
        # Firefox on Linux
        "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
        
        # Mobile Chrome
        "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        
        # Mobile Safari
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    ]
    
    def __init__(self, user_agents: Optional[List[str]] = None):
        """
        Initialize the UserAgentRotator.
        
        Args:
            user_agents: Optional list of custom user-agent strings.
                        If not provided, uses DEFAULT_USER_AGENTS.
        """
        self.user_agents = user_agents if user_agents else self.DEFAULT_USER_AGENTS.copy()
        self._current_index = 0
        
    def get_random(self) -> str:
        """
        Get a random user-agent from the pool.
        
        Returns:
            A randomly selected user-agent string.
        """
        return random.choice(self.user_agents)
    
    def get_next(self) -> str:
        """
        Get the next user-agent in rotation (round-robin).
        
        Returns:
            The next user-agent string in the sequence.
        """
        user_agent = self.user_agents[self._current_index]
        self._current_index = (self._current_index + 1) % len(self.user_agents)
        return user_agent
    
    def add_user_agent(self, user_agent: str) -> None:
        """
        Add a custom user-agent to the pool.
        
        Args:
            user_agent: The user-agent string to add.
        """
        if user_agent and user_agent not in self.user_agents:
            self.user_agents.append(user_agent)
    
    def remove_user_agent(self, user_agent: str) -> None:
        """
        Remove a user-agent from the pool.
        
        Args:
            user_agent: The user-agent string to remove.
        """
        if user_agent in self.user_agents:
            self.user_agents.remove(user_agent)
    
    def reset(self) -> None:
        """Reset the rotation index to the beginning."""
        self._current_index = 0
    
    def __len__(self) -> int:
        """Return the number of user-agents in the pool."""
        return len(self.user_agents)
