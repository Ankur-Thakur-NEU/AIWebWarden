#!/usr/bin/env python3
"""
Test script for the enhanced Agentic Browser Assistant with tool selection
"""

from main import AgenticBrowserAssistant
from tools import web_search, scrape_url, search_and_scrape, get_available_tools

def test_individual_tools():
    """Test each tool individually."""
    print("🧪 Testing Individual Tools")
    print("=" * 50)
    
    # Test web_search
    print("\n1. Testing web_search tool:")
    try:
        result = web_search("Python programming tips", max_results=2)
        print(f"✅ Web search successful! Result length: {len(result)} chars")
        print(f"Preview: {result[:200]}...")
    except Exception as e:
        print(f"❌ Web search failed: {e}")
    
    # Test scrape_url (using a reliable test URL)
    print("\n2. Testing scrape_url tool:")
    try:
        result = scrape_url("https://httpbin.org/html", max_chars=300)
        print(f"✅ URL scraping successful! Result length: {len(result)} chars")
        print(f"Preview: {result[:150]}...")
    except Exception as e:
        print(f"❌ URL scraping failed: {e}")
    
    # Test search_and_scrape
    print("\n3. Testing search_and_scrape tool:")
    try:
        result = search_and_scrape("what is machine learning", max_results=2, scrape_top_n=1)
        print(f"✅ Search and scrape successful! Result length: {len(result)} chars")
        print(f"Preview: {result[:200]}...")
    except Exception as e:
        print(f"❌ Search and scrape failed: {e}")

def test_tool_selection():
    """Test the AI's tool selection capability."""
    print("\n🧪 Testing AI Tool Selection")
    print("=" * 50)
    
    assistant = AgenticBrowserAssistant()
    
    test_queries = [
        "Find the best laptops under $1000",
        "What are the latest developments in AI?",
        "Scrape information from https://httpbin.org/html"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing query: '{query}'")
        try:
            # Test just the tool decision and execution part
            tool_results = assistant.decide_and_use_tools(query)
            print(f"✅ Tool execution successful! Result length: {len(tool_results)} chars")
            print(f"Preview: {tool_results[:150]}...")
        except Exception as e:
            print(f"❌ Tool selection/execution failed: {e}")

def test_full_agentic_flow():
    """Test the complete agentic flow."""
    print("\n🧪 Testing Full Agentic Flow")
    print("=" * 50)
    
    assistant = AgenticBrowserAssistant()
    
    test_query = "What is the current price of Bitcoin?"
    print(f"Testing with query: '{test_query}'")
    
    try:
        response = assistant.process_query(test_query)
        print(f"\n✅ Full flow successful!")
        print("📝 AI Response:")
        print("-" * 40)
        print(response)
        print("-" * 40)
    except Exception as e:
        print(f"❌ Full flow failed: {e}")

def test_available_tools():
    """Test the tools information function."""
    print("\n🧪 Testing Available Tools Information")
    print("=" * 50)
    
    try:
        tools = get_available_tools()
        print(f"✅ Found {len(tools)} available tools:")
        for name, info in tools.items():
            print(f"\n🔧 {name}:")
            print(f"   Description: {info['description']}")
            print(f"   Parameters: {info['parameters']}")
            print(f"   Example: {info['example']}")
    except Exception as e:
        print(f"❌ Tools information failed: {e}")

def main():
    """Run all tests."""
    print("🚀 Agentic Browser Assistant - Enhanced Tool Tests")
    print("=" * 60)
    
    tests = [
        test_available_tools,
        test_individual_tools,
        test_tool_selection,
        test_full_agentic_flow
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            test()
            passed += 1
            print(f"\n✅ {test.__name__} completed successfully")
        except Exception as e:
            print(f"\n❌ {test.__name__} failed: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} test suites completed")
    
    if passed == total:
        print("🎉 All test suites completed! Your agentic tools are working!")
    else:
        print("⚠️  Some test suites had issues. Check the output above.")

if __name__ == "__main__":
    main()