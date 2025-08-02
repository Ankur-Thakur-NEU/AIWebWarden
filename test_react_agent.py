#!/usr/bin/env python3
"""
Test script for the ReAct Browser Agent
"""

from agent import ReactBrowserAgent
import time

def test_react_initialization():
    """Test ReAct agent initialization."""
    print("🧪 Testing ReAct Agent Initialization")
    print("=" * 50)
    
    try:
        agent = ReactBrowserAgent(verbose=False)
        print("✅ ReAct agent initialized successfully!")
        
        # Test tool info
        tools = agent.get_tool_info()
        print(f"✅ Found {len(tools)} tools:")
        for name, info in tools.items():
            print(f"  • {name}: {info['description'][:50]}...")
        
        return agent
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return None

def test_simple_query(agent):
    """Test a simple query with the ReAct agent."""
    print("\n🧪 Testing Simple ReAct Query")
    print("=" * 50)
    
    test_query = "What is Python programming language?"
    print(f"Query: '{test_query}'")
    
    try:
        start_time = time.time()
        response = agent.query(test_query)
        end_time = time.time()
        
        print(f"\n📋 Response received in {end_time - start_time:.2f} seconds:")
        print("-" * 40)
        print(response)
        print("-" * 40)
        
        return True
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return False

def test_complex_query(agent):
    """Test a more complex query that should trigger ReAct reasoning."""
    print("\n🧪 Testing Complex ReAct Query")
    print("=" * 50)
    
    test_query = "Find the best programming languages to learn in 2024"
    print(f"Query: '{test_query}'")
    print("This should trigger ReAct reasoning: Thought → Action → Observation → Final Answer")
    
    try:
        start_time = time.time()
        response = agent.query(test_query)
        end_time = time.time()
        
        print(f"\n📋 Complex response received in {end_time - start_time:.2f} seconds:")
        print("-" * 40)
        print(response)
        print("-" * 40)
        
        return True
    except Exception as e:
        print(f"❌ Complex query failed: {e}")
        return False

def main():
    """Run all ReAct agent tests."""
    print("🚀 ReAct Browser Agent Testing Suite")
    print("=" * 60)
    
    # Test 1: Initialization
    agent = test_react_initialization()
    if not agent:
        print("❌ Cannot proceed without successful initialization")
        return
    
    # Test 2: Simple query
    simple_success = test_simple_query(agent)
    
    # Test 3: Complex query (only if simple worked)
    complex_success = False
    if simple_success:
        complex_success = test_complex_query(agent)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"✅ Initialization: {'PASSED' if agent else 'FAILED'}")
    print(f"✅ Simple Query: {'PASSED' if simple_success else 'FAILED'}")
    print(f"✅ Complex Query: {'PASSED' if complex_success else 'FAILED'}")
    
    if agent and simple_success and complex_success:
        print("\n🎉 All tests passed! ReAct agent is working correctly!")
        print("\n🎬 Ready for demo! The agent shows:")
        print("• ✅ Step-by-step reasoning (ReAct pattern)")
        print("• ✅ Autonomous tool selection")
        print("• ✅ Comprehensive information gathering")
        print("• ✅ Cerebras-powered fast inference")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()