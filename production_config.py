#!/usr/bin/env python3
"""
Production Configuration and Optimization Settings
Optimized settings for different deployment scenarios
"""

import os
from typing import Dict, Any

class ProductionConfig:
    """Production-ready configuration settings."""
    
    # Performance Optimization Settings
    PERFORMANCE_SETTINGS = {
        'demo_mode': {
            'max_iterations': 2,
            'max_response_length': 1500,
            'tool_timeout': 10,
            'max_search_results': 2,
            'max_scrape_chars': 1000,
            'enable_caching': True,
            'verbose_mode': True
        },
        'production_mode': {
            'max_iterations': 3,
            'max_response_length': 2000,
            'tool_timeout': 15,
            'max_search_results': 3,
            'max_scrape_chars': 1500,
            'enable_caching': True,
            'verbose_mode': False
        },
        'development_mode': {
            'max_iterations': 5,
            'max_response_length': 3000,
            'tool_timeout': 30,
            'max_search_results': 5,
            'max_scrape_chars': 2000,
            'enable_caching': False,
            'verbose_mode': True
        }
    }
    
    # Error Handling Settings
    ERROR_HANDLING = {
        'max_retries': 3,
        'retry_delay': 1.0,
        'graceful_degradation': True,
        'fallback_responses': {
            'network_error': "I'm experiencing network connectivity issues. Please try again in a moment.",
            'api_error': "I'm having trouble processing your request. Please try rephrasing your question.",
            'timeout_error': "Your request is taking longer than expected. Please try a simpler query.",
            'rate_limit': "I'm currently processing many requests. Please wait a moment and try again."
        }
    }
    
    # Model Configuration
    MODEL_CONFIG = {
        'default_model': 'llama3.1-8b',
        'fallback_model': 'llama3.1-8b',
        'max_tokens': {
            'planning': 150,
            'synthesis': 400,
            'fallback': 200
        },
        'temperature': 0.7
    }
    
    # Monitoring and Logging
    MONITORING = {
        'enable_performance_tracking': True,
        'enable_error_logging': True,
        'log_level': 'INFO',
        'metrics_retention_days': 7,
        'alert_thresholds': {
            'response_time': 10.0,  # seconds
            'error_rate': 0.1,      # 10%
            'success_rate': 0.9     # 90%
        }
    }
    
    @classmethod
    def get_config(cls, mode: str = 'production') -> Dict[str, Any]:
        """Get configuration for specified mode."""
        if mode not in cls.PERFORMANCE_SETTINGS:
            mode = 'production'
        
        config = {
            'performance': cls.PERFORMANCE_SETTINGS[mode],
            'error_handling': cls.ERROR_HANDLING,
            'model': cls.MODEL_CONFIG,
            'monitoring': cls.MONITORING,
            'mode': mode
        }
        
        return config
    
    @classmethod
    def validate_environment(cls) -> Dict[str, bool]:
        """Validate environment setup."""
        checks = {
            'api_key_present': bool(os.getenv('CEREBRAS_API_KEY')),
            'api_key_valid': len(os.getenv('CEREBRAS_API_KEY', '')) > 10,
            'dependencies_available': True,  # Would check imports in real implementation
            'network_connectivity': True,    # Would check network in real implementation
        }
        
        return checks
    
    @classmethod
    def get_optimization_recommendations(cls, performance_stats: Dict[str, Any]) -> list:
        """Get optimization recommendations based on performance stats."""
        recommendations = []
        
        avg_response_time = performance_stats.get('avg_response_time', 0)
        if avg_response_time > 8:
            recommendations.append("Consider enabling demo mode for faster responses")
        
        cache_hit_rate = performance_stats.get('cache_hits', 0) / max(performance_stats.get('total_queries', 1), 1)
        if cache_hit_rate < 0.2:
            recommendations.append("Enable caching to improve response times")
        
        error_rate = 1 - (performance_stats.get('successful_queries', 0) / max(performance_stats.get('total_queries', 1), 1))
        if error_rate > 0.1:
            recommendations.append("Review error handling and tool reliability")
        
        return recommendations

class ProductionAgent:
    """Production-ready agent with optimized configuration."""
    
    def __init__(self, mode: str = 'production'):
        """Initialize production agent."""
        self.config = ProductionConfig.get_config(mode)
        self.mode = mode
        self.stats = {
            'total_queries': 0,
            'successful_queries': 0,
            'avg_response_time': 0,
            'cache_hits': 0,
            'errors': []
        }
        
        # Validate environment
        env_checks = ProductionConfig.validate_environment()
        if not all(env_checks.values()):
            print("⚠️ Environment validation warnings:")
            for check, status in env_checks.items():
                if not status:
                    print(f"   ❌ {check}")
        
        print(f"🚀 Production Agent initialized in {mode} mode")
        print(f"⚡ Performance optimizations: {len(self.config['performance'])} settings applied")
    
    def process_query_with_monitoring(self, query: str) -> Dict[str, Any]:
        """Process query with comprehensive monitoring."""
        import time
        
        start_time = time.time()
        self.stats['total_queries'] += 1
        
        result = {
            'query': query,
            'success': False,
            'response': '',
            'duration': 0,
            'error': None,
            'mode': self.mode
        }
        
        try:
            # Import and use optimized agent
            from react_agent_optimized import OptimizedReActAgent
            
            agent = OptimizedReActAgent(
                verbose=self.config['performance']['verbose_mode'],
                max_iterations=self.config['performance']['max_iterations']
            )
            
            # Apply production optimizations
            if self.mode == 'demo_mode':
                agent.optimize_for_demo()
            
            response = agent.query(query)
            
            duration = time.time() - start_time
            
            result.update({
                'success': True,
                'response': response,
                'duration': duration
            })
            
            self.stats['successful_queries'] += 1
            
            # Update average response time
            self.stats['avg_response_time'] = (
                (self.stats['avg_response_time'] * (self.stats['total_queries'] - 1) + duration) 
                / self.stats['total_queries']
            )
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            
            result.update({
                'success': False,
                'response': self._get_fallback_response(error_msg),
                'duration': duration,
                'error': error_msg
            })
            
            self.stats['errors'].append({
                'query': query,
                'error': error_msg,
                'timestamp': time.time()
            })
        
        return result
    
    def _get_fallback_response(self, error_msg: str) -> str:
        """Get appropriate fallback response based on error type."""
        error_msg_lower = error_msg.lower()
        
        fallbacks = self.config['error_handling']['fallback_responses']
        
        if 'network' in error_msg_lower or 'connection' in error_msg_lower:
            return fallbacks['network_error']
        elif 'timeout' in error_msg_lower:
            return fallbacks['timeout_error']
        elif 'rate' in error_msg_lower or 'limit' in error_msg_lower:
            return fallbacks['rate_limit']
        else:
            return fallbacks['api_error']
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status and recommendations."""
        if self.stats['total_queries'] == 0:
            return {'status': 'ready', 'message': 'Agent ready for queries'}
        
        success_rate = self.stats['successful_queries'] / self.stats['total_queries']
        avg_time = self.stats['avg_response_time']
        
        status = 'healthy'
        if success_rate < 0.9:
            status = 'degraded'
        if avg_time > 10:
            status = 'slow'
        if success_rate < 0.5:
            status = 'critical'
        
        recommendations = ProductionConfig.get_optimization_recommendations(self.stats)
        
        return {
            'status': status,
            'success_rate': success_rate,
            'avg_response_time': avg_time,
            'total_queries': self.stats['total_queries'],
            'recommendations': recommendations,
            'mode': self.mode
        }

def run_production_test():
    """Run production configuration test."""
    print("🏭 PRODUCTION CONFIGURATION TEST")
    print("="*50)
    
    modes = ['demo_mode', 'production_mode', 'development_mode']
    
    for mode in modes:
        print(f"\n🧪 Testing {mode}...")
        
        agent = ProductionAgent(mode=mode)
        
        # Test with a simple query
        result = agent.process_query_with_monitoring("What is Python programming?")
        
        print(f"✅ {mode}: {result['success']} - {result['duration']:.2f}s")
        
        # Show health status
        health = agent.get_health_status()
        print(f"   Status: {health['status']} - Success rate: {health['success_rate']:.1%}")
        
        if health['recommendations']:
            print(f"   Recommendations: {len(health['recommendations'])} available")

if __name__ == "__main__":
    run_production_test()