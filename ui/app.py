import streamlit as st
import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.team import DAForgeTeam

# Page configuration
st.set_page_config(
    page_title="DA-Forge: Autonomous Developer Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better visibility and clean design
st.markdown("""
<style>
    /* Main app background - light blue for better visibility */
    .stApp {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 30%, #90caf9 70%, #64b5f6 100%);
        background-attachment: fixed;
    }
    
    /* Main container - white background for content */
    .main .block-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 2rem;
        border: 1px solid rgba(0, 0, 0, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin-top: 1rem;
    }
    
    /* Sidebar styling - dark but readable */
    .css-1d391kg {
        background: linear-gradient(135deg, #343a40 0%, #495057 50%, #343a40 100%);
    }
    
    /* Main header with better contrast */
    .main-header {
        background: linear-gradient(135deg, #007bff 0%, #0056b3 50%, #004085 100%);
        padding: 2.5rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: black;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0, 123, 255, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Status cards with high contrast */
    .status-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        color: #212529;
        border: 1px solid #dee2e6;
    }
    
    .success-card {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left-color: #28a745;
        color: #155724;
    }
    
    .error-card {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border-left-color: #dc3545;
        color: #721c24;
    }
    
    /* Instructions section with good contrast */
    .feature-highlight {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid #2196f3;
        box-shadow: 0 4px 15px rgba(33, 150, 243, 0.2);
        color: #0d47a1;
        border: 1px solid #90caf9;
    }
    
    .feature-highlight h4 {
        color: #0d47a1;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    
    .feature-highlight ol {
        color: #1565c0;
        font-weight: 500;
    }
    
    /* Sidebar header */
    .sidebar-header {
        background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
        color: black;
        padding: 1.2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,123,255,0.3);
    }
    
    /* Progress container */
    .progress-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        border: 1px solid #dee2e6;
    }
    
    /* JSON container */
    .json-container {
        background: #2d3748;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #4a5568;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Text styling for better readability */
    .main .stMarkdown {
        color: #212529;
    }
    
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
        color: #212529;
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
        color: black;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(0, 123, 255, 0.4);
    }
    
    /* Text area styling */
    .stTextArea textarea {
        background: #ffffff;
        border: 2px solid #ced4da;
        border-radius: 10px;
        color: #212529;
    }
    
    /* Footer styling */
    .footer-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-top: 2rem;
        text-align: center;
        border: 1px solid #dee2e6;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .footer-section h3 {
        color: #212529;
        margin-bottom: 1rem;
    }
    
    .footer-section p {
        color: #495057;
        margin-bottom: 0.5rem;
    }
    
    /* Sidebar text colors */
    .css-1d391kg .stMarkdown {
        color: black;
    }
    
    /* Example prompt styling */
    .example-button {
        background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
        color: black;
        padding: 10px 15px;
        border-radius: 8px;
        margin: 5px 0;
        border: none;
        width: 100%;
        text-align: left;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 123, 255, 0.2);
    }
    
    .example-button:hover {
        background: linear-gradient(135deg, #0056b3 0%, #004085 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'team' not in st.session_state:
    st.session_state.team = None
if 'execution_result' not in st.session_state:
    st.session_state.execution_result = None
if 'progress_messages' not in st.session_state:
    st.session_state.progress_messages = []
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False

def update_progress(stage: str, message: str):
    """Update progress in session state"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.progress_messages.append({
        "stage": stage,
        "message": message,
        "timestamp": timestamp
    })

def initialize_team(llm_provider: str) -> DAForgeTeam:
    """Initialize the DA-Forge team"""
    team = DAForgeTeam(llm_provider=llm_provider)
    team.set_progress_callback(update_progress)
    return team

async def process_workflow_request(user_input: str, llm_provider: str) -> Dict[str, Any]:
    """Process the workflow generation request with real-time updates"""
    st.session_state.is_processing = True
    st.session_state.progress_messages = []
    
    # Add immediate progress update
    update_progress("input", "🔄 Starting workflow generation...")
    
    try:
        # Initialize team
        team = initialize_team(llm_provider)
        st.session_state.team = team
        
        # Execute workflow generation
        result = await team.execute_workflow_generation(user_input)
        
        st.session_state.is_processing = False
        return result
        
    except Exception as e:
        st.session_state.is_processing = False
        update_progress("error", f"❌ Error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "stage": "execution"
        }

def render_header():
    """Render the premium header"""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 DA-Forge: Autonomous Developer Agent</h1>
        <p>🏆 Hackathon-Winning AI System for n8n Workflow Generation</p>
        <p>✨ Transform natural language into production-ready workflows instantly</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render the simplified sidebar with configuration"""
    st.sidebar.markdown('<div class="sidebar-header">⚙️ DA-Forge Configuration</div>', unsafe_allow_html=True)
    
    # LLM Provider selection
    st.sidebar.markdown("### 🧠 AI Provider")
    llm_provider = st.sidebar.selectbox(
        "Choose your LLM",
        ["openrouter", "anthropic"],
        help="Select your preferred AI provider for workflow planning"
    )
    
    # API Key configuration
    if llm_provider == "openrouter":
        api_key = st.sidebar.text_input(
            "🔑 OpenRouter API Key",
            type="password",
            help="Get your key from: https://openrouter.ai/"
        )
        if api_key:
            os.environ["OPENROUTER_API_KEY"] = api_key
            st.sidebar.success("✅ API Key configured!")
        else:
            st.sidebar.info("💡 Demo mode: Smart fallback planning")
    else:
        api_key = st.sidebar.text_input(
            "🔑 Anthropic API Key", 
            type="password",
            help="Get your key from: https://console.anthropic.com/"
        )
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key
            st.sidebar.success("✅ API Key configured!")
        else:
            st.sidebar.info("💡 Demo mode: Smart fallback planning")
    
    # Set JSON Download as default (remove direct deploy option)
    output_mode = "JSON Download"
    os.environ["MOCK_DEPLOYMENT"] = "true"
    st.sidebar.info("📦 JSON download mode enabled")
    
    # Quick Actions
    st.sidebar.markdown("### ⚡ Quick Actions")
    if st.sidebar.button("🔄 Reset Configuration"):
        for key in ["OPENROUTER_API_KEY", "ANTHROPIC_API_KEY"]:
            if key in os.environ:
                del os.environ[key]
        st.rerun()
    
    if st.sidebar.button("🗑️ Clear Session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    return llm_provider, output_mode

def render_progress():
    """Render enhanced real-time progress messages"""
    if st.session_state.progress_messages:
        st.markdown('<div class="progress-container">', unsafe_allow_html=True)
        
        progress_steps = ["input", "planning", "generation", "deployment", "complete"]
        current_step = 0
        
        # Find current step
        for msg in st.session_state.progress_messages:
            if msg["stage"] in progress_steps:
                current_step = max(current_step, progress_steps.index(msg["stage"]))
        
        # Progress bar with percentage
        progress_value = min((current_step + 1) * 20, 100)
        st.progress(progress_value)
        st.markdown(f"**Progress: {progress_value}% Complete**")
        
        # Stage indicators with status
        cols = st.columns(5)
        stage_names = ["📝 Input", "🧠 Planning", "⚙️ Generation", "🚀 Deployment", "✅ Complete"]
        stage_status = ["✅", "⏳", "⏱️", "🔄", "🎉"]
        
        for i, (col, stage_name) in enumerate(zip(cols, stage_names)):
            with col:
                if i < current_step:
                    st.markdown(f"<div style='text-align: center; color: #28a745; font-weight: bold;'>{stage_names[i]} ✅</div>", unsafe_allow_html=True)
                elif i == current_step:
                    st.markdown(f"<div style='text-align: center; color: #ffc107; font-weight: bold;'>{stage_names[i]} ⏳</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align: center; color: #6c757d;'>{stage_names[i]} ⏸️</div>", unsafe_allow_html=True)
        
        # Real-time messages with timestamps
        st.markdown("#### 📋 Real-time Activity Log")
        
        # Show all messages, most recent first
        for msg in reversed(st.session_state.progress_messages[-5:]):  # Show last 5 messages
            stage_emoji = {
                "input": "📝",
                "planning": "🧠", 
                "generation": "⚙️",
                "deployment": "🚀",
                "complete": "✅",
                "error": "❌"
            }.get(msg["stage"], "ℹ️")
            
            css_class = "success-card" if msg["stage"] == "complete" else "error-card" if msg["stage"] == "error" else "status-card"
            
            # Add blinking effect for current activity
            blink_style = "animation: blink 1s infinite;" if msg == st.session_state.progress_messages[-1] and msg["stage"] not in ["complete", "error"] else ""
            
            st.markdown(f"""
            <div class="{css_class}" style="{blink_style}">
                <strong>{stage_emoji} {msg["timestamp"]}</strong><br>
                {msg["message"]}
            </div>
            """, unsafe_allow_html=True)
        
        # Estimated time remaining
        if current_step < len(progress_steps) - 1:
            remaining_steps = len(progress_steps) - current_step - 1
            estimated_time = remaining_steps * 10  # Rough estimate
            st.info(f"⏱️ Estimated time remaining: ~{estimated_time} seconds")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add CSS for blinking animation
        st.markdown("""
        <style>
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0.7; }
        }
        </style>
        """, unsafe_allow_html=True)

def render_results(result: Dict[str, Any], output_mode: str):
    """Render execution results with prominent download functionality"""
    if result["success"]:
        st.markdown("""
        <div class="success-card">
            <h3>🎉 Workflow Successfully Generated!</h3>
            <p>Your autonomous agent has created a production-ready n8n workflow</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Prominent download section
        st.markdown("## 📥 Download Your Workflow")
        
        workflow_json = result.get('workflow_json', {})
        json_str = json.dumps(workflow_json, indent=2)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Large, prominent download button
            st.download_button(
                label="📄 Download n8n Workflow JSON",
                data=json_str,
                file_name=f"da_forge_workflow_{result.get('workflow_id', 'unknown')[:8]}.json",
                mime="application/json",
                help="Download the complete workflow to import into n8n",
                use_container_width=True
            )
            
            # File info
            st.success(f"✅ File ready: {len(json_str):,} characters")
            st.info(f"📦 File size: {len(json_str.encode('utf-8'))//1024}KB")
        
        with col2:
            # Workflow stats
            nodes = workflow_json.get('nodes', [])
            connections = workflow_json.get('connections', {})
            
            st.metric("📊 Total Nodes", len(nodes))
            st.metric("🔗 Connections", len(connections))
        
        # Import instructions
        st.markdown("""
        <div class="feature-highlight">
            <h4>📖 How to Import into n8n:</h4>
            <ol>
                <li><strong>Download</strong> the JSON file using the button above</li>
                <li><strong>Open</strong> your n8n instance</li>
                <li><strong>Click</strong> "+ Add workflow" or "Import"</li>
                <li><strong>Select</strong> "Import from file"</li>
                <li><strong>Upload</strong> the downloaded JSON file</li>
                <li><strong>Activate</strong> your workflow and you're done! 🎉</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Detailed workflow information
        st.markdown("### 📊 Workflow Details")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'''
            <div class="status-card">
                <strong>📛 Name:</strong><br>
                {result.get('workflow_name', 'N/A')}
            </div>
            ''', unsafe_allow_html=True)
            
        with col2:
            st.markdown(f'''
            <div class="status-card">
                <strong>🆔 Workflow ID:</strong><br>
                <code>{result.get('workflow_id', 'N/A')}</code>
            </div>
            ''', unsafe_allow_html=True)
        
        if result.get('execution_summary'):
            summary = result['execution_summary']
            st.markdown(f'''
            <div class="status-card">
                <strong>⚙️ Nodes:</strong> {summary.get('total_nodes', 0)} | 
                <strong>🎯 Complexity:</strong> {summary.get('complexity', 'unknown').title()}
            </div>
            ''', unsafe_allow_html=True)
        
        # JSON viewer (collapsible)
        if st.checkbox("🔍 Show Complete Workflow JSON", help="View the complete workflow structure"):
            st.markdown("#### 📄 Complete Workflow JSON")
            st.markdown('<div class="json-container">', unsafe_allow_html=True)
            st.json(workflow_json)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Copy to clipboard button
            st.code(json_str, language="json")
    
    else:
        st.markdown(f"""
        <div class="error-card">
            <h3>❌ Workflow Generation Failed</h3>
            <p><strong>Error:</strong> {result.get('error', 'Unknown error')}</p>
            <p><strong>Stage:</strong> {result.get('stage', 'Unknown')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show partial results if available
        if result.get('workflow_json'):
            st.markdown("### 📄 Partial Workflow JSON (Generated but not fully completed)")
            
            workflow_json = result['workflow_json']
            json_str = json.dumps(workflow_json, indent=2)
            
            # Still allow download of partial results
            st.download_button(
                label="📄 Download Partial Workflow JSON",
                data=json_str,
                file_name=f"da_forge_partial_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                help="Download the partial workflow (may need manual fixes)"
            )
            
            st.json(workflow_json)

def main():
    """Main application function"""
    render_header()
    
    # Sidebar configuration
    llm_provider, output_mode = render_sidebar()
    
    # Main content area with enhanced layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("### 💬 Describe Your Workflow")
        
        # Handle example input population
        initial_value = ""
        if hasattr(st.session_state, 'selected_example'):
            initial_value = st.session_state.selected_example
            del st.session_state.selected_example
        
        user_input = st.text_area(
            "What workflow would you like to create?",
            value=initial_value,
            placeholder="Example: Create a comprehensive webhook system that receives data, validates it, processes it through multiple stages, sends notifications via Slack and email, logs to database, and generates reports...",
            height=120,
            help="Describe in natural language what you want your workflow to do. Be as detailed as possible for better results!"
        )
        
        # Enhanced Generate button
        generate_button = st.button(
            "🚀 Generate & Process Workflow",
            type="primary",
            disabled=st.session_state.is_processing or not user_input.strip(),
            help="Click to automatically generate your n8n workflow"
        )
    
    with col2:
        st.markdown("### ℹ️ Instructions")
        st.markdown("""
        <div class="feature-highlight">
            <h4>🎯 How to Use DA-Forge:</h4>
            <ol>
                <li><strong>Configure</strong> your API keys in the sidebar (optional)</li>
                <li><strong>Describe</strong> your workflow in detail below</li>
                <li><strong>Click Generate</strong> to create your workflow</li>
                <li><strong>Download JSON</strong> and import into n8n</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced Example prompts with working functionality
        st.markdown("### 💡 Example Workflows")
        
        complex_examples = [
            {
                "title": "🔗 Advanced Webhook System",
                "prompt": "Create a webhook that receives JSON data, validates the schema, processes it through multiple transformation stages, sends Slack notifications for important events, stores data in PostgreSQL, triggers email alerts for errors, and generates daily summary reports"
            },
            {
                "title": "📡 RSS Monitoring Pipeline", 
                "prompt": "Build an RSS feed monitor that checks multiple sources every hour, filters for specific keywords, removes duplicates, enriches content with AI analysis, sends formatted notifications to Discord and Slack, saves to Google Sheets, and creates weekly digest emails"
            },
            {
                "title": "📊 Data Processing Workflow",
                "prompt": "Design a system that processes uploaded CSV files, validates data quality, performs statistical analysis, generates visualizations, sends reports via email, uploads results to cloud storage, and triggers downstream API calls based on findings"
            },
            {
                "title": "🔄 API Integration Hub",
                "prompt": "Create a workflow that integrates with multiple APIs (GitHub, Jira, Slack), synchronizes data between systems, handles rate limiting and retries, logs all activities, sends status updates, and maintains data consistency across platforms"
            },
            {
                "title": "🎯 E-commerce Automation",
                "prompt": "Build an order processing system that monitors new orders, validates inventory, processes payments, updates multiple databases, sends order confirmations, triggers fulfillment workflows, handles exceptions, and generates business analytics"
            },
            {
                "title": "🌐 Social Media Manager",
                "prompt": "Design a social media automation system that schedules posts across platforms, monitors mentions and hashtags, analyzes sentiment, responds to customer queries, generates engagement reports, and optimizes posting times based on analytics"
            }
        ]
        
        for example in complex_examples:
            if st.button(
                f"📝 {example['title']}", 
                key=f"example_{hash(example['title'])}",
                help=f"Click to use: {example['prompt'][:100]}...",
                use_container_width=True
            ):
                st.session_state.selected_example = example['prompt']
                st.rerun()
    
    # Process workflow generation with real-time updates
    if generate_button and user_input.strip():
        # Clear previous results
        st.session_state.execution_result = None
        st.session_state.progress_messages = []
        
        # Create placeholder for real-time updates
        progress_placeholder = st.empty()
        result_placeholder = st.empty()
        
        with st.spinner("🤖 DA-Forge is working its magic..."):
            try:
                # Show initial progress
                with progress_placeholder.container():
                    st.markdown("### 📈 Generation Progress")
                    st.progress(10)
                    st.info("🔄 Initializing workflow generation...")
                
                # Run async function
                result = asyncio.run(process_workflow_request(user_input, llm_provider))
                st.session_state.execution_result = result
                
                # Clear placeholders and rerun to show final results
                progress_placeholder.empty()
                result_placeholder.empty()
                st.rerun()
                
            except Exception as e:
                progress_placeholder.empty()
                result_placeholder.empty()
                st.error(f"❌ System Error: {str(e)}")
    
    # Show progress if processing
    if st.session_state.is_processing and st.session_state.progress_messages:
        st.markdown("### 📈 Real-time Progress")
        render_progress()
    
    # Show results after completion
    if st.session_state.execution_result and not st.session_state.is_processing:
        st.markdown("---")
        st.markdown("### 🎯 Results")
        render_results(st.session_state.execution_result, output_mode)
    
    # Enhanced Debug and Memory info with compact layout
    if st.session_state.team and st.checkbox("🔍 Show Debug Information", help="View detailed system information"):
        with st.expander("🛠️ System Debug Information"):
            try:
                memory_summary = asyncio.run(st.session_state.team.get_memory_summary())
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### 💾 Memory State")
                    st.json(memory_summary)
                
                with col2:
                    st.markdown("#### ⚙️ System Info")
                    st.json({
                        "llm_provider": llm_provider,
                        "output_mode": output_mode,
                        "mock_deployment": os.environ.get("MOCK_DEPLOYMENT", "true"),
                        "api_configured": bool(os.environ.get("OPENROUTER_API_KEY") or os.environ.get("ANTHROPIC_API_KEY"))
                    })
            except Exception as e:
                st.error(f"Debug info error: {e}")
    
    # Enhanced Footer - single version
    st.markdown("---")
    st.markdown("""
    <div class="footer-section">
        <h3>🏆 DA-Forge: Autonomous Developer Agent</h3>
        <p><strong>Award-Winning AI System for n8n Workflow Generation</strong></p>
        <p>Built for Agent Development Kit Hackathon with Google Cloud</p>
        <p><strong>About this project:</strong> DA-Forge uses advanced multi-agent AI architecture to automatically transform natural language descriptions into complete, production-ready n8n workflows. Our system features intelligent planning, robust error handling, and seamless JSON export for easy workflow deployment.</p>
        <p>✨ Transform ideas into automation in seconds ✨</p>
        <div style="margin-top: 1.5rem;">
            <span style="background: #fd7e14; color: black; padding: 8px 16px; border-radius: 20px; margin: 0 8px; font-size: 14px; font-weight: bold;">🎯 Smart Planning</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()