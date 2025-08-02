#!/usr/bin/env python3
"""
Test script for all main interfaces
"""

import sys
import subprocess
import time

def test_simple_interface():
    """Test the simple main interface."""
    print("🧪 Testing Simple Main Interface")
    print("=" * 50)
    
    try:
        from main_simple import run_agent
        
        test_query = "What is artificial intelligence?"
        print(f"Testing query: '{test_query}'")
        
        start_time = time.time()
        response = run_agent(test_query)
        end_time = time.time()
        
        print(f"✅ Response received in {end_time - start_time:.2f} seconds")
        print(f"Response length: {len(response)} characters")
        print(f"Preview: {response[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Simple interface test failed: {e}")
        return False

def test_advanced_interface():
    """Test the advanced main interface."""
    print("\n🧪 Testing Advanced Main Interface")
    print("=" * 50)
    
    try:
        from main_interface import AgenticBrowserInterface
        
        interface = AgenticBrowserInterface()
        
        # Test initialization
        if not interface.initialize_agent():
            print("❌ Failed to initialize agent")
            return False
        
        print("✅ Agent initialized successfully")
        
        # Test query processing
        test_query = "What is machine learning?"
        print(f"Testing query: '{test_query}'")
        
        start_time = time.time()
        response = interface.run_agent(test_query)
        end_time = time.time()
        
        print(f"✅ Response received in {end_time - start_time:.2f} seconds")
        print(f"Response length: {len(response)} characters")
        print(f"Preview: {response[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Advanced interface test failed: {e}")
        return False

def test_streamlit_imports():
    """Test that Streamlit app can be imported."""
    print("\n🧪 Testing Streamlit App Imports")
    print("=" * 50)
    
    try:
        import streamlit_app
        print("✅ Streamlit app imports successfully")
        print("✅ Ready to run with: streamlit run streamlit_app.py")
        return True
        
    except Exception as e:
        print(f"❌ Streamlit import test failed: {e}")
        return False

def show_interface_comparison():
    """Show comparison of different interfaces."""
    print("\n📊 INTERFACE COMPARISON")
    print("=" * 60)
    print()
    print("1️⃣ **Simple CLI Interface** (main_simple.py):")
    print("   • Follows original specification exactly")
    print("   • Minimal code, easy to understand")
    print("   • Perfect for basic usage")
    print("   • Run with: python main_simple.py")
    print()
    print("2️⃣ **Advanced CLI Interface** (main_interface.py):")
    print("   • Rich feature set with commands")
    print("   • Session statistics and help system")
    print("   • Demo mode and verbose controls")
    print("   • Run with: python main_interface.py")
    print()
    print("3️⃣ **Streamlit Web UI** (streamlit_app.py):")
    print("   • Modern web interface")
    print("   • Interactive controls and progress bars")
    print("   • Chat history and example queries")
    print("   • Run with: streamlit run streamlit_app.py")
    print()
    print("🏆 **Recommended for Demo**: Streamlit Web UI")
    print("   • Most visually impressive")
    print("   • Great for screen recording")
    print("   • Interactive and user-friendly")

def show_usage_instructions():
    """Show usage instructions for each interface."""
    print("\n📖 USAGE INSTRUCTIONS")
    print("=" * 60)
    print()
    print("🚀 **Quick Start (Simple CLI):**")
    print("   python main_simple.py")
    print()
    print("🎮 **Full Featured (Advanced CLI):**")
    print("   python main_interface.py")
    print("   Commands: help, demo, stats, verbose on/off, clear")
    print()
    print("🌐 **Web Interface (Streamlit):**")
    print("   streamlit run streamlit_app.py")
    print("   Then open: http://localhost:8501")
    print()
    print("🧪 **Testing & Demos:**")
    print("   python demo_react_complete.py    # ReAct reasoning demo")
    print("   python test_react_agent.py       # ReAct agent testing")
    print("   python test_agentic_tools.py     # Tool system testing")

def main():
    """Run all interface tests."""
    print("🚀 AGENTIC BROWSER ASSISTANT - INTERFACE TESTING")
    print("=" * 70)
    
    tests = [
        test_simple_interface,
        test_advanced_interface,
        test_streamlit_imports
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All interface tests passed!")
        print("✅ All interfaces are ready for use!")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    # Show comparisons and instructions regardless of test results
    show_interface_comparison()
    show_usage_instructions()
    
    print("\n" + "=" * 70)
    print("🎬 READY FOR DEMO!")
    print("Choose your preferred interface and start showcasing!")

if __name__ == "__main__":
    main()