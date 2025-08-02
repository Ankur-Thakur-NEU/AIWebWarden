#!/usr/bin/env python3
"""
Advanced Analytics and Business Intelligence Dashboard
Real-time monitoring, insights, and predictive analytics for the AI agent system
"""

import json
import time
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import statistics
from collections import defaultdict, Counter

@dataclass
class QueryMetrics:
    """Comprehensive query metrics."""
    query_id: str
    query: str
    response_time: float
    success: bool
    tool_used: str
    response_length: int
    user_satisfaction: Optional[float]
    timestamp: datetime
    error_type: Optional[str]
    cache_hit: bool
    optimization_applied: bool

class AdvancedAnalytics:
    """Advanced analytics engine for AI agent performance."""
    
    def __init__(self, db_path: str = "analytics.db"):
        """Initialize analytics engine."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
        
    def _init_database(self):
        """Initialize analytics database."""
        with sqlite3.connect(self.db_path) as conn:
            # Query metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS query_metrics (
                    query_id TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    response_time REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    tool_used TEXT,
                    response_length INTEGER,
                    user_satisfaction REAL,
                    timestamp TEXT NOT NULL,
                    error_type TEXT,
                    cache_hit BOOLEAN DEFAULT FALSE,
                    optimization_applied BOOLEAN DEFAULT FALSE
                )
            """
            )
            
            # User behavior table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_behavior (
                    session_id TEXT,
                    query_sequence INTEGER,
                    query_category TEXT,
                    time_spent REAL,
                    follow_up_queries INTEGER,
                    timestamp TEXT NOT NULL
                )
            """
            )
            
            # System performance table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_performance (
                    timestamp TEXT PRIMARY KEY,
                    cpu_usage REAL,
                    memory_usage REAL,
                    active_sessions INTEGER,
                    queue_length INTEGER,
                    error_rate REAL
                )
            """
            )
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON query_metrics(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tool_used ON query_metrics(tool_used)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_success ON query_metrics(success)")
    
    def log_query_metrics(self, metrics: QueryMetrics):
        """Log query metrics to database with enhanced error handling."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO query_metrics 
                    (query_id, query, response_time, success, tool_used, response_length,
                     user_satisfaction, timestamp, error_type, cache_hit, optimization_applied)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metrics.query_id, metrics.query, metrics.response_time, metrics.success,
                    metrics.tool_used, metrics.response_length, metrics.user_satisfaction,
                    metrics.timestamp.isoformat(), metrics.error_type, metrics.cache_hit,
                    metrics.optimization_applied
                ))
        except sqlite3.Error as e:
            print(f"🚨 Database error logging metrics: {str(e)}")
        except Exception as e:
            print(f"❌ Unexpected error logging metrics: {str(e)}")
    
    def get_performance_insights(self, days: int = 7) -> Dict[str, Any]:
        """Generate comprehensive performance insights."""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Basic metrics
            basic_stats = conn.execute("""
                SELECT 
                    COUNT(*) as total_queries,
                    AVG(response_time) as avg_response_time,
                    AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate,
                    AVG(response_length) as avg_response_length,
                    AVG(CASE WHEN cache_hit THEN 1.0 ELSE 0.0 END) as cache_hit_rate
                FROM query_metrics 
                WHERE timestamp > ?
            """, (cutoff_date,)).fetchone()
            
            # Tool usage distribution
            tool_usage = conn.execute("""
                SELECT tool_used, COUNT(*) as usage_count, AVG(response_time) as avg_time
                FROM query_metrics 
                WHERE timestamp > ? AND tool_used IS NOT NULL
                GROUP BY tool_used
                ORDER BY usage_count DESC
            """, (cutoff_date,)).fetchall()
            
            # Error analysis
            error_analysis = conn.execute("""
                SELECT error_type, COUNT(*) as error_count
                FROM query_metrics 
                WHERE timestamp > ? AND error_type IS NOT NULL
                GROUP BY error_type
                ORDER BY error_count DESC
            """, (cutoff_date,)).fetchall()
            
            # Performance trends (hourly)
            hourly_trends = conn.execute("""
                SELECT 
                    strftime('%H', timestamp) as hour,
                    COUNT(*) as query_count,
                    AVG(response_time) as avg_response_time,
                    AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate
                FROM query_metrics 
                WHERE timestamp > ?
                GROUP BY strftime('%H', timestamp)
                ORDER BY hour
            """, (cutoff_date,)).fetchall()
            
            return {
                'basic_stats': {
                    'total_queries': basic_stats[0] or 0,
                    'avg_response_time': round(basic_stats[1] or 0, 2),
                    'success_rate': round((basic_stats[2] or 0) * 100, 1),
                    'avg_response_length': int(basic_stats[3] or 0),
                    'cache_hit_rate': round((basic_stats[4] or 0) * 100, 1)
                },
                'tool_usage': [
                    {'tool': row[0], 'count': row[1], 'avg_time': round(row[2], 2)}
                    for row in tool_usage
                ],
                'error_analysis': [
                    {'error_type': row[0], 'count': row[1]}
                    for row in error_analysis
                ],
                'hourly_trends': [
                    {
                        'hour': int(row[0]),
                        'query_count': row[1],
                        'avg_response_time': round(row[2], 2),
                        'success_rate': round(row[3] * 100, 1)
                    }
                    for row in hourly_trends
                ]
            }
    
    def get_user_behavior_insights(self, days: int = 7) -> Dict[str, Any]:
        """Analyze user behavior patterns."""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Query categories
            query_categories = conn.execute("""
                SELECT 
                    CASE 
                        WHEN query LIKE '%how to%' OR query LIKE '%tutorial%' THEN 'Tutorial'
                        WHEN query LIKE '%what is%' OR query LIKE '%define%' THEN 'Definition'
                        WHEN query LIKE '%compare%' OR query LIKE '%vs%' THEN 'Comparison'
                        WHEN query LIKE '%best%' OR query LIKE '%recommend%' THEN 'Recommendation'
                        WHEN query LIKE '%price%' OR query LIKE '%cost%' THEN 'Pricing'
                        ELSE 'General'
                    END as category,
                    COUNT(*) as count,
                    AVG(response_time) as avg_time
                FROM query_metrics 
                WHERE timestamp > ?
                GROUP BY category
                ORDER BY count DESC
            """, (cutoff_date,)).fetchall()
            
            # Query complexity analysis
            complexity_analysis = conn.execute("""
                SELECT 
                    CASE 
                        WHEN LENGTH(query) < 50 THEN 'Simple'
                        WHEN LENGTH(query) < 100 THEN 'Medium'
                        ELSE 'Complex'
                    END as complexity,
                    COUNT(*) as count,
                    AVG(response_time) as avg_time,
                    AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate
                FROM query_metrics 
                WHERE timestamp > ?
                GROUP BY complexity
            """, (cutoff_date,)).fetchall()
            
            return {
                'query_categories': [
                    {'category': row[0], 'count': row[1], 'avg_time': round(row[2], 2)}
                    for row in query_categories
                ],
                'complexity_analysis': [
                    {
                        'complexity': row[0],
                        'count': row[1],
                        'avg_time': round(row[2], 2),
                        'success_rate': round(row[3] * 100, 1)
                    }
                    for row in complexity_analysis
                ]
            }
    
    def predict_performance_trends(self) -> Dict[str, Any]:
        """Predict performance trends using simple statistical analysis."""
        with sqlite3.connect(self.db_path) as conn:
            # Get recent performance data
            recent_data = conn.execute("""
                SELECT 
                    DATE(timestamp) as date,
                    AVG(response_time) as avg_response_time,
                    AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate,
                    COUNT(*) as query_count
                FROM query_metrics 
                WHERE timestamp > date('now', '-30 days')
                GROUP BY DATE(timestamp)
                ORDER BY date
            """).fetchall()
            
            if len(recent_data) < 7:
                return {'prediction': 'Insufficient data for trend analysis'}
            
            # Simple trend analysis
            response_times = [row[1] for row in recent_data[-14:]]  # Last 14 days
            success_rates = [row[2] for row in recent_data[-14:]]
            query_counts = [row[3] for row in recent_data[-14:]]
            
            # Calculate trends (simple linear regression slope approximation)
            def calculate_trend(values):
                if len(values) < 2:
                    return 0
                n = len(values)
                x_mean = (n - 1) / 2
                y_mean = sum(values) / n
                numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
                denominator = sum((i - x_mean) ** 2 for i in range(n))
                return numerator / denominator if denominator != 0 else 0
            
            response_time_trend = calculate_trend(response_times)
            success_rate_trend = calculate_trend(success_rates)
            query_count_trend = calculate_trend(query_counts)
            
            # Generate predictions
            predictions = {
                'response_time': {
                    'current_avg': round(statistics.mean(response_times[-7:]), 2),
                    'trend': 'improving' if response_time_trend < -0.01 else 'degrading' if response_time_trend > 0.01 else 'stable',
                    'predicted_change': round(response_time_trend * 7, 2)  # 7-day projection
                },
                'success_rate': {
                    'current_avg': round(statistics.mean(success_rates[-7:]) * 100, 1),
                    'trend': 'improving' if success_rate_trend > 0.001 else 'degrading' if success_rate_trend < -0.001 else 'stable',
                    'predicted_change': round(success_rate_trend * 7 * 100, 1)
                },
                'query_volume': {
                    'current_avg': round(statistics.mean(query_counts[-7:])),
                    'trend': 'increasing' if query_count_trend > 0.1 else 'decreasing' if query_count_trend < -0.1 else 'stable',
                    'predicted_change': round(query_count_trend * 7)
                }
            }
            
            return predictions
    
    def generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on analytics."""
        insights = self.get_performance_insights()
        behavior = self.get_user_behavior_insights()
        trends = self.predict_performance_trends()
        
        recommendations = []
        
        # Performance recommendations
        if insights['basic_stats']['avg_response_time'] > 5:
            recommendations.append("🚀 Consider enabling more aggressive caching to reduce response times")
        
        if insights['basic_stats']['success_rate'] < 90:
            recommendations.append("🔧 Review error handling and tool reliability")
        
        if insights['basic_stats']['cache_hit_rate'] < 20:
            recommendations.append("💾 Optimize caching strategy for better performance")
        
        # Tool usage recommendations
        if insights['tool_usage']:
            slowest_tool = max(insights['tool_usage'], key=lambda x: x['avg_time'])
            if slowest_tool['avg_time'] > 8:
                recommendations.append(f"⚡ Optimize {slowest_tool['tool']} tool performance")
        
        # User behavior recommendations
        if behavior['query_categories']:
            top_category = behavior['query_categories'][0]
            recommendations.append(f"📊 Consider specialized optimizations for {top_category['category']} queries")
        
        # Trend-based recommendations
        if isinstance(trends, dict) and 'response_time' in trends:
            if trends['response_time']['trend'] == 'degrading':
                recommendations.append("📈 Response times are trending upward - investigate performance bottlenecks")
            
            if trends['query_volume']['trend'] == 'increasing':
                recommendations.append("📊 Query volume is increasing - consider scaling infrastructure")
        
        return recommendations[:5]  # Top 5 recommendations

class BusinessIntelligenceDashboard:
    """Business intelligence dashboard for stakeholders."""
    
    def __init__(self, analytics: AdvancedAnalytics):
        """Initialize BI dashboard."""
        self.analytics = analytics
    
    def generate_executive_summary(self) -> Dict[str, Any]:
        """Generate executive summary for stakeholders."""
        insights = self.analytics.get_performance_insights()
        behavior = self.analytics.get_user_behavior_insights()
        trends = self.analytics.predict_performance_trends()
        recommendations = self.analytics.generate_recommendations()
        
        # Calculate key metrics
        total_queries = insights['basic_stats']['total_queries']
        avg_response_time = insights['basic_stats']['avg_response_time']
        success_rate = insights['basic_stats']['success_rate']
        
        # Performance grade
        performance_score = 0
        if success_rate >= 95:
            performance_score += 40
        elif success_rate >= 90:
            performance_score += 30
        elif success_rate >= 85:
            performance_score += 20
        
        if avg_response_time <= 2:
            performance_score += 40
        elif avg_response_time <= 5:
            performance_score += 30
        elif avg_response_time <= 10:
            performance_score += 20
        
        if total_queries > 100:
            performance_score += 20
        elif total_queries > 50:
            performance_score += 15
        elif total_queries > 10:
            performance_score += 10
        
        grade = 'A+' if performance_score >= 90 else 'A' if performance_score >= 80 else 'B' if performance_score >= 70 else 'C' if performance_score >= 60 else 'D'
        
        return {
            'summary': {
                'total_queries': total_queries,
                'success_rate': success_rate,
                'avg_response_time': avg_response_time,
                'performance_grade': grade,
                'performance_score': performance_score
            },
            'key_insights': {
                'most_used_tool': insights['tool_usage'][0]['tool'] if insights['tool_usage'] else 'N/A',
                'top_query_category': behavior['query_categories'][0]['category'] if behavior['query_categories'] else 'N/A',
                'cache_efficiency': insights['basic_stats']['cache_hit_rate']
            },
            'trends': trends,
            'recommendations': recommendations,
            'generated_at': datetime.now().isoformat()
        }
    
    def export_report(self, format: str = 'json') -> str:
        """Export comprehensive report."""
        summary = self.generate_executive_summary()
        
        if format == 'json':
            return json.dumps(summary, indent=2)
        elif format == 'text':
            return self._format_text_report(summary)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _format_text_report(self, summary: Dict[str, Any]) -> str:
        """Format report as readable text."""
        report = f"""
🏢 AI AGENT BUSINESS INTELLIGENCE REPORT
{'='*50}
Generated: {summary['generated_at']}

📊 EXECUTIVE SUMMARY
Performance Grade: {summary['summary']['performance_grade']} ({summary['summary']['performance_score']}/100)
Total Queries: {summary['summary']['total_queries']:,}
Success Rate: {summary['summary']['success_rate']}%
Avg Response Time: {summary['summary']['avg_response_time']}s

🔍 KEY INSIGHTS
Most Used Tool: {summary['key_insights']['most_used_tool']}
Top Query Category: {summary['key_insights']['top_query_category']}
Cache Efficiency: {summary['key_insights']['cache_efficiency']}%

📈 PERFORMANCE TRENDS
"""
        
        if isinstance(summary['trends'], dict):
            for metric, data in summary['trends'].items():
                if isinstance(data, dict):
                    report += f"{metric.replace('_', ' ').title()}: {data['trend']} ({data.get('predicted_change', 'N/A')} projected change)\n"
        
        report += f"\n💡 RECOMMENDATIONS\n"
        for i, rec in enumerate(summary['recommendations'], 1):
            report += f"{i}. {rec}\n"
        
        return report

# Demo function
def demo_analytics_dashboard():
    """Demonstrate analytics dashboard capabilities."""
    print("📊 ADVANCED ANALYTICS DASHBOARD DEMO")
    print("="*50)
    
    # Initialize analytics
    analytics = AdvancedAnalytics("demo_analytics.db")
    dashboard = BusinessIntelligenceDashboard(analytics)
    
    # Simulate some data
    print("📝 Simulating query data...")
    
    import uuid
    sample_queries = [
        ("What is Python?", "web_search", 1.2, True),
        ("How to learn machine learning?", "search_and_scrape", 2.5, True),
        ("Compare iPhone vs Android", "search_and_scrape", 3.1, True),
        ("Best laptops under $1000", "web_search", 1.8, True),
        ("Invalid query test", "web_search", 0.5, False),
    ]
    
    for query, tool, time_taken, success in sample_queries:
        metrics = QueryMetrics(
            query_id=str(uuid.uuid4()),
            query=query,
            response_time=time_taken,
            success=success,
            tool_used=tool,
            response_length=500 if success else 50,
            user_satisfaction=4.5 if success else 2.0,
            timestamp=datetime.now(),
            error_type=None if success else "tool_error",
            cache_hit=False,
            optimization_applied=True
        )
        analytics.log_query_metrics(metrics)
    
    # Generate insights
    print("\n📈 Generating performance insights...")
    insights = analytics.get_performance_insights()
    
    print(f"✅ Basic Stats:")
    for key, value in insights['basic_stats'].items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    # Generate executive summary
    print("\n🏢 Generating executive summary...")
    summary = dashboard.generate_executive_summary()
    
    print(f"📊 Performance Grade: {summary['summary']['performance_grade']}")
    print(f"🎯 Success Rate: {summary['summary']['success_rate']}%")
    print(f"⚡ Avg Response Time: {summary['summary']['avg_response_time']}s")
    
    print(f"\n💡 Top Recommendations:")
    for i, rec in enumerate(summary['recommendations'][:3], 1):
        print(f"   {i}. {rec}")
    
    # Export report
    print(f"\n📄 Exporting report...")
    text_report = dashboard.export_report('text')
    print("Report generated successfully!")
    
    return summary

if __name__ == "__main__":
    demo_analytics_dashboard()
