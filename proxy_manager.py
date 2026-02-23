"""
Proxy Rotation Manager for Residential Proxies
"""
import random
import time
from typing import List, Optional, Dict
from collections import defaultdict
import requests
from retrying import retry


class ProxyManager:
    """Manages rotation and health checking of residential proxies"""
    
    def __init__(self, proxies: List[str], rotation_strategy: str = 'round_robin'):
        """
        Initialize proxy manager
        
        Args:
            proxies: List of proxy URLs in format 'http://user:pass@host:port'
            rotation_strategy: 'round_robin', 'random', or 'least_used'
        """
        self.proxies = proxies
        self.rotation_strategy = rotation_strategy
        self.current_index = 0
        self.proxy_stats = defaultdict(lambda: {'success': 0, 'failures': 0, 'last_used': 0})
        self.failed_proxies = set()
        
    def get_proxy(self) -> Optional[Dict[str, str]]:
        """Get next proxy based on rotation strategy"""
        if not self.proxies:
            return None
            
        available_proxies = [p for p in self.proxies if p not in self.failed_proxies]
        
        if not available_proxies:
            # Reset failed proxies if all are marked as failed
            self.failed_proxies.clear()
            available_proxies = self.proxies
            
        if self.rotation_strategy == 'round_robin':
            proxy = available_proxies[self.current_index % len(available_proxies)]
            self.current_index += 1
        elif self.rotation_strategy == 'random':
            proxy = random.choice(available_proxies)
        elif self.rotation_strategy == 'least_used':
            proxy = min(available_proxies, 
                       key=lambda p: self.proxy_stats[p]['success'] + self.proxy_stats[p]['failures'])
        else:
            proxy = available_proxies[0]
            
        return {
            'http': proxy,
            'https': proxy
        }
    
    def mark_success(self, proxy: str):
        """Mark proxy as successful"""
        if proxy in self.proxy_stats:
            self.proxy_stats[proxy]['success'] += 1
            self.proxy_stats[proxy]['last_used'] = time.time()
            if proxy in self.failed_proxies:
                self.failed_proxies.remove(proxy)
    
    def mark_failure(self, proxy: str):
        """Mark proxy as failed"""
        if proxy in self.proxy_stats:
            self.proxy_stats[proxy]['failures'] += 1
            if self.proxy_stats[proxy]['failures'] > 3:
                self.failed_proxies.add(proxy)
    
    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def test_proxy(self, proxy: Dict[str, str], test_url: str = 'https://httpbin.org/ip') -> bool:
        """Test if proxy is working"""
        try:
            response = requests.get(
                test_url,
                proxies=proxy,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Proxy test failed: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get statistics about proxy usage"""
        return {
            'total_proxies': len(self.proxies),
            'active_proxies': len(self.proxies) - len(self.failed_proxies),
            'failed_proxies': len(self.failed_proxies),
            'proxy_stats': dict(self.proxy_stats)
        }
