#!/usr/bin/env python3
"""
Test script to verify the Agentic Browser Assistant setup
"""

from cerebras_client import get_completion
from main import AgenticBrowserAssistant

def test_cerebras_client():
    """Test the Cerebras client directly."""
    print("🧪 Testing Cerebras client...")
    try:
        response = get_completion("What is 2+2?", max_tokens=50)
        print(f"✅ Cerebras client works! Response: {response.strip()}")
        return True
    except Exception as e:
        print(f"❌ Cerebras client error: {e}")
        return False

def test_assistant_initialization():
    """Test the assistant initialization."""
    print("\n🧪 Testing assistant initialization...")
    try:
        assistant = AgenticBrowserAssistant()
        print("✅ Assistant initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Assistant initialization error: {e}")
        return False

def test_web_search():
    """Test the web search functionality."""
    print("\n🧪 Testing web search...")
    try:
        assistant = AgenticBrowserAssistant()
        results = assistant.search_web("Python programming", max_results=2)
        if results:
            print(f"✅ Web search works! Found {len(results)} results")
            print(f"First result: {results[0]['title'][:50]}...")
            return True
        else:
            print("❌ No search results returned")
            return False
    except Exception as e:
        print(f"❌ Web search error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Running Agentic Browser Assistant Setup Tests")
    print("=" * 60)
    
    tests = [
        test_cerebras_client,
        test_assistant_initialization,
        test_web_search
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready!")
        print("\n🚀 You can now run: python main.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()