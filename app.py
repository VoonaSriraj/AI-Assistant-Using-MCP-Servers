import os
import asyncio
import logging
import warnings
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from mcp_use import MCPClient, MCPAgent

# Suppress noisy logs
logging.getLogger("mcp_use").setLevel(logging.ERROR)
logging.getLogger("mcp_use.telemetry").setLevel(logging.ERROR)
logging.getLogger().setLevel(logging.WARNING)
warnings.filterwarnings("ignore")

# Load environment variables
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")

# Page configuration
st.set_page_config(
    page_title="MCP AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for theme
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# Theme CSS
def apply_theme():
    if st.session_state.dark_mode:
        st.markdown("""
        <style>
        /* Global dark theme */
        .stApp {
            background: linear-gradient(135deg, #0d1117 0%, #1c1c1c 100%);
            color: #e6edf3;
        }
        
        /* Main content area */
        .main .block-container {
            background: transparent;
            color: #e6edf3;
        }
        
        /* Sidebar */
        .stSidebar {
            background: linear-gradient(180deg, #161b22 0%, #0d1117 100%);
        }
        
        .stSidebar .block-container {
            background: transparent;
            color: #e6edf3;
        }
        
        /* Chat messages */
        .stChatMessage {
            background: rgba(33, 38, 45, 0.8) !important;
            border: 1px solid #30363d;
            border-radius: 12px;
            color: #e6edf3 !important;
        }
        
        /* Text inputs */
        .stTextInput input, .stChatInput input {
            background: rgba(33, 38, 45, 0.9) !important;
            color: #e6edf3 !important;
            border: 1px solid #30363d !important;
            border-radius: 8px;
        }
        
        .stTextInput input::placeholder, .stChatInput input::placeholder {
            color: #7d8590 !important;
        }
        
        /* Buttons */
        .stButton button {
            background: linear-gradient(90deg, #238636 0%, #2ea043 100%);
            color: white;
            border: none;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .stButton button:hover {
            background: linear-gradient(90deg, #2ea043 0%, #238636 100%);
            transform: translateY(-2px);
        }
        
        /* Success/Error messages */
        .stSuccess {
            background: rgba(35, 134, 54, 0.2);
            border: 1px solid #238636;
            color: #4ac26b;
        }
        
        .stError {
            background: rgba(248, 81, 73, 0.2);
            border: 1px solid #f85149;
            color: #ff7b72;
        }
        
        /* Custom components */
        .chat-header {
            background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
            color: white;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }
        
        .stats-container {
            background: rgba(33, 38, 45, 0.6);
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            border: 1px solid #30363d;
            color: #e6edf3;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #e6edf3 !important;
        }
        
        /* Markdown text */
        p, span, div {
            color: #e6edf3 !important;
        }
        
        /* Spinner */
        .stSpinner {
            color: #e6edf3 !important;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        /* Global light theme */
        .stApp {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            color: #1e293b;
        }
        
        /* Main content area */
        .main .block-container {
            background: transparent;
            color: #1e293b;
        }
        
        /* Sidebar */
        .stSidebar {
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        }
        
        .stSidebar .block-container {
            background: transparent;
            color: #1e293b;
        }
        
        /* Chat messages */
        .stChatMessage {
            background: rgba(255, 255, 255, 0.9) !important;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            color: #1e293b !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        /* Text inputs */
        .stTextInput input, .stChatInput input {
            background: rgba(255, 255, 255, 0.9) !important;
            color: #1e293b !important;
            border: 1px solid #d1d5db !important;
            border-radius: 8px;
        }
        
        .stTextInput input::placeholder, .stChatInput input::placeholder {
            color: #9ca3af !important;
        }
        
        /* Buttons */
        .stButton button {
            background: linear-gradient(90deg, #3b82f6 0%, #6366f1 100%);
            color: white;
            border: none;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .stButton button:hover {
            background: linear-gradient(90deg, #6366f1 0%, #3b82f6 100%);
            transform: translateY(-2px);
        }
        
        /* Success/Error messages */
        .stSuccess {
            background: rgba(34, 197, 94, 0.1);
            border: 1px solid #22c55e;
            color: #16a34a;
        }
        
        .stError {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid #ef4444;
            color: #dc2626;
        }
        
        /* Custom components */
        .chat-header {
            background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
            color: white;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .stats-container {
            background: rgba(255, 255, 255, 0.8);
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            border: 1px solid #e2e8f0;
            color: #1e293b;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #1e293b !important;
        }
        
        /* Markdown text */
        p, span, div {
            color: #1e293b !important;
        }
        
        /* Spinner */
        .stSpinner {
            color: #1e293b !important;
        }
        </style>
        """, unsafe_allow_html=True)

# Apply theme
apply_theme()

# Cache the client + agent setup
@st.cache_resource
def init_agent():
    try:
        client = MCPClient()
        llm = ChatGroq(model="llama-3.1-8b-instant")
        agent = MCPAgent(
            llm=llm,
            client=client,
            max_steps=15,
            memory_enabled=True
        )
        return agent, client, True
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}")
        return None, None, False

# Initialize agent
agent, client, init_success = init_agent()

# Sidebar with theme toggle and settings
with st.sidebar:
    st.markdown("### 🎨 Theme Settings")
    
    # Theme toggle button
    theme_icon = "🌙" if not st.session_state.dark_mode else "☀️"
    theme_text = "Dark Mode" if not st.session_state.dark_mode else "Light Mode"
    
    if st.button(f"{theme_icon} {theme_text}", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    
    st.markdown("---")
    
    # App settings
    st.markdown("### ⚙️ Settings")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    # Connection status
    st.markdown("### 📊 Status")
    if init_success:
        st.success("✅ MCP Agent Connected")
    else:
        st.error("❌ MCP Agent Failed")
    
    # Chat statistics
    if "messages" in st.session_state:
        total_messages = len(st.session_state.messages)
        user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
        assistant_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
        
        st.markdown(f"""
        <div class="stats-container">
            <strong>Chat Statistics:</strong><br>
            📝 Total Messages: {total_messages}<br>
            👤 User Messages: {user_messages}<br>
            🤖 AI Messages: {assistant_messages}
        </div>
        """, unsafe_allow_html=True)

# Main chat interface
st.markdown("""
<div class="chat-header">
    <h1>🤖 MCP AI Assistant</h1>
    <p>Powered by LangChain + Groq + MCP | Ask anything you want!</p>
</div>
""", unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
chat_container = st.container()

with chat_container:
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Chat input
if not init_success:
    st.error("❌ Cannot proceed without MCP Agent. Please check your configuration.")
    st.stop()

if prompt := st.chat_input("Ask me anything..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Show typing indicator
        with st.spinner("🤔 Thinking..."):
            async def call_agent(query):
                try:
                    if hasattr(agent, "run"):
                        return await agent.run(query)
                    elif hasattr(agent, "invoke"):
                        return await agent.invoke(query)
                    elif hasattr(agent, "ainvoke"):
                        return await agent.ainvoke(query)
                    else:
                        return "⚠️ MCPAgent has no supported method (`run`, `invoke`, or `ainvoke`)."
                except Exception as e:
                    return f"❌ Error: {str(e)}"
            
            try:
                response = asyncio.run(call_agent(prompt))
            except Exception as e:
                response = f"❌ Failed to get response: {str(e)}"
        
        # Display response
        message_placeholder.markdown(response)
        
        # Add assistant message to history
        st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; opacity: 0.7;">
    <p>🚀 Built with Streamlit • 🧠 Powered by Groq • 🔗 Enhanced with MCP</p>
</div>
""", unsafe_allow_html=True)

# Cleanup function
def on_shutdown():
    if client and hasattr(client, "is_connected") and client.is_connected():
        asyncio.run(client.close_all_sessions())