#!/usr/bin/env python3
"""
Advanced Caching and Performance Enhancement Layer
Implements intelligent caching, response optimization, and performance monitoring
"""

import json
import time
import hashlib
import sqlite3
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path

@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    query_hash: str
    query: str
    response: str
    timestamp: float
    access_count: int
    response_time: float
    quality_score: float

class IntelligentCache:
    """Advanced caching system with intelligent eviction and optimization."""
    
    def __init__(self, cache_dir: str = "cache", max_entries: int = 1000):
        """Initialize the intelligent cache."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_entries = max_entries
        self.db_path = self.cache_dir / "cache.db"
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for cache."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    query_hash TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    access_count INTEGER DEFAULT 1,
                    response_time REAL NOT NULL,
                    quality_score REAL DEFAULT 1.0,
                    created_at REAL DEFAULT (julianday('now'))
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON cache_entries(timestamp);
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_access_count ON cache_entries(access_count);
            """)
    
    def _hash_query(self, query: str) -> str:
        """Create a hash for the query."""
        return hashlib.sha256(query.lower().strip().encode()).hexdigest()[:16]
    
    def _calculate_quality_score(self, response: str, response_time: float) -> float:
        """Calculate quality score for response."""
        # Base score from response length and content quality
        length_score = min(len(response) / 1000, 1.0)  # Normalize to 0-1
        
        # Penalty for errors
        error_penalty = 0.5 if "error" in response.lower() else 0
        
        # Speed bonus
        speed_bonus = max(0, (10 - response_time) / 10) * 0.2
        
        # Source bonus
        source_bonus = 0.2 if "http" in response else 0
        
        return max(0, length_score + speed_bonus + source_bonus - error_penalty)
    
    def get(self, query: str) -> Optional[str]:
        """Get cached response if available."""
        query_hash = self._hash_query(query)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT response, access_count FROM cache_entries 
                WHERE query_hash = ? AND timestamp > ?
            """, (query_hash, time.time() - 86400))  # 24 hour TTL
            
            result = cursor.fetchone()
            if result:
                response, access_count = result
                
                # Update access count
                conn.execute("""
                    UPDATE cache_entries 
                    SET access_count = access_count + 1, timestamp = ?
                    WHERE query_hash = ?
                """, (time.time(), query_hash))
                
                return response
        
        return None
    
    def set(self, query: str, response: str, response_time: float):
        """Cache a response with metadata."""
        query_hash = self._hash_query(query)
        quality_score = self._calculate_quality_score(response, response_time)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO cache_entries 
                (query_hash, query, response, timestamp, response_time, quality_score)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (query_hash, query, response, time.time(), response_time, quality_score))
            
            # Cleanup old entries if needed
            self._cleanup_cache(conn)
    
    def _cleanup_cache(self, conn):
        """Remove old or low-quality entries."""
        # Count current entries
        count = conn.execute("SELECT COUNT(*) FROM cache_entries").fetchone()[0]
        
        if count > self.max_entries:
            # Remove entries with lowest score (quality * access_count)
            entries_to_remove = count - int(self.max_entries * 0.8)
            conn.execute("""
                DELETE FROM cache_entries 
                WHERE query_hash IN (
                    SELECT query_hash FROM cache_entries 
                    ORDER BY (quality_score * access_count) ASC 
                    LIMIT ?
                )
            """, (entries_to_remove,))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            # Basic stats
            stats['total_entries'] = conn.execute("SELECT COUNT(*) FROM cache_entries").fetchone()[0]
            stats['avg_quality'] = conn.execute("SELECT AVG(quality_score) FROM cache_entries").fetchone()[0] or 0
            stats['avg_access_count'] = conn.execute("SELECT AVG(access_count) FROM cache_entries").fetchone()[0] or 0
            
            # Top queries
            top_queries = conn.execute("""
                SELECT query, access_count FROM cache_entries 
                ORDER BY access_count DESC LIMIT 5
            """).fetchall()
            stats['top_queries'] = [{'query': q[:50] + '...', 'count': c} for q, c in top_queries]
            
            return stats

class PerformanceOptimizer:
    """Advanced performance optimization and monitoring."""
    
    def __init__(self):
        """Initialize performance optimizer."""
        self.metrics = {
            'total_queries': 0,
            'cache_hits': 0,
            'avg_response_time': 0,
            'response_times': [],
            'error_count': 0,
            'optimization_applied': 0
        }
        self.cache = IntelligentCache()
    
    def optimize_query(self, query: str) -> str:
        """Optimize query for better performance."""
        # Remove redundant words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = query.lower().split()
        optimized_words = [w for w in words if w not in stop_words or len(words) <= 3]
        
        # Limit query length
        if len(' '.join(optimized_words)) > 200:
            optimized_words = optimized_words[:20]
            self.metrics['optimization_applied'] += 1
        
        return ' '.join(optimized_words)
    
    def process_with_optimization(self, query: str, agent_function) -> Dict[str, Any]:
        """Process query with full optimization pipeline."""
        start_time = time.time()
        self.metrics['total_queries'] += 1
        
        # Check cache first
        cached_response = self.cache.get(query)
        if cached_response:
            self.metrics['cache_hits'] += 1
            return {
                'response': cached_response,
                'duration': 0.001,  # Near-instant cache hit
                'cached': True,
                'optimized': False
            }
        
        # Optimize query
        optimized_query = self.optimize_query(query)
        
        try:
            # Execute with optimized query
            response = agent_function(optimized_query)
            duration = time.time() - start_time
            
            # Cache the result
            self.cache.set(query, response, duration)
            
            # Update metrics
            self.metrics['response_times'].append(duration)
            if len(self.metrics['response_times']) > 100:
                self.metrics['response_times'] = self.metrics['response_times'][-100:]
            
            self.metrics['avg_response_time'] = sum(self.metrics['response_times']) / len(self.metrics['response_times'])
            
            return {
                'response': response,
                'duration': duration,
                'cached': False,
                'optimized': optimized_query != query
            }
            
        except Exception as e:
            self.metrics['error_count'] += 1
            raise e
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        cache_stats = self.cache.get_stats()
        
        cache_hit_rate = (self.metrics['cache_hits'] / max(self.metrics['total_queries'], 1)) * 100
        
        return {
            'total_queries': self.metrics['total_queries'],
            'cache_hit_rate': cache_hit_rate,
            'avg_response_time': self.metrics['avg_response_time'],
            'error_rate': (self.metrics['error_count'] / max(self.metrics['total_queries'], 1)) * 100,
            'optimizations_applied': self.metrics['optimization_applied'],
            'cache_stats': cache_stats,
            'performance_grade': self._calculate_grade(cache_hit_rate, self.metrics['avg_response_time'])
        }
    
    def _calculate_grade(self, cache_hit_rate: float, avg_response_time: float) -> str:
        """Calculate performance grade."""
        score = 0
        
        # Cache performance (40% of score)
        if cache_hit_rate > 50:
            score += 40
        elif cache_hit_rate > 25:
            score += 30
        elif cache_hit_rate > 10:
            score += 20
        
        # Response time performance (40% of score)
        if avg_response_time < 2:
            score += 40
        elif avg_response_time < 5:
            score += 30
        elif avg_response_time < 10:
            score += 20
        
        # Error rate (20% of score)
        error_rate = (self.metrics['error_count'] / max(self.metrics['total_queries'], 1)) * 100
        if error_rate < 5:
            score += 20
        elif error_rate < 10:
            score += 15
        elif error_rate < 20:
            score += 10
        
        if score >= 90:
            return "A+ (Excellent)"
        elif score >= 80:
            return "A (Very Good)"
        elif score >= 70:
            return "B (Good)"
        elif score >= 60:
            return "C (Fair)"
        else:
            return "D (Needs Improvement)"

# Demo function
def demo_enhanced_performance():
    """Demonstrate enhanced performance features."""
    print("🚀 ENHANCED PERFORMANCE DEMO")
    print("="*50)
    
    optimizer = PerformanceOptimizer()
    
    # Simulate agent function
    def mock_agent(query):
        import time
        time.sleep(1)  # Simulate processing time
        return f"Mock response for: {query}"
    
    # Test queries
    test_queries = [
        "What is artificial intelligence?",
        "What is artificial intelligence?",  # Duplicate for cache test
        "Find the best programming languages to learn in 2024",
        "What is artificial intelligence?",  # Another duplicate
    ]
    
    print("Testing performance optimization...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🧪 Query {i}: '{query[:50]}...'")
        
        result = optimizer.process_with_optimization(query, mock_agent)
        
        status = "⚡ CACHED" if result['cached'] else "🔄 PROCESSED"
        opt_status = "✨ OPTIMIZED" if result['optimized'] else ""
        
        print(f"   {status} {opt_status} - {result['duration']:.3f}s")
    
    # Show performance report
    report = optimizer.get_performance_report()
    print(f"\n📊 PERFORMANCE REPORT:")
    print(f"   Total Queries: {report['total_queries']}")
    print(f"   Cache Hit Rate: {report['cache_hit_rate']:.1f}%")
    print(f"   Avg Response Time: {report['avg_response_time']:.2f}s")
    print(f"   Performance Grade: {report['performance_grade']}")
    
    print(f"\n🎯 Cache Statistics:")
    for key, value in report['cache_stats'].items():
        if key != 'top_queries':
            print(f"   {key.replace('_', ' ').title()}: {value}")

if __name__ == "__main__":
    demo_enhanced_performance()
