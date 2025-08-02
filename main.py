#!/usr/bin/env python3
"""
Agentic Browser Assistant
An AI agent that "browses" the web via tools to answer queries instantly.
"""

import os
from dotenv import load_dotenv
import json
from cerebras_client import get_completion
from tools import web_search, scrape_url, search_and_scrape, get_available_tools

# Load environment variables
load_dotenv()

class AgenticBrowserAssistant:
    def __init__(self):
        """Initialize the Agentic Browser Assistant."""
        self.api_key = os.getenv('CEREBRAS_API_KEY')
        if not self.api_key:
            raise ValueError("CEREBRAS_API_KEY not found in environment variables")
        
        self.model = "llama3.1-8b"  # You can change this to other models
        
        print("🤖 Agentic Browser Assistant initialized!")
        print(f"✅ Cerebras API key loaded")
        print(f"🧠 Using model: {self.model}")
    
    def use_tool(self, tool_name: str, **kwargs) -> str:
        """Use a specific tool with given parameters."""
        try:
            if tool_name == "web_search":
                return web_search(kwargs.get('query', ''), kwargs.get('max_results', 5))
            elif tool_name == "scrape_url":
                return scrape_url(kwargs.get('url', ''), kwargs.get('max_chars', 2000))
            elif tool_name == "search_and_scrape":
                return search_and_scrape(
                    kwargs.get('query', ''), 
                    kwargs.get('max_results', 3),
                    kwargs.get('scrape_top_n', 2)
                )
            else:
                return f"Unknown tool: {tool_name}"
        except Exception as e:
            return f"Error using tool {tool_name}: {str(e)}"
    
    def decide_and_use_tools(self, user_query: str) -> str:
        """Decide which tools to use based on the user query and execute them."""
        # Get available tools info
        available_tools = get_available_tools()
        tools_description = "\n".join([
            f"- {name}: {info['description']}" 
            for name, info in available_tools.items()
        ])
        
        # Ask AI to decide which tool to use
        decision_prompt = f"""You are an AI assistant that helps users by browsing the web. 
        You have access to these tools:
        
        {tools_description}
        
        User Query: "{user_query}"
        
        Based on the user's query, decide which tool would be most appropriate and return ONLY the tool name and parameters in this exact JSON format:
        {{"tool": "tool_name", "parameters": {{"param1": "value1", "param2": "value2"}}}}
        
        For most queries, use "search_and_scrape" as it provides both search results and detailed content.
        For specific URL requests, use "scrape_url".
        For simple searches without needing full content, use "web_search".
        """
        
        try:
            decision_response = get_completion(decision_prompt, max_tokens=200)
            print(f"🤖 AI Decision: {decision_response}")
            
            # Try to parse the JSON response
            try:
                decision_data = json.loads(decision_response.strip())
                tool_name = decision_data.get('tool', 'search_and_scrape')
                parameters = decision_data.get('parameters', {'query': user_query})
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                print("⚠️  Using fallback tool selection")
                tool_name = 'search_and_scrape'
                parameters = {'query': user_query}
            
            # Execute the chosen tool
            print(f"🔧 Using tool: {tool_name} with parameters: {parameters}")
            tool_result = self.use_tool(tool_name, **parameters)
            
            return tool_result
            
        except Exception as e:
            print(f"❌ Error in tool decision: {e}")
            # Fallback to basic search
            return search_and_scrape(user_query)
    
    def generate_response(self, user_query: str, tool_results: str) -> str:
        """Generate response using Cerebras API based on tool results."""
        try:
            prompt = f"""You are an AI assistant that helps users by browsing the web and finding relevant information. 
            You have access to web search and scraping tools that provide you with up-to-date information.
            Always provide comprehensive, accurate answers and cite your sources when possible.

            User Query: {user_query}
            
            Information gathered from web tools:
            {tool_results}
            
            Based on the information above, provide a comprehensive and helpful answer to the user's query. 
            Structure your response clearly, cite sources with URLs when available, and provide actionable insights.
            If the information seems insufficient, acknowledge this and suggest what additional information might be helpful.
            """
            
            response = get_completion(prompt, model=self.model, max_tokens=1000)
            return response
            
        except Exception as e:
            print(f"❌ API error: {e}")
            return "Sorry, I encountered an error while generating the response."
    
    def process_query(self, query: str) -> str:
        """Process a user query end-to-end using agentic tool selection."""
        print(f"\n🔍 Processing query: '{query}'")
        
        # Step 1: AI decides which tools to use and executes them
        print("🤖 AI is deciding which tools to use...")
        tool_results = self.decide_and_use_tools(query)
        
        if not tool_results or "Error" in tool_results:
            return "❌ Unable to gather information. Please try a different query."
        
        print("✅ Information gathered successfully")
        
        # Step 2: Generate response using AI based on tool results
        print("🧠 Generating comprehensive response...")
        response = self.generate_response(query, tool_results)
        
        return response

def main():
    """Main function to run the Agentic Browser Assistant."""
    try:
        # Initialize the assistant
        assistant = AgenticBrowserAssistant()
        
        print("\n" + "="*60)
        print("🌐 AGENTIC BROWSER ASSISTANT")
        print("Ask me anything and I'll browse the web to find answers!")
        print("Type 'quit' to exit")
        print("="*60)
        
        while True:
            # Get user input
            user_query = input("\n💬 Your query: ").strip()
            
            if user_query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_query:
                print("Please enter a valid query.")
                continue
            
            # Process the query
            response = assistant.process_query(user_query)
            
            # Display the response
            print("\n" + "="*60)
            print("🤖 ASSISTANT RESPONSE:")
            print("="*60)
            print(response)
            print("="*60)
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 