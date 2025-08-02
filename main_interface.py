#!/usr/bin/env python3
"""
Main Interface for Agentic Browser Assistant
Integrates ReAct agent with user-friendly CLI
"""

import os
import sys
import time
from react_agent_simple import SimpleReActAgent

class AgenticBrowserInterface:
    """Main interface for the Agentic Browser Assistant."""
    
    def __init__(self):
        """Initialize the interface."""
        self.agent = None
        self.session_queries = 0
        
    def initialize_agent(self):
        """Initialize the ReAct agent."""
        try:
            print("🚀 Initializing Agentic Browser Assistant...")
            print("⚡ Powered by Cerebras ultra-fast inference")
            print("🧠 Using ReAct reasoning pattern")
            print("-" * 60)
            
            self.agent = SimpleReActAgent(verbose=True)
            
            print("-" * 60)
            print("✅ Agent initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize agent: {e}")
            print("Please check your .env file and API key.")
            return False
    
    def run_agent(self, query: str) -> str:
        """Run the agent with a query."""
        if not self.agent:
            return "❌ Agent not initialized. Please restart the application."
        
        try:
            print(f"\n🔄 Processing query #{self.session_queries + 1}")
            print("⏳ Agent is thinking and browsing...")
            print("=" * 70)
            
            start_time = time.time()
            response = self.agent.query(query)
            end_time = time.time()
            
            self.session_queries += 1
            
            print("=" * 70)
            print(f"✅ Query completed in {end_time - start_time:.2f} seconds")
            print(f"🎯 Total queries this session: {self.session_queries}")
            
            return response
            
        except Exception as e:
            error_msg = f"❌ Error processing query: {str(e)}"
            print(error_msg)
            return error_msg
    
    def show_welcome(self):
        """Show welcome message."""
        print("\n" + "="*80)
        print("🌐 AGENTIC BROWSER ASSISTANT")
        print("="*80)
        print("🧠 AI Agent with ReAct Reasoning | ⚡ Powered by Cerebras")
        print()
        print("Features:")
        print("• 🔍 Intelligent web browsing and information gathering")
        print("• 🧠 Transparent ReAct reasoning (Reason → Act → Observe → Synthesize)")
        print("• ⚡ Ultra-fast inference with Cerebras API")
        print("• 🔧 Autonomous tool selection and execution")
        print("• 📊 Comprehensive, sourced responses")
        print()
        print("Example queries:")
        print('• "Find the best laptop under $1000 for programming"')
        print('• "What are the latest developments in artificial intelligence?"')
        print('• "Compare Python vs JavaScript for web development"')
        print('• "What is the current Bitcoin price and market trends?"')
        print()
        print("Type 'help' for commands, 'exit' to quit")
        print("="*80)
    
    def show_help(self):
        """Show help information."""
        print("\n📖 HELP - Available Commands:")
        print("-" * 40)
        print("• help          - Show this help message")
        print("• exit/quit     - Exit the application")
        print("• clear         - Clear screen")
        print("• stats         - Show session statistics")
        print("• demo          - Run example queries")
        print("• verbose on/off - Toggle verbose mode")
        print()
        print("💡 Tips:")
        print("• Ask specific questions for better results")
        print("• The AI will show its reasoning process")
        print("• Watch for the 4-step ReAct pattern")
        print("• Responses include sources when available")
        print("-" * 40)
    
    def show_stats(self):
        """Show session statistics."""
        print(f"\n📊 Session Statistics:")
        print(f"• Queries processed: {self.session_queries}")
        print(f"• Agent status: {'✅ Ready' if self.agent else '❌ Not initialized'}")
        print(f"• Model: llama3.1-8b (Cerebras)")
        print(f"• Reasoning pattern: ReAct (Reason→Act→Observe→Synthesize)")
    
    def run_demo(self):
        """Run demonstration queries."""
        demo_queries = [
            "What is artificial intelligence?",
            "Find information about Python programming language"
        ]
        
        print("\n🎬 Running Demo Queries...")
        print("This will show the ReAct reasoning process in action.")
        
        for i, query in enumerate(demo_queries, 1):
            print(f"\n🎯 Demo Query {i}: '{query}'")
            if input("Press Enter to continue (or 'skip' to skip): ").lower() == 'skip':
                continue
            
            response = self.run_agent(query)
            print(f"\n📋 Demo Response {i}:")
            print("-" * 50)
            print(response)
            print("-" * 50)
            
            if i < len(demo_queries):
                print("\n" + "🔄 " * 20)
    
    def clear_screen(self):
        """Clear the screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def run_cli(self):
        """Run the command-line interface."""
        # Initialize agent
        if not self.initialize_agent():
            print("❌ Cannot start without agent initialization.")
            return
        
        # Show welcome
        self.show_welcome()
        
        # Main loop
        while True:
            try:
                print(f"\n💬 Query #{self.session_queries + 1}")
                query = input("➤ ").strip()
                
                if not query:
                    print("Please enter a query or command.")
                    continue
                
                # Handle commands
                if query.lower() in ['exit', 'quit', 'q']:
                    print("\n👋 Thank you for using Agentic Browser Assistant!")
                    print(f"📊 Session summary: {self.session_queries} queries processed")
                    break
                elif query.lower() == 'help':
                    self.show_help()
                    continue
                elif query.lower() == 'clear':
                    self.clear_screen()
                    self.show_welcome()
                    continue
                elif query.lower() == 'stats':
                    self.show_stats()
                    continue
                elif query.lower() == 'demo':
                    self.run_demo()
                    continue
                elif query.lower().startswith('verbose'):
                    parts = query.split()
                    if len(parts) > 1:
                        if parts[1].lower() == 'on':
                            self.agent.verbose = True
                            print("✅ Verbose mode enabled")
                        elif parts[1].lower() == 'off':
                            self.agent.verbose = False
                            print("✅ Verbose mode disabled")
                        else:
                            print("Usage: verbose on/off")
                    else:
                        print(f"Current verbose mode: {'ON' if self.agent.verbose else 'OFF'}")
                    continue
                
                # Process query
                response = self.run_agent(query)
                
                # Display response
                print(f"\n📋 RESPONSE:")
                print("=" * 60)
                print(response)
                print("=" * 60)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("Type 'help' for available commands.")

def main():
    """Main function."""
    try:
        interface = AgenticBrowserInterface()
        interface.run_cli()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()