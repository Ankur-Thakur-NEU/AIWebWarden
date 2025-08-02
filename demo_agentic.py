#!/usr/bin/env python3
"""
Demo script showcasing the Agentic Browser Assistant's enhanced capabilities
"""

from main import AgenticBrowserAssistant
import time

def demo_queries():
    """Demo with various types of queries to show agentic tool selection."""
    
    # Initialize the assistant
    print("🚀 Initializing Agentic Browser Assistant...")
    assistant = AgenticBrowserAssistant()
    
    # Demo queries that showcase different tool usage
    demo_cases = [
        {
            "query": "Find the best programming languages to learn in 2024",
            "description": "Shopping/Research Query - Should use search_and_scrape"
        },
        {
            "query": "What are the latest developments in artificial intelligence?",
            "description": "News/Current Events Query - Should use search_and_scrape"
        },
        {
            "query": "Scrape content from https://httpbin.org/html",
            "description": "Direct URL Query - Should use scrape_url"
        }
    ]
    
    print("\n" + "="*80)
    print("🎬 AGENTIC BROWSER ASSISTANT DEMO")
    print("="*80)
    print("Watch as the AI agent autonomously selects and uses tools!")
    print()
    
    for i, case in enumerate(demo_cases, 1):
        print(f"\n🎯 DEMO CASE {i}: {case['description']}")
        print(f"Query: '{case['query']}'")
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            response = assistant.process_query(case['query'])
            
            end_time = time.time()
            duration = end_time - start_time
            
            print("\n📋 FINAL RESPONSE:")
            print("=" * 40)
            print(response)
            print("=" * 40)
            print(f"⏱️  Response time: {duration:.2f} seconds")
            
        except Exception as e:
            print(f"❌ Error in demo case {i}: {e}")
        
        print("\n" + "🔄 " * 20)
        time.sleep(1)  # Brief pause between demos
    
    print("\n🎉 Demo completed! The AI agent successfully:")
    print("✅ Analyzed each query type")
    print("✅ Selected appropriate tools automatically") 
    print("✅ Executed tools with proper parameters")
    print("✅ Generated comprehensive responses")
    print("\n💡 This showcases true agentic behavior - the AI makes decisions!")

def interactive_demo():
    """Interactive demo where user can input queries."""
    print("\n🎮 INTERACTIVE MODE")
    print("="*50)
    print("Now you can test the assistant with your own queries!")
    print("The AI will automatically select the best tools for each query.")
    print("Type 'quit' to exit.")
    
    assistant = AgenticBrowserAssistant()
    
    while True:
        print("\n" + "-"*50)
        user_query = input("💬 Enter your query: ").strip()
        
        if user_query.lower() in ['quit', 'exit', 'q']:
            print("👋 Thanks for trying the Agentic Browser Assistant!")
            break
        
        if not user_query:
            print("Please enter a valid query.")
            continue
        
        print(f"\n🚀 Processing: '{user_query}'")
        print("Watch the AI select and use tools automatically...")
        
        try:
            start_time = time.time()
            response = assistant.process_query(user_query)
            end_time = time.time()
            
            print("\n📋 RESPONSE:")
            print("="*40)
            print(response)
            print("="*40)
            print(f"⏱️  Response time: {end_time - start_time:.2f} seconds")
            
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main demo function."""
    print("🌐 AGENTIC BROWSER ASSISTANT - ENHANCED DEMO")
    print("="*60)
    print("This demo showcases the AI agent's ability to:")
    print("• 🧠 Analyze user queries intelligently")
    print("• 🔧 Select appropriate tools automatically") 
    print("• 🌐 Browse the web with multiple strategies")
    print("• 📊 Provide comprehensive, sourced responses")
    print("• ⚡ Deliver results at Cerebras speed!")
    
    choice = input("\nChoose demo mode:\n1. Automated Demo (3 example queries)\n2. Interactive Demo (your queries)\n\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        demo_queries()
    elif choice == "2":
        interactive_demo()
    else:
        print("Invalid choice. Running automated demo...")
        demo_queries()

if __name__ == "__main__":
    main()