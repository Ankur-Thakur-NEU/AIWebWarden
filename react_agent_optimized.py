#!/usr/bin/env python3
"""
Optimized ReAct Agent Implementation
Enhanced with performance optimizations, better error handling, and output management
"""

import json
import re
import time
from typing import Dict, Any, Optional
from cerebras_client import get_completion
from tools import web_search, scrape_url, search_and_scrape

class OptimizedReActAgent:
    """Performance-optimized ReAct agent with enhanced error handling."""
    
    def __init__(self, model_name: str = "llama3.1-8b", verbose: bool = True, max_iterations: int = 3):
        """Initialize the optimized ReAct agent."""
        self.model_name = model_name
        self.verbose = verbose
        self.max_iterations = max_iterations
        self.max_response_length = 2000  # Limit response length
        self.query_cache = {}  # Simple caching for repeated queries
        
        # Performance tracking
        self.performance_stats = {
            'total_queries': 0,
            'avg_response_time': 0,
            'cache_hits': 0,
            'tool_calls': 0
        }
        
        # Available tools with optimization settings
        self.tools = {
            "web_search": {
                "function": web_search,
                "description": "Quick web search for basic information",
                "max_results": 3,  # Reduced for speed
                "timeout": 10
            },
            "scrape_url": {
                "function": scrape_url,
                "description": "Extract content from specific URL",
                "max_chars": 1500,  # Reduced for speed
                "timeout": 8
            },
            "search_and_scrape": {
                "function": search_and_scrape,
                "description": "Comprehensive search with content extraction",
                "max_results": 2,  # Reduced for speed
                "scrape_top_n": 1,  # Reduced for speed
                "timeout": 15
            }
        }
        
        if self.verbose:
            print(f"🚀 Optimized ReAct Agent initialized!")
            print(f"🧠 Model: {model_name}")
            print(f"⚡ Max iterations: {max_iterations}")
            print(f"🔧 Tools: {len(self.tools)} available (performance optimized)")
    
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key for query."""
        return query.lower().strip()
    
    def _check_cache(self, query: str) -> Optional[str]:
        """Check if query result is cached."""
        cache_key = self._get_cache_key(query)
        if cache_key in self.query_cache:
            self.performance_stats['cache_hits'] += 1
            if self.verbose:
                print("🔄 Using cached result")
            return self.query_cache[cache_key]
        return None
    
    def _cache_result(self, query: str, result: str) -> None:
        """Cache query result."""
        cache_key = self._get_cache_key(query)
        # Keep cache size reasonable
        if len(self.query_cache) > 50:
            # Remove oldest entry
            oldest_key = next(iter(self.query_cache))
            del self.query_cache[oldest_key]
        self.query_cache[cache_key] = result
    
    def _plan_actions_optimized(self, query: str) -> Dict[str, Any]:
        """Optimized planning with faster prompts and response limits."""
        planning_prompt = f"""Analyze this query and choose the best tool. Be concise.

Available tools:
- web_search: Quick search (use for simple questions)
- scrape_url: Get content from specific URL (use if URL provided)
- search_and_scrape: Comprehensive research (use for complex topics)

Query: "{query}"

Respond with JSON only:
{{"tool": "tool_name", "input": "search_terms_or_url", "reasoning": "brief_explanation"}}"""
        
        try:
            response = get_completion(planning_prompt, model=self.model_name, max_tokens=150)
            
            # Extract JSON with improved parsing
            json_match = re.search(r'\{[^}]*"tool"[^}]*\}', response, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
                
                # Validate plan
                if plan.get('tool') in self.tools:
                    return plan
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️ Planning error: {e}")
        
        # Fast fallback plan
        if "http" in query:
            return {"tool": "scrape_url", "input": query, "reasoning": "URL detected"}
        elif len(query.split()) > 8:
            return {"tool": "search_and_scrape", "input": query, "reasoning": "Complex query"}
        else:
            return {"tool": "web_search", "input": query, "reasoning": "Simple query"}
    
    def _execute_tool_optimized(self, tool_name: str, action_input: str) -> str:
        """Execute tool with optimization settings and timeout."""
        if tool_name not in self.tools:
            return f"Error: Unknown tool '{tool_name}'"
        
        try:
            self.performance_stats['tool_calls'] += 1
            
            if self.verbose:
                print(f"🔧 Executing: {tool_name}")
            
            tool_config = self.tools[tool_name]
            tool_function = tool_config["function"]
            
            start_time = time.time()
            
            # Execute with optimized parameters
            if tool_name == "scrape_url":
                result = tool_function(action_input, max_chars=tool_config["max_chars"])
            elif tool_name == "search_and_scrape":
                result = tool_function(
                    action_input, 
                    max_results=tool_config["max_results"],
                    scrape_top_n=tool_config["scrape_top_n"]
                )
            else:  # web_search
                result = tool_function(action_input, max_results=tool_config["max_results"])
            
            duration = time.time() - start_time
            
            if self.verbose:
                print(f"✅ Tool completed in {duration:.1f}s - {len(result)} chars")
            
            # Trim result if too long
            if len(result) > 3000:
                result = result[:3000] + "\n... [Content trimmed for performance]"
            
            return result
            
        except Exception as e:
            error_msg = f"Tool execution error: {str(e)}"
            if self.verbose:
                print(f"❌ {error_msg}")
            return error_msg
    
    def _synthesize_response_optimized(self, query: str, tool_results: str, reasoning: str) -> str:
        """Optimized response synthesis with length limits."""
        synthesis_prompt = f"""Provide a concise, helpful answer based on the information gathered.

Query: "{query}"
Information: {tool_results[:2000]}  # Limit input length

Requirements:
- Be concise but comprehensive
- Include key facts and sources when available
- Maximum 300 words
- Structure clearly with bullet points if needed

Answer:"""
        
        try:
            response = get_completion(synthesis_prompt, model=self.model_name, max_tokens=400)
            
            # Ensure response isn't too long
            if len(response) > self.max_response_length:
                response = response[:self.max_response_length] + "\n... [Response trimmed]"
            
            return response
            
        except Exception as e:
            return f"Error generating response: {str(e)}\n\nRaw information:\n{tool_results[:500]}..."
    
    def query(self, user_query: str) -> str:
        """Process query with optimizations and performance tracking."""
        start_time = time.time()
        self.performance_stats['total_queries'] += 1
        
        # Check cache first
        cached_result = self._check_cache(user_query)
        if cached_result:
            return cached_result
        
        if self.verbose:
            print(f"\n🔍 Processing optimized query: '{user_query}'")
            print("⚡ Using performance optimizations...")
        
        try:
            # Step 1: Fast planning
            plan = self._plan_actions_optimized(user_query)
            
            if self.verbose:
                print(f"🎯 Plan: {plan.get('reasoning', 'No reasoning')}")
                print(f"🔧 Tool: {plan['tool']} | Input: {plan['input'][:50]}...")
            
            # Step 2: Execute tool
            tool_results = self._execute_tool_optimized(plan['tool'], plan['input'])
            
            # Step 3: Quick synthesis
            if self.verbose:
                print("🧠 Synthesizing response...")
            
            response = self._synthesize_response_optimized(
                user_query, tool_results, plan.get('reasoning', '')
            )
            
            # Update performance stats
            duration = time.time() - start_time
            self.performance_stats['avg_response_time'] = (
                (self.performance_stats['avg_response_time'] * (self.performance_stats['total_queries'] - 1) + duration) 
                / self.performance_stats['total_queries']
            )
            
            # Cache result
            self._cache_result(user_query, response)
            
            if self.verbose:
                print(f"✅ Completed in {duration:.2f}s (avg: {self.performance_stats['avg_response_time']:.2f}s)")
            
            return response
            
        except Exception as e:
            error_response = f"Error processing query: {str(e)}"
            if self.verbose:
                print(f"❌ {error_response}")
            return error_response
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return self.performance_stats.copy()
    
    def clear_cache(self) -> None:
        """Clear query cache."""
        self.query_cache.clear()
        if self.verbose:
            print("🗑️ Cache cleared")
    
    def optimize_for_demo(self) -> None:
        """Apply demo-specific optimizations."""
        self.max_iterations = 2  # Faster for demos
        self.max_response_length = 1500  # Shorter responses
        
        # Reduce tool limits for speed
        for tool_config in self.tools.values():
            if 'max_results' in tool_config:
                tool_config['max_results'] = min(tool_config.get('max_results', 3), 2)
            if 'max_chars' in tool_config:
                tool_config['max_chars'] = min(tool_config.get('max_chars', 1500), 1000)
        
        if self.verbose:
            print("🎬 Demo optimizations applied!")

# Performance testing and debugging utilities
def run_performance_test():
    """Run performance optimization tests."""
    print("⚡ PERFORMANCE OPTIMIZATION TEST")
    print("="*50)
    
    agent = OptimizedReActAgent(verbose=True)
    
    test_queries = [
        "What is Python programming?",
        "Latest AI developments",
        "Compare iPhone vs Android"
    ]
    
    print("🔥 Running performance tests...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📊 Test {i}/3: '{query}'")
        
        start_time = time.time()
        response = agent.query(query)
        duration = time.time() - start_time
        
        print(f"⏱️ Time: {duration:.2f}s | Length: {len(response)} chars")
        
        # Test cache hit
        print("🔄 Testing cache...")
        cache_start = time.time()
        cached_response = agent.query(query)
        cache_duration = time.time() - cache_start
        
        print(f"⚡ Cache hit: {cache_duration:.2f}s (speedup: {duration/cache_duration:.1f}x)")
    
    # Show final stats
    stats = agent.get_performance_stats()
    print(f"\n📈 Final Performance Stats:")
    for key, value in stats.items():
        print(f"   {key}: {value}")

def debug_agent_issues():
    """Debug common agent issues."""
    print("🐛 AGENT DEBUGGING UTILITIES")
    print("="*50)
    
    agent = OptimizedReActAgent(verbose=True)
    
    # Test error handling
    error_queries = [
        "https://invalid-url-test.com",  # Bad URL
        "",  # Empty query
        "x" * 1000,  # Very long query
    ]
    
    for query in error_queries:
        print(f"\n🧪 Testing error handling: '{query[:50]}...'")
        try:
            response = agent.query(query)
            print(f"✅ Handled gracefully: {len(response)} chars")
        except Exception as e:
            print(f"❌ Error not handled: {e}")

if __name__ == "__main__":
    print("🚀 OPTIMIZED REACT AGENT - TESTING & DEBUGGING")
    print("="*60)
    
    choice = input("Choose test type:\n1. Performance Test\n2. Debug Issues\n3. Both\nChoice: ").strip()
    
    if choice in ['1', '3']:
        run_performance_test()
    
    if choice in ['2', '3']:
        debug_agent_issues()
    
    print("\n✅ Testing complete!")