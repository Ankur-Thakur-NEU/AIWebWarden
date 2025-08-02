#!/usr/bin/env python3
"""
Simplified ReAct Agent Implementation
A more robust implementation that works well with Cerebras LLM
"""

import json
import re
from cerebras_client import get_completion
from tools import web_search, scrape_url, search_and_scrape

class SimpleReActAgent:
    """A simplified but robust ReAct agent for web browsing."""
    
    def __init__(self, model_name: str = "llama3.1-8b", verbose: bool = True):
        """Initialize the Simple ReAct agent."""
        self.model_name = model_name
        self.verbose = verbose
        
        # Available tools
        self.tools = {
            "web_search": {
                "function": web_search,
                "description": "Search the web for information about any topic",
                "example": "web_search('artificial intelligence')"
            },
            "scrape_url": {
                "function": scrape_url,
                "description": "Extract text content from a specific URL",
                "example": "scrape_url('https://example.com')"
            },
            "search_and_scrape": {
                "function": search_and_scrape,
                "description": "Search the web and scrape content from top results for comprehensive information",
                "example": "search_and_scrape('best laptops 2024')"
            }
        }
        
        print(f"🤖 Simple ReAct Agent initialized!")
        print(f"🧠 Model: {model_name}")
        print(f"🔧 Tools: {len(self.tools)} available")
        print(f"📝 Verbose mode: {verbose}")
    
    def _get_tools_description(self) -> str:
        """Get a formatted description of available tools."""
        descriptions = []
        for name, info in self.tools.items():
            descriptions.append(f"- {name}: {info['description']}")
        return "\n".join(descriptions)
    
    def _plan_actions(self, query: str) -> str:
        """Plan what actions to take for the given query."""
        tools_desc = self._get_tools_description()
        
        planning_prompt = f"""You are an intelligent web browsing assistant. Analyze the user's query and plan what actions to take.

Available tools:
{tools_desc}

User Query: "{query}"

Think step-by-step and decide:
1. What information do I need to find?
2. Which tool(s) would be most appropriate?
3. What should I search for or scrape?

Respond with a JSON object containing your plan:
{{
    "reasoning": "Your step-by-step thinking",
    "tool": "tool_name_to_use",
    "action_input": "what to search for or URL to scrape",
    "expected_outcome": "what you expect to find"
}}

Choose the most appropriate tool:
- Use "web_search" for quick searches
- Use "scrape_url" if you have a specific URL
- Use "search_and_scrape" for comprehensive research (recommended for most queries)
"""
        
        try:
            response = get_completion(planning_prompt, model=self.model_name, max_tokens=300)
            if self.verbose:
                print(f"🧠 Planning Response: {response}")
            return response
        except Exception as e:
            return f'{{"reasoning": "Error in planning: {str(e)}", "tool": "search_and_scrape", "action_input": "{query}", "expected_outcome": "Basic search results"}}'
    
    def _execute_tool(self, tool_name: str, action_input: str) -> str:
        """Execute the specified tool with the given input."""
        if tool_name not in self.tools:
            return f"Error: Unknown tool '{tool_name}'"
        
        try:
            if self.verbose:
                print(f"🔧 Executing: {tool_name}({action_input})")
            
            tool_function = self.tools[tool_name]["function"]
            
            if tool_name == "scrape_url":
                result = tool_function(action_input)
            else:
                # For search tools, pass max_results parameter
                if tool_name == "search_and_scrape":
                    result = tool_function(action_input, max_results=3, scrape_top_n=2)
                else:
                    result = tool_function(action_input, max_results=5)
            
            if self.verbose:
                print(f"✅ Tool execution completed. Result length: {len(result)} chars")
            
            return result
        except Exception as e:
            error_msg = f"Error executing {tool_name}: {str(e)}"
            if self.verbose:
                print(f"❌ {error_msg}")
            return error_msg
    
    def _synthesize_response(self, query: str, tool_results: str, reasoning: str) -> str:
        """Synthesize a final response based on the tool results."""
        synthesis_prompt = f"""You are an intelligent assistant that provides comprehensive answers based on web research.

Original Query: "{query}"

Your Reasoning: {reasoning}

Information Gathered:
{tool_results}

Based on the information above, provide a comprehensive, well-structured answer to the user's query. 

Guidelines:
- Start with a clear, direct answer
- Include relevant details and examples
- Cite sources with URLs when available
- If information is insufficient, acknowledge this
- Structure your response with clear sections if needed
- Be helpful and actionable

Provide your final answer:"""
        
        try:
            response = get_completion(synthesis_prompt, model=self.model_name, max_tokens=800)
            return response
        except Exception as e:
            return f"Error synthesizing response: {str(e)}\n\nRaw information gathered:\n{tool_results}"
    
    def query(self, user_query: str) -> str:
        """Process a query using the ReAct pattern: Reason → Act → Observe → Synthesize."""
        if self.verbose:
            print(f"\n🔍 Processing ReAct query: '{user_query}'")
            print("🧠 Following ReAct pattern: Reason → Act → Observe → Synthesize")
            print("-" * 60)
        
        try:
            # Step 1: Reason (Plan actions)
            if self.verbose:
                print("1️⃣ REASONING: Planning actions...")
            
            plan_response = self._plan_actions(user_query)
            
            # Parse the plan (with fallback)
            try:
                # Try to extract JSON from the response
                json_match = re.search(r'\{.*\}', plan_response, re.DOTALL)
                if json_match:
                    plan = json.loads(json_match.group())
                else:
                    raise ValueError("No JSON found in plan")
            except (json.JSONDecodeError, ValueError):
                # Fallback plan
                plan = {
                    "reasoning": "Using fallback planning due to parsing error",
                    "tool": "search_and_scrape",
                    "action_input": user_query,
                    "expected_outcome": "Comprehensive search results"
                }
            
            if self.verbose:
                print(f"📋 Plan: {plan['reasoning']}")
                print(f"🎯 Selected tool: {plan['tool']}")
                print(f"📝 Action input: {plan['action_input']}")
            
            # Step 2: Act (Execute tool)
            if self.verbose:
                print("\n2️⃣ ACTION: Executing selected tool...")
            
            tool_results = self._execute_tool(plan['tool'], plan['action_input'])
            
            # Step 3: Observe (Review results)
            if self.verbose:
                print("\n3️⃣ OBSERVATION: Reviewing results...")
                print(f"📊 Information gathered: {len(tool_results)} characters")
                print(f"📄 Preview: {tool_results[:200]}...")
            
            # Step 4: Synthesize (Create final response)
            if self.verbose:
                print("\n4️⃣ SYNTHESIS: Creating comprehensive response...")
            
            final_response = self._synthesize_response(user_query, tool_results, plan['reasoning'])
            
            if self.verbose:
                print("\n✅ ReAct process completed successfully!")
                print("-" * 60)
            
            return final_response
            
        except Exception as e:
            error_msg = f"Error in ReAct process: {str(e)}"
            if self.verbose:
                print(f"❌ {error_msg}")
            return error_msg
    
    def get_tool_info(self) -> dict:
        """Get information about available tools."""
        return {name: {"description": info["description"], "example": info["example"]} 
                for name, info in self.tools.items()}

# Demo functions
def demo_simple_react():
    """Demo the simple ReAct agent."""
    print("🎬 Simple ReAct Agent Demo")
    print("=" * 50)
    print("This demo shows the ReAct pattern in action:")
    print("1️⃣ REASON: AI analyzes query and plans actions")
    print("2️⃣ ACT: AI executes selected tools")
    print("3️⃣ OBSERVE: AI reviews gathered information")
    print("4️⃣ SYNTHESIZE: AI creates comprehensive response")
    
    agent = SimpleReActAgent(verbose=True)
    
    demo_queries = [
        "What are the best programming languages to learn in 2024?",
        "What is artificial intelligence?"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n🎯 Demo Query {i}: '{query}'")
        print("=" * 70)
        
        try:
            response = agent.query(query)
            print(f"\n📋 FINAL RESPONSE:")
            print("-" * 40)
            print(response)
            print("-" * 40)
        except Exception as e:
            print(f"❌ Demo {i} failed: {e}")
        
        if i < len(demo_queries):
            print("\n" + "🔄 " * 15)

if __name__ == "__main__":
    demo_simple_react()