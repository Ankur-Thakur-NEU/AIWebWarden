#!/usr/bin/env python3
"""
Enterprise Integration & API Gateway
Provides enterprise-grade APIs, authentication, rate limiting, and integration capabilities
"""

import json
import time
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
from functools import wraps
import threading
from collections import defaultdict, deque

@dataclass
class APIKey:
    """API key with metadata."""
    key_id: str
    key_hash: str
    name: str
    permissions: List[str]
    rate_limit: int  # requests per minute
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool
    usage_count: int = 0
    last_used: Optional[datetime] = None

@dataclass
class APIRequest:
    """API request metadata."""
    request_id: str
    api_key_id: str
    endpoint: str
    method: str
    query: str
    response_time: float
    status_code: int
    timestamp: datetime
    ip_address: str
    user_agent: str

class RateLimiter:
    """Advanced rate limiting with multiple strategies."""
    
    def __init__(self):
        """Initialize rate limiter."""
        self.requests = defaultdict(deque)  # key_id -> deque of timestamps
        self.lock = threading.Lock()
    
    def is_allowed(self, key_id: str, limit: int, window_minutes: int = 1) -> bool:
        """Check if request is allowed under rate limit."""
        with self.lock:
            now = time.time()
            window_start = now - (window_minutes * 60)
            
            # Clean old requests
            while self.requests[key_id] and self.requests[key_id][0] < window_start:
                self.requests[key_id].popleft()
            
            # Check if under limit
            if len(self.requests[key_id]) < limit:
                self.requests[key_id].append(now)
                return True
            
            return False
    
    def get_remaining_requests(self, key_id: str, limit: int, window_minutes: int = 1) -> int:
        """Get remaining requests in current window."""
        with self.lock:
            now = time.time()
            window_start = now - (window_minutes * 60)
            
            # Clean old requests
            while self.requests[key_id] and self.requests[key_id][0] < window_start:
                self.requests[key_id].popleft()
            
            return max(0, limit - len(self.requests[key_id]))

class APIKeyManager:
    """Manages API keys and authentication."""
    
    def __init__(self, db_path: str = "enterprise.db"):
        """Initialize API key manager."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database for API keys."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    key_id TEXT PRIMARY KEY,
                    key_hash TEXT NOT NULL,
                    name TEXT NOT NULL,
                    permissions TEXT NOT NULL,
                    rate_limit INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    usage_count INTEGER DEFAULT 0,
                    last_used TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_requests (
                    request_id TEXT PRIMARY KEY,
                    api_key_id TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    method TEXT NOT NULL,
                    query TEXT,
                    response_time REAL NOT NULL,
                    status_code INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    FOREIGN KEY (api_key_id) REFERENCES api_keys (key_id)
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_api_key_hash ON api_keys(key_hash)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_request_timestamp ON api_requests(timestamp)")
    
    def create_api_key(self, name: str, permissions: List[str], rate_limit: int = 100, 
                      expires_days: Optional[int] = None) -> tuple[str, str]:
        """Create a new API key."""
        key_id = secrets.token_urlsafe(16)
        api_key = f"aiba_{secrets.token_urlsafe(32)}"  # AI Browser Assistant prefix
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        expires_at = None
        if expires_days:
            expires_at = datetime.now() + timedelta(days=expires_days)
        
        api_key_obj = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            name=name,
            permissions=permissions,
            rate_limit=rate_limit,
            created_at=datetime.now(),
            expires_at=expires_at,
            is_active=True
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO api_keys 
                (key_id, key_hash, name, permissions, rate_limit, created_at, expires_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                api_key_obj.key_id, api_key_obj.key_hash, api_key_obj.name,
                json.dumps(api_key_obj.permissions), api_key_obj.rate_limit,
                api_key_obj.created_at.isoformat(),
                api_key_obj.expires_at.isoformat() if api_key_obj.expires_at else None,
                api_key_obj.is_active
            ))
        
        return key_id, api_key
    
    def validate_api_key(self, api_key: str) -> Optional[APIKey]:
        """Validate API key and return key info."""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT key_id, key_hash, name, permissions, rate_limit, created_at, 
                       expires_at, is_active, usage_count, last_used
                FROM api_keys 
                WHERE key_hash = ? AND is_active = TRUE
            """, (key_hash,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Check expiration
            expires_at = datetime.fromisoformat(row[6]) if row[6] else None
            if expires_at and datetime.now() > expires_at:
                return None
            
            return APIKey(
                key_id=row[0],
                key_hash=row[1],
                name=row[2],
                permissions=json.loads(row[3]),
                rate_limit=row[4],
                created_at=datetime.fromisoformat(row[5]),
                expires_at=expires_at,
                is_active=row[7],
                usage_count=row[8],
                last_used=datetime.fromisoformat(row[9]) if row[9] else None
            )
    
    def update_usage(self, key_id: str):
        """Update API key usage statistics."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE api_keys 
                SET usage_count = usage_count + 1, last_used = ?
                WHERE key_id = ?
            """, (datetime.now().isoformat(), key_id))
    
    def log_request(self, request: APIRequest):
        """Log API request."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO api_requests 
                (request_id, api_key_id, endpoint, method, query, response_time, 
                 status_code, timestamp, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request.request_id, request.api_key_id, request.endpoint,
                request.method, request.query, request.response_time,
                request.status_code, request.timestamp.isoformat(),
                request.ip_address, request.user_agent
            ))
    
    def get_usage_stats(self, key_id: str, days: int = 30) -> Dict[str, Any]:
        """Get usage statistics for API key."""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Basic stats
            stats = conn.execute("""
                SELECT 
                    COUNT(*) as total_requests,
                    AVG(response_time) as avg_response_time,
                    COUNT(CASE WHEN status_code = 200 THEN 1 END) as successful_requests
                FROM api_requests 
                WHERE api_key_id = ? AND timestamp > ?
            """, (key_id, cutoff_date)).fetchone()
            
            # Daily usage
            daily_usage = conn.execute("""
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as request_count,
                    AVG(response_time) as avg_response_time
                FROM api_requests 
                WHERE api_key_id = ? AND timestamp > ?
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
            """, (key_id, cutoff_date)).fetchall()
            
            return {
                'total_requests': stats[0] or 0,
                'avg_response_time': round(stats[1] or 0, 2),
                'successful_requests': stats[2] or 0,
                'success_rate': round((stats[2] or 0) / max(stats[0] or 1, 1) * 100, 1),
                'daily_usage': [
                    {'date': row[0], 'requests': row[1], 'avg_time': round(row[2], 2)}
                    for row in daily_usage
                ]
            }

class EnterpriseAPIGateway:
    """Enterprise-grade API gateway with authentication, rate limiting, and monitoring."""
    
    def __init__(self):
        """Initialize API gateway."""
        self.key_manager = APIKeyManager()
        self.rate_limiter = RateLimiter()
        self.endpoints = {}
        self.middleware = []
        
    def register_endpoint(self, path: str, handler: Callable, 
                         required_permissions: List[str] = None,
                         rate_limit_override: Optional[int] = None):
        """Register an API endpoint."""
        self.endpoints[path] = {
            'handler': handler,
            'permissions': required_permissions or [],
            'rate_limit_override': rate_limit_override
        }
    
    def add_middleware(self, middleware_func: Callable):
        """Add middleware function."""
        self.middleware.append(middleware_func)
    
    def authenticate_request(self, api_key: str) -> tuple[bool, Optional[APIKey], str]:
        """Authenticate API request."""
        if not api_key:
            return False, None, "Missing API key"
        
        if not api_key.startswith('aiba_'):
            return False, None, "Invalid API key format"
        
        key_info = self.key_manager.validate_api_key(api_key)
        if not key_info:
            return False, None, "Invalid or expired API key"
        
        return True, key_info, "Authenticated"
    
    def check_permissions(self, key_info: APIKey, required_permissions: List[str]) -> bool:
        """Check if API key has required permissions."""
        if not required_permissions:
            return True
        
        # Check if key has admin permission (grants all access)
        if 'admin' in key_info.permissions:
            return True
        
        # Check specific permissions
        return all(perm in key_info.permissions for perm in required_permissions)
    
    def process_request(self, endpoint: str, method: str, api_key: str, 
                       query: str, ip_address: str = "unknown", 
                       user_agent: str = "unknown") -> Dict[str, Any]:
        """Process API request with full enterprise features."""
        request_id = secrets.token_urlsafe(16)
        start_time = time.time()
        
        try:
            # Authentication
            is_authenticated, key_info, auth_message = self.authenticate_request(api_key)
            if not is_authenticated:
                return {
                    'success': False,
                    'error': auth_message,
                    'status_code': 401,
                    'request_id': request_id
                }
            
            # Check if endpoint exists
            if endpoint not in self.endpoints:
                return {
                    'success': False,
                    'error': f"Endpoint '{endpoint}' not found",
                    'status_code': 404,
                    'request_id': request_id
                }
            
            endpoint_config = self.endpoints[endpoint]
            
            # Permission check
            if not self.check_permissions(key_info, endpoint_config['permissions']):
                return {
                    'success': False,
                    'error': "Insufficient permissions",
                    'status_code': 403,
                    'request_id': request_id
                }
            
            # Rate limiting
            rate_limit = endpoint_config.get('rate_limit_override', key_info.rate_limit)
            if not self.rate_limiter.is_allowed(key_info.key_id, rate_limit):
                remaining = self.rate_limiter.get_remaining_requests(key_info.key_id, rate_limit)
                return {
                    'success': False,
                    'error': "Rate limit exceeded",
                    'status_code': 429,
                    'request_id': request_id,
                    'rate_limit': {
                        'limit': rate_limit,
                        'remaining': remaining,
                        'reset_time': int(time.time() + 60)  # 1 minute window
                    }
                }
            
            # Apply middleware
            for middleware in self.middleware:
                result = middleware(endpoint, method, query, key_info)
                if result is not None:
                    return result
            
            # Execute handler
            response = endpoint_config['handler'](query)
            response_time = time.time() - start_time
            
            # Update usage statistics
            self.key_manager.update_usage(key_info.key_id)
            
            # Log request
            api_request = APIRequest(
                request_id=request_id,
                api_key_id=key_info.key_id,
                endpoint=endpoint,
                method=method,
                query=query,
                response_time=response_time,
                status_code=200,
                timestamp=datetime.now(),
                ip_address=ip_address,
                user_agent=user_agent
            )
            self.key_manager.log_request(api_request)
            
            # Get remaining rate limit
            remaining = self.rate_limiter.get_remaining_requests(key_info.key_id, rate_limit)
            
            return {
                'success': True,
                'data': response,
                'status_code': 200,
                'request_id': request_id,
                'response_time': round(response_time, 3),
                'rate_limit': {
                    'limit': rate_limit,
                    'remaining': remaining,
                    'reset_time': int(time.time() + 60)
                }
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            
            # Log failed request
            if 'key_info' in locals() and key_info:
                api_request = APIRequest(
                    request_id=request_id,
                    api_key_id=key_info.key_id,
                    endpoint=endpoint,
                    method=method,
                    query=query,
                    response_time=response_time,
                    status_code=500,
                    timestamp=datetime.now(),
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                self.key_manager.log_request(api_request)
            
            return {
                'success': False,
                'error': f"Internal server error: {str(e)}",
                'status_code': 500,
                'request_id': request_id,
                'response_time': round(response_time, 3)
            }

class EnterpriseIntegration:
    """Enterprise integration capabilities."""
    
    def __init__(self):
        """Initialize enterprise integration."""
        self.gateway = EnterpriseAPIGateway()
        self._setup_default_endpoints()
    
    def _setup_default_endpoints(self):
        """Setup default API endpoints."""
        from react_agent_simple import SimpleReActAgent
        
        # Initialize agent
        self.agent = SimpleReActAgent(verbose=False)
        
        # Register endpoints
        self.gateway.register_endpoint(
            '/query',
            self._handle_query,
            required_permissions=['query'],
            rate_limit_override=None
        )
        
        self.gateway.register_endpoint(
            '/health',
            self._handle_health,
            required_permissions=[],
            rate_limit_override=1000  # High limit for health checks
        )
        
        self.gateway.register_endpoint(
            '/stats',
            self._handle_stats,
            required_permissions=['analytics'],
            rate_limit_override=100
        )
    
    def _handle_query(self, query: str) -> Dict[str, Any]:
        """Handle query endpoint."""
        try:
            response = self.agent.query(query)
            return {
                'query': query,
                'response': response,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            raise Exception(f"Query processing failed: {str(e)}")
    
    def _handle_health(self, query: str) -> Dict[str, Any]:
        """Handle health check endpoint."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'uptime': time.time()  # Simple uptime metric
        }
    
    def _handle_stats(self, query: str) -> Dict[str, Any]:
        """Handle statistics endpoint."""
        # This would integrate with analytics dashboard
        return {
            'message': 'Statistics endpoint - integrate with analytics dashboard',
            'timestamp': datetime.now().isoformat()
        }
    
    def create_client_credentials(self, client_name: str, permissions: List[str], 
                                rate_limit: int = 100) -> Dict[str, Any]:
        """Create API credentials for a client."""
        key_id, api_key = self.gateway.key_manager.create_api_key(
            name=client_name,
            permissions=permissions,
            rate_limit=rate_limit
        )
        
        return {
            'client_name': client_name,
            'key_id': key_id,
            'api_key': api_key,
            'permissions': permissions,
            'rate_limit': rate_limit,
            'created_at': datetime.now().isoformat(),
            'usage_instructions': {
                'authentication': 'Include API key in Authorization header: Bearer <api_key>',
                'endpoints': list(self.gateway.endpoints.keys()),
                'rate_limiting': f'Maximum {rate_limit} requests per minute'
            }
        }
    
    def get_client_dashboard(self, api_key: str) -> Dict[str, Any]:
        """Get client dashboard with usage statistics."""
        is_authenticated, key_info, _ = self.gateway.authenticate_request(api_key)
        
        if not is_authenticated or not key_info:
            return {'error': 'Invalid API key'}
        
        usage_stats = self.gateway.key_manager.get_usage_stats(key_info.key_id)
        
        return {
            'client_info': {
                'name': key_info.name,
                'key_id': key_info.key_id,
                'permissions': key_info.permissions,
                'rate_limit': key_info.rate_limit,
                'created_at': key_info.created_at.isoformat(),
                'last_used': key_info.last_used.isoformat() if key_info.last_used else None
            },
            'usage_statistics': usage_stats,
            'available_endpoints': [
                {
                    'path': path,
                    'permissions': config['permissions'],
                    'rate_limit': config.get('rate_limit_override', key_info.rate_limit)
                }
                for path, config in self.gateway.endpoints.items()
                if self.gateway.check_permissions(key_info, config['permissions'])
            ]
        }

# Demo and testing functions
def demo_enterprise_integration():
    """Demonstrate enterprise integration capabilities."""
    print("🏢 ENTERPRISE INTEGRATION DEMO")
    print("="*50)
    
    # Initialize enterprise integration
    integration = EnterpriseIntegration()
    
    # Create test client credentials
    print("🔑 Creating client credentials...")
    
    credentials = integration.create_client_credentials(
        client_name="Demo Client",
        permissions=["query", "analytics"],
        rate_limit=50
    )
    
    print(f"✅ Client created: {credentials['client_name']}")
    print(f"   Key ID: {credentials['key_id']}")
    print(f"   API Key: {credentials['api_key'][:20]}...")
    print(f"   Permissions: {credentials['permissions']}")
    
    # Test API requests
    print(f"\n🧪 Testing API endpoints...")
    
    api_key = credentials['api_key']
    
    # Test health endpoint
    health_response = integration.gateway.process_request(
        endpoint='/health',
        method='GET',
        api_key=api_key,
        query='',
        ip_address='127.0.0.1',
        user_agent='Demo Client'
    )
    
    print(f"🏥 Health check: {health_response['success']} - {health_response.get('status_code', 'N/A')}")
    
    # Test query endpoint
    query_response = integration.gateway.process_request(
        endpoint='/query',
        method='POST',
        api_key=api_key,
        query='What is artificial intelligence?',
        ip_address='127.0.0.1',
        user_agent='Demo Client'
    )
    
    print(f"🔍 Query test: {query_response['success']} - Response time: {query_response.get('response_time', 'N/A')}s")
    
    # Test rate limiting
    print(f"\n⚡ Testing rate limiting...")
    
    rate_limit_tests = 0
    for i in range(5):
        response = integration.gateway.process_request(
            endpoint='/health',
            method='GET',
            api_key=api_key,
            query='',
            ip_address='127.0.0.1',
            user_agent='Rate Limit Test'
        )
        
        if response['success']:
            rate_limit_tests += 1
        
        remaining = response.get('rate_limit', {}).get('remaining', 'N/A')
        print(f"   Request {i+1}: Success={response['success']}, Remaining={remaining}")
    
    # Get client dashboard
    print(f"\n📊 Client dashboard...")
    dashboard = integration.get_client_dashboard(api_key)
    
    if 'error' not in dashboard:
        print(f"   Total requests: {dashboard['usage_statistics']['total_requests']}")
        print(f"   Success rate: {dashboard['usage_statistics']['success_rate']}%")
        print(f"   Available endpoints: {len(dashboard['available_endpoints'])}")
    
    print(f"\n✅ Enterprise integration demo completed!")
    
    return {
        'credentials': credentials,
        'test_results': {
            'health_check': health_response['success'],
            'query_test': query_response['success'],
            'rate_limit_tests': rate_limit_tests
        }
    }

if __name__ == "__main__":
    demo_enterprise_integration()
