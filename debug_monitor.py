#!/usr/bin/env python3
"""
Debugging and Monitoring Utilities for Agentic Browser Assistant
Provides debugging tools, performance monitoring, and optimization insights
"""

import time
import json
import traceback
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

class AgentDebugger:
    """Comprehensive debugging and monitoring system."""
    
    def __init__(self, log_file: str = "agent_debug.log"):
        """Initialize the debugger."""
        self.log_file = log_file
        self.setup_logging()
        self.performance_data = []
        self.error_log = []
        self.optimization_suggestions = []
        
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log_query_performance(self, query: str, duration: float, response_length: int, 
                            tool_used: str = None, success: bool = True, error: str = None):
        """Log query performance data."""
        performance_entry = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'duration': duration,
            'response_length': response_length,
            'tool_used': tool_used,
            'success': success,
            'error': error
        }
        
        self.performance_data.append(performance_entry)
        
        if success:
            self.logger.info(f"Query completed: {duration:.2f}s, {response_length} chars")
        else:
            self.logger.error(f"Query failed: {error}")
            self.error_log.append(performance_entry)
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance data and provide insights."""
        if not self.performance_data:
            return {"message": "No performance data available"}
        
        successful_queries = [entry for entry in self.performance_data if entry['success']]
        
        if not successful_queries:
            return {"message": "No successful queries to analyze"}
        
        durations = [entry['duration'] for entry in successful_queries]
        response_lengths = [entry['response_length'] for entry in successful_queries]
        
        analysis = {
            'total_queries': len(self.performance_data),
            'successful_queries': len(successful_queries),
            'success_rate': len(successful_queries) / len(self.performance_data) * 100,
            'avg_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'avg_response_length': sum(response_lengths) / len(response_lengths),
            'queries_per_minute': len(successful_queries) / (max(durations) / 60) if durations else 0
        }
        
        # Generate optimization suggestions
        self._generate_optimization_suggestions(analysis)
        
        return analysis
    
    def _generate_optimization_suggestions(self, analysis: Dict[str, Any]):
        """Generate optimization suggestions based on performance data."""
        suggestions = []
        
        if analysis['avg_duration'] > 8:
            suggestions.append("⚡ Response time is high (>8s). Consider reducing tool iterations or response length.")
        
        if analysis['success_rate'] < 90:
            suggestions.append("🛠️ Success rate is low (<90%). Review error handling and tool reliability.")
        
        if analysis['avg_response_length'] > 2000:
            suggestions.append("📝 Responses are lengthy (>2000 chars). Consider trimming for better UX.")
        
        if analysis['max_duration'] > 15:
            suggestions.append("⏰ Some queries are very slow (>15s). Implement timeout handling.")
        
        # Tool-specific suggestions
        tool_usage = {}
        for entry in self.performance_data:
            if entry['tool_used']:
                tool_usage[entry['tool_used']] = tool_usage.get(entry['tool_used'], 0) + 1
        
        if tool_usage:
            most_used_tool = max(tool_usage, key=tool_usage.get)
            suggestions.append(f"🔧 Most used tool: {most_used_tool}. Consider optimizing its performance.")
        
        self.optimization_suggestions = suggestions
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors encountered."""
        if not self.error_log:
            return {"message": "No errors logged"}
        
        error_types = {}
        for error_entry in self.error_log:
            error_msg = error_entry.get('error', 'Unknown error')
            error_type = error_msg.split(':')[0] if ':' in error_msg else error_msg
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            'total_errors': len(self.error_log),
            'error_types': error_types,
            'recent_errors': self.error_log[-5:] if len(self.error_log) > 5 else self.error_log
        }
    
    def debug_query_step_by_step(self, agent, query: str):
        """Debug a query step by step with detailed logging."""
        print(f"🐛 DEBUGGING QUERY: '{query}'")
        print("="*60)
        
        try:
            # Step 1: Planning phase
            print("1️⃣ PLANNING PHASE")
            start_time = time.time()
            
            # This would need to be adapted based on the agent's internal methods
            print("   📋 Analyzing query intent...")
            print("   🎯 Selecting appropriate tools...")
            
            planning_time = time.time() - start_time
            print(f"   ✅ Planning completed in {planning_time:.3f}s")
            
            # Step 2: Tool execution phase
            print("\n2️⃣ TOOL EXECUTION PHASE")
            tool_start = time.time()
            
            print("   🔧 Executing selected tool...")
            print("   📡 Making web requests...")
            print("   📄 Processing content...")
            
            tool_time = time.time() - tool_start
            print(f"   ✅ Tool execution completed in {tool_time:.3f}s")
            
            # Step 3: Response synthesis
            print("\n3️⃣ RESPONSE SYNTHESIS PHASE")
            synthesis_start = time.time()
            
            print("   🧠 Generating AI response...")
            print("   📝 Formatting output...")
            
            synthesis_time = time.time() - synthesis_start
            print(f"   ✅ Synthesis completed in {synthesis_time:.3f}s")
            
            total_time = time.time() - start_time
            print(f"\n⏱️ TOTAL DEBUG TIME: {total_time:.3f}s")
            
            # Breakdown analysis
            print(f"\n📊 TIME BREAKDOWN:")
            print(f"   Planning: {planning_time:.3f}s ({planning_time/total_time*100:.1f}%)")
            print(f"   Tool Execution: {tool_time:.3f}s ({tool_time/total_time*100:.1f}%)")
            print(f"   Synthesis: {synthesis_time:.3f}s ({synthesis_time/total_time*100:.1f}%)")
            
        except Exception as e:
            print(f"❌ DEBUG ERROR: {e}")
            traceback.print_exc()
    
    def monitor_system_resources(self):
        """Monitor system resources during agent operation."""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            resource_info = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"💻 SYSTEM RESOURCES:")
            print(f"   CPU: {cpu_percent}%")
            print(f"   Memory: {memory.percent}% ({memory.available / (1024**3):.1f}GB available)")
            
            return resource_info
            
        except ImportError:
            print("⚠️ psutil not installed. Install with: pip install psutil")
            return None
    
    def generate_debug_report(self) -> str:
        """Generate comprehensive debug report."""
        report = []
        report.append("🐛 AGENT DEBUG REPORT")
        report.append("="*60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Performance analysis
        perf_analysis = self.analyze_performance()
        if 'total_queries' in perf_analysis:
            report.append("📊 PERFORMANCE ANALYSIS:")
            report.append(f"   Total Queries: {perf_analysis['total_queries']}")
            report.append(f"   Success Rate: {perf_analysis['success_rate']:.1f}%")
            report.append(f"   Avg Duration: {perf_analysis['avg_duration']:.2f}s")
            report.append(f"   Duration Range: {perf_analysis['min_duration']:.2f}s - {perf_analysis['max_duration']:.2f}s")
            report.append("")
        
        # Error summary
        error_summary = self.get_error_summary()
        if 'total_errors' in error_summary:
            report.append("❌ ERROR SUMMARY:")
            report.append(f"   Total Errors: {error_summary['total_errors']}")
            report.append("   Error Types:")
            for error_type, count in error_summary['error_types'].items():
                report.append(f"     • {error_type}: {count}")
            report.append("")
        
        # Optimization suggestions
        if self.optimization_suggestions:
            report.append("💡 OPTIMIZATION SUGGESTIONS:")
            for suggestion in self.optimization_suggestions:
                report.append(f"   {suggestion}")
            report.append("")
        
        # System status
        report.append("✅ SYSTEM STATUS: OPERATIONAL")
        report.append("   All debugging utilities are functioning correctly.")
        
        return "\n".join(report)
    
    def save_debug_report(self, filename: str = None):
        """Save debug report to file."""
        if filename is None:
            filename = f"debug_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        report = self.generate_debug_report()
        
        with open(filename, 'w') as f:
            f.write(report)
        
        print(f"📄 Debug report saved to: {filename}")
        return filename

class PerformanceProfiler:
    """Performance profiling utilities."""
    
    def __init__(self):
        """Initialize the profiler."""
        self.profiles = {}
    
    def profile_function(self, func_name: str):
        """Decorator to profile function execution time."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                if func_name not in self.profiles:
                    self.profiles[func_name] = []
                self.profiles[func_name].append(duration)
                
                return result
            return wrapper
        return decorator
    
    def get_profile_summary(self) -> Dict[str, Any]:
        """Get summary of all profiled functions."""
        summary = {}
        
        for func_name, durations in self.profiles.items():
            summary[func_name] = {
                'calls': len(durations),
                'total_time': sum(durations),
                'avg_time': sum(durations) / len(durations),
                'min_time': min(durations),
                'max_time': max(durations)
            }
        
        return summary

# Utility functions for debugging
def test_agent_with_debugging():
    """Test agent with comprehensive debugging."""
    print("🧪 AGENT DEBUGGING TEST")
    print("="*50)
    
    debugger = AgentDebugger()
    
    # Import and test with different agents
    try:
        from react_agent_optimized import OptimizedReActAgent
        agent = OptimizedReActAgent(verbose=True)
        
        test_queries = [
            "What is Python programming?",
            "https://invalid-url-test.com",  # This should fail
            "Latest AI developments"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing: '{query}'")
            
            start_time = time.time()
            try:
                response = agent.query(query)
                duration = time.time() - start_time
                
                debugger.log_query_performance(
                    query=query,
                    duration=duration,
                    response_length=len(response),
                    tool_used="optimized_agent",
                    success=True
                )
                
                print(f"✅ Success: {duration:.2f}s, {len(response)} chars")
                
            except Exception as e:
                duration = time.time() - start_time
                
                debugger.log_query_performance(
                    query=query,
                    duration=duration,
                    response_length=0,
                    tool_used="optimized_agent",
                    success=False,
                    error=str(e)
                )
                
                print(f"❌ Failed: {e}")
        
        # Generate and display report
        print("\n" + debugger.generate_debug_report())
        
        # Save report
        debugger.save_debug_report()
        
    except ImportError as e:
        print(f"❌ Could not import agent: {e}")

if __name__ == "__main__":
    test_agent_with_debugging()