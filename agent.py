#!/usr/bin/env python3
"""
ReAct Agent Implementation using LangChain
Implements Reason-Action-Observation pattern for agentic web browsing
"""

import os
from typing import Any, List, Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from cerebras_client import get_completion
from tools import web_search, scrape_url, search_and_scrape

class CerebrasLLM(LLM):
    """Custom LangChain LLM wrapper for Cerebras API."""
    
    model_name: str = "llama3.1-8b"
    max_tokens: int = 1000
    temperature: float = 0.7
    
    @property
    def _llm_type(self) -> str:
        return "cerebras"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the Cerebras API."""
        try:
            response = get_completion(
                prompt, 
                model=self.model_name, 
                max_tokens=self.max_tokens
            )
            return response
        except Exception as e:
            return f"Error calling Cerebras API: {str(e)}"
    
    @property
    def _identifying_params(self) -> dict:
        """Get the identifying parameters."""
        return {
            "model_name": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

def create_web_search_tool():
    """Create a LangChain tool for web search."""
    def search_wrapper(query: str) -> str:
        """Wrapper for web search that returns formatted results."""
        try:
            results = web_search(query, max_results=5)
            if not results or "Error" in results:
                return f"No search results found for: {query}"
            return results
        except Exception as e:
            return f"Error in web search: {str(e)}"
    
    return Tool(
        name="WebSearch",
        func=search_wrapper,
        description="Search the web for information about any topic. Input should be a search query string."
    )

def create_scrape_tool():
    """Create a LangChain tool for URL scraping."""
    def scrape_wrapper(url: str) -> str:
        """Wrapper for URL scraping that handles errors."""
        try:
            content = scrape_url(url, max_chars=2000)
            if not content or "Error" in content:
                return f"Could not scrape content from: {url}"
            return content
        except Exception as e:
            return f"Error scraping URL: {str(e)}"
    
    return Tool(
        name="ScrapeURL",
        func=scrape_wrapper,
        description="Extract text content from a specific URL. Input should be a valid URL string."
    )

def create_search_and_scrape_tool():
    """Create a LangChain tool for combined search and scrape."""
    def search_scrape_wrapper(query: str) -> str:
        """Wrapper for search and scrape that returns comprehensive results."""
        try:
            results = search_and_scrape(query, max_results=3, scrape_top_n=2)
            if not results or "Error" in results:
                return f"No comprehensive results found for: {query}"
            return results
        except Exception as e:
            return f"Error in search and scrape: {str(e)}"
    
    return Tool(
        name="SearchAndScrape",
        func=search_scrape_wrapper,
        description="Search the web and scrape content from top results for comprehensive information. Input should be a search query string."
    )

def create_react_prompt():
    """Create the ReAct prompt template."""
    template = """You are an intelligent web browsing assistant that uses tools to find information. 
You follow the ReAct pattern: Reason about what to do, then Act using tools, then Observe the results.

You have access to these tools:
{tools}

Tool names: {tool_names}

Use the following format:

Thought: I need to understand what the user is asking and decide which tool would be most helpful.
Action: [tool_name]
Action Input: [the input to the tool]
Observation: [the result of the action]
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now have enough information to provide a comprehensive answer.
Final Answer: [your final response to the user based on all observations]

Important guidelines:
- Always start with a Thought about what you need to do
- Use WebSearch for general queries that need current information
- Use ScrapeURL when you have a specific URL to extract content from
- Use SearchAndScrape when you need comprehensive information with detailed content
- Provide sources and URLs in your final answer when available
- If a tool returns an error, try a different approach or tool

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

    return PromptTemplate.from_template(template)

class ReactBrowserAgent:
    """ReAct-based browser agent for autonomous web browsing."""
    
    def __init__(self, model_name: str = "llama3.1-8b", verbose: bool = True):
        """Initialize the ReAct browser agent."""
        self.model_name = model_name
        self.verbose = verbose
        
        # Initialize Cerebras LLM
        self.llm = CerebrasLLM(model_name=model_name)
        
        # Create tools
        self.tools = [
            create_web_search_tool(),
            create_scrape_tool(),
            create_search_and_scrape_tool(),
        ]
        
        # Create prompt
        self.prompt = create_react_prompt()
        
        # Create agent
        self.agent = create_react_agent(self.llm, self.tools, self.prompt)
        
        # Create executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=self.verbose,
            handle_parsing_errors=True,
            max_iterations=5,  # Prevent infinite loops
            return_intermediate_steps=True
        )
        
        print(f"🤖 ReAct Browser Agent initialized!")
        print(f"🧠 Model: {model_name}")
        print(f"🔧 Tools: {len(self.tools)} available")
        print(f"📝 Verbose mode: {verbose}")
    
    def query(self, question: str) -> str:
        """Process a query using the ReAct pattern."""
        try:
            print(f"\n🔍 Processing ReAct query: '{question}'")
            print("🧠 Agent will now Reason → Act → Observe...")
            print("-" * 60)
            
            result = self.agent_executor.invoke({"input": question})
            
            print("-" * 60)
            print("✅ ReAct process completed!")
            
            return result.get("output", "No output generated")
            
        except Exception as e:
            error_msg = f"Error in ReAct agent: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def get_tool_info(self) -> dict:
        """Get information about available tools."""
        tool_info = {}
        for tool in self.tools:
            tool_info[tool.name] = {
                "description": tool.description,
                "function": tool.func.__name__
            }
        return tool_info

# Demo and testing functions
def test_react_agent():
    """Test the ReAct agent with sample queries."""
    print("🧪 Testing ReAct Browser Agent")
    print("=" * 50)
    
    # Initialize agent
    agent = ReactBrowserAgent(verbose=True)
    
    # Test queries
    test_queries = [
        "What are the best programming languages to learn in 2024?",
        "Find information about the latest AI developments",
        "What is the current price of Bitcoin?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🎯 Test {i}: {query}")
        print("=" * 60)
        
        try:
            response = agent.query(query)
            print(f"\n📋 Final Response:")
            print(response)
        except Exception as e:
            print(f"❌ Test {i} failed: {e}")
        
        print("\n" + "🔄 " * 20)

def demo_react_reasoning():
    """Demo showing the ReAct reasoning process."""
    print("🎬 ReAct Reasoning Demo")
    print("=" * 50)
    print("This demo shows how the AI agent reasons step-by-step:")
    print("• Thought: Analyzes what needs to be done")
    print("• Action: Chooses and uses appropriate tools") 
    print("• Observation: Reviews results from tools")
    print("• Repeats until sufficient information is gathered")
    print("• Final Answer: Synthesizes comprehensive response")
    
    agent = ReactBrowserAgent(verbose=True)
    
    demo_query = "Find the best laptop under $1000 for programming"
    print(f"\n🎯 Demo Query: '{demo_query}'")
    print("\nWatch the ReAct pattern in action:")
    
    try:
        response = agent.query(demo_query)
        print(f"\n🎉 Demo completed! The agent used ReAct reasoning to:")
        print("✅ Break down the problem")
        print("✅ Select appropriate tools")
        print("✅ Gather comprehensive information") 
        print("✅ Synthesize a helpful response")
    except Exception as e:
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    # Run tests
    test_react_agent()