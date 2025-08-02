#!/usr/bin/env python3
"""
Streamlit Web UI for Agentic Browser Assistant
"""

import streamlit as st
import time
from react_agent_simple import SimpleReActAgent

# Configure page
st.set_page_config(
    page_title="Agentic Browser Assistant",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'query_count' not in st.session_state:
    st.session_state.query_count = 0
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def initialize_agent():
    """Initialize the ReAct agent."""
    if st.session_state.agent is None:
        try:
            with st.spinner("🚀 Initializing Agentic Browser Assistant..."):
                st.session_state.agent = SimpleReActAgent(verbose=False)
            return True
        except Exception as e:
            st.error(f"❌ Failed to initialize agent: {e}")
            st.error("Please check your .env file and API key.")
            return False
    return True

def run_agent(query):
    """Run the agent with a query."""
    if not st.session_state.agent:
        return "❌ Agent not initialized."
    
    try:
        with st.spinner("🤖 AI is thinking and browsing the web..."):
            progress_bar = st.progress(0)
            progress_bar.progress(25, "🧠 Reasoning about your query...")
            
            start_time = time.time()
            response = st.session_state.agent.query(query)
            end_time = time.time()
            
            progress_bar.progress(100, "✅ Complete!")
            time.sleep(0.5)  # Brief pause to show completion
            progress_bar.empty()
            
            st.session_state.query_count += 1
            
            # Add to chat history
            st.session_state.chat_history.append({
                'query': query,
                'response': response,
                'duration': end_time - start_time,
                'timestamp': time.strftime("%H:%M:%S")
            })
            
            return response, end_time - start_time
            
    except Exception as e:
        return f"❌ Error: {str(e)}", 0

# Main UI
def main():
    # Header
    st.title("🌐 Agentic Browser Assistant")
    st.markdown("**⚡ Powered by Cerebras | 🧠 ReAct Reasoning Pattern**")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Controls")
        
        # Initialize agent
        if st.button("🚀 Initialize Agent", type="primary"):
            initialize_agent()
        
        # Agent status
        if st.session_state.agent:
            st.success("✅ Agent Ready")
        else:
            st.warning("⚠️ Agent Not Initialized")
        
        # Statistics
        st.header("📊 Statistics")
        st.metric("Queries Processed", st.session_state.query_count)
        
        # Settings
        st.header("⚙️ Settings")
        verbose_mode = st.checkbox("Verbose Mode", value=False)
        if st.session_state.agent:
            st.session_state.agent.verbose = verbose_mode
        
        # Example queries
        st.header("💡 Example Queries")
        example_queries = [
            "Find the best laptop under $1000",
            "What are the latest AI developments?",
            "Compare Python vs JavaScript",
            "What is the current Bitcoin price?"
        ]
        
        for example in example_queries:
            if st.button(f"📝 {example[:30]}...", key=f"example_{example}"):
                st.session_state.current_query = example
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Ask Your Question")
        
        # Query input
        query = st.text_input(
            "Enter your query:",
            value=st.session_state.get('current_query', ''),
            placeholder="e.g., Find the best programming languages to learn in 2024",
            key="main_query"
        )
        
        # Clear the current_query after using it
        if 'current_query' in st.session_state:
            del st.session_state.current_query
        
        # Submit button
        if st.button("🔍 Ask Assistant", type="primary", disabled=not st.session_state.agent):
            if query.strip():
                response, duration = run_agent(query)
                
                # Display response
                st.header("📋 Response")
                st.success(f"✅ Completed in {duration:.2f} seconds")
                
                with st.container():
                    st.markdown("### 🤖 AI Response:")
                    st.markdown(response)
                
            else:
                st.warning("Please enter a query.")
    
    with col2:
        st.header("🕒 Recent Queries")
        
        if st.session_state.chat_history:
            # Show recent queries (last 5)
            recent_queries = st.session_state.chat_history[-5:]
            
            for i, item in enumerate(reversed(recent_queries)):
                with st.expander(f"🕐 {item['timestamp']} - {item['query'][:30]}..."):
                    st.write(f"**Query:** {item['query']}")
                    st.write(f"**Duration:** {item['duration']:.2f}s")
                    st.write("**Response:**")
                    st.write(item['response'][:200] + "..." if len(item['response']) > 200 else item['response'])
        else:
            st.info("No queries yet. Ask a question to get started!")
    
    # Features section
    st.header("🚀 Features")
    
    feature_cols = st.columns(4)
    
    with feature_cols[0]:
        st.markdown("""
        **🧠 ReAct Reasoning**
        - Reason → Act → Observe
        - Transparent AI thinking
        - Step-by-step process
        """)
    
    with feature_cols[1]:
        st.markdown("""
        **⚡ Ultra-Fast Inference**
        - Cerebras API power
        - Real-time responses
        - Instant reasoning
        """)
    
    with feature_cols[2]:
        st.markdown("""
        **🔧 Smart Tools**
        - Web search
        - URL scraping
        - Combined operations
        """)
    
    with feature_cols[3]:
        st.markdown("""
        **🎯 Comprehensive**
        - Sourced responses
        - Context-aware
        - Quality synthesis
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Cerebras AI, Streamlit, and Python")

if __name__ == "__main__":
    # Auto-initialize agent on startup
    if not initialize_agent():
        st.stop()
    
    main()