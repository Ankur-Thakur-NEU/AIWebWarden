#!/usr/bin/env python3
"""
Simple Main Interface following the original specification
Uses the ReAct agent for intelligent web browsing
"""

from react_agent_simple import SimpleReActAgent

def run_agent(query):
    """Run the agent with a query and return the response."""
    try:
        # Initialize agent (you could make this global for efficiency)
        agent = SimpleReActAgent(verbose=True)
        result = agent.query(query)
        return result
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    """Main CLI loop."""
    print("🌐 Agentic Browser Assistant")
    print("⚡ Powered by Cerebras | 🧠 ReAct Reasoning")
    print("-" * 50)
    print("Ask me anything and I'll browse the web to find answers!")
    print("Example: 'Find the best laptop under $1000'")
    print()
    
    while True:
        query = input("Enter your query (or 'exit'): ").strip()
        
        if query.lower() in ['exit', 'quit']:
            print("👋 Goodbye!")
            break
            
        if not query:
            print("Please enter a valid query.")
            continue
            
        print("\n🤖 Thinking and browsing the web...")
        print("=" * 60)
        
        response = run_agent(query)
        
        print("=" * 60)
        print("📋 Response:")
        print(response)
        print("\n" + "🔄 " * 20)

if __name__ == "__main__":
    main()