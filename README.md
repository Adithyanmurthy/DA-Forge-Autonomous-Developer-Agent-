# DA-Forge: Autonomous Developer Agent for Workflow Generation

**Winner-ready hackathon project for Agent Development Kit Hackathon with Google Cloud**

DA-Forge is an autonomous multi-agent system that automatically plans, generates, and deploys complete n8n workflows from natural language descriptions. Built with Google's Agent Development Kit (ADK) architecture.

## Quick Start Guide

### Prerequisites

- Python 3.9 or higher
- Git
- Terminal/Command Prompt

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/da_forge_adk.git
cd da_forge_adk
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set API Keys

Choose one of the following LLM providers:

**Option A: OpenRouter (Recommended)**

```bash
export OPENROUTER_API_KEY="your_openrouter_key_here"
```

**Option B: Anthropic Claude**

```bash
export ANTHROPIC_API_KEY="your_anthropic_key_here"
```

**Optional: n8n Deployment Configuration**

```bash
export N8N_BASE_URL="http://localhost:5678"
export N8N_API_KEY="your_n8n_api_key"
```

### Step 4: Launch the Application

```bash
streamlit run ui/app.py
```

### Step 5: Use the System

1. Open your web browser to `http://localhost:8501`
2. Enter your workflow description in plain English
3. Click "Generate & Process Workflow"
4. Download the generated n8n workflow JSON
5. Import the JSON into your n8n instance

## Core Features

- **One-Click Operation** - No terminal interaction needed
- **Natural Language Input** - Describe workflows in plain English
- **Automatic Planning** - AI plans the complete workflow structure
- **JSON Generation** - Creates valid n8n workflow JSON
- **Auto-Deployment** - Deploys to n8n and returns live URL
- **Real-time Progress** - Visual progress tracking
- **Mock Mode** - Works without n8n instance for demos

## Project Architecture

```
da_forge_adk/
├── agents/              # ADK-compliant agents
│   ├── input_agent.py   # Processes user input
│   ├── planner_agent.py # Plans workflow with LLM
│   └── team.py         # Coordinates all agents
├── tools/              # Specialized tools
│   ├── workflow_generator.py  # Generates n8n JSON
│   └── deploy_tool.py         # Deploys to n8n
├── memory/             # Short-term memory
│   └── short_term.py   # Stores execution state
├── ui/                 # Streamlit interface
│   └── app.py         # Main UI application
├── examples/           # Example usage
│   └── run_da_forge.py # Programmatic examples
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Detailed Setup Instructions

### 1. Environment Setup

**Windows:**

```cmd
# Create virtual environment
python -m venv da_forge_env
da_forge_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**macOS/Linux:**

```bash
# Create virtual environment
python3 -m venv da_forge_env
source da_forge_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. API Key Configuration

**Get OpenRouter API Key (Recommended):**

1. Visit https://openrouter.ai/
2. Sign up for an account
3. Navigate to "Keys" section
4. Create a new API key
5. Copy the key and set it as environment variable

**Get Anthropic API Key (Alternative):**

1. Visit https://console.anthropic.com/
2. Sign up for an account
3. Navigate to "API Keys" section
4. Create a new API key
5. Copy the key and set it as environment variable

**Setting Environment Variables:**

**Windows (Command Prompt):**

```cmd
set OPENROUTER_API_KEY=your_key_here
```

**Windows (PowerShell):**

```powershell
$env:OPENROUTER_API_KEY="your_key_here"
```

**macOS/Linux:**

```bash
export OPENROUTER_API_KEY="your_key_here"
```

**Permanent Setup (Optional):**
Create a `.env` file in the project root:

```
OPENROUTER_API_KEY=your_key_here
# OR
ANTHROPIC_API_KEY=your_key_here

# Optional n8n configuration
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=your_n8n_key
MOCK_DEPLOYMENT=true
```

### 3. Running the Application

**Start the Streamlit UI:**

```bash
streamlit run ui/app.py
```

**Alternative: Run with specific configuration:**

```bash
streamlit run ui/app.py --server.port 8501 --server.address localhost
```

The application will open automatically in your default web browser at `http://localhost:8501`

### 4. Using the System

**Basic Usage:**

1. **Input**: Enter a workflow description like "Create a webhook that processes orders and sends email confirmations"
2. **Configure**: Select your LLM provider in the sidebar
3. **Generate**: Click the "Generate & Process Workflow" button
4. **Download**: Download the generated n8n workflow JSON
5. **Deploy**: Import the JSON into your n8n instance

**Example Workflow Descriptions:**

- "Create a webhook that receives JSON data, validates it, and sends Slack notifications"
- "Monitor RSS feeds every hour and save new items to Google Sheets"
- "Process CSV uploads, validate data, and generate summary reports"
- "Create an order processing system with inventory checks and email confirmations"

## Programmatic Usage

### Basic Example

```python
import asyncio
from agents.team import DAForgeTeam

async def generate_workflow():
    # Initialize the team
    team = DAForgeTeam(llm_provider="openrouter")

    # Generate workflow
    result = await team.execute_workflow_generation(
        "Create a webhook that processes JSON and sends notifications"
    )

    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Workflow ID: {result['workflow_id']}")
        print(f"Nodes: {len(result['workflow_json']['nodes'])}")

# Run the example
asyncio.run(generate_workflow())
```

### Running Examples

```bash
# Interactive mode
python examples/run_da_forge.py interactive

# Run multiple examples
python examples/run_da_forge.py examples

# Run single example
python examples/run_da_forge.py single
```

## Configuration Options

### LLM Provider Selection

**OpenRouter (Recommended):**

- Access to multiple models including Claude-3.5-Sonnet
- Competitive pricing
- High availability

**Anthropic Direct:**

- Direct Claude API access
- Lower latency
- Requires Anthropic account

### Deployment Modes

**Mock Mode (Default):**

- Generates workflow JSON only
- No actual n8n deployment
- Perfect for demos and testing

**Real Mode:**

- Deploys to actual n8n instance
- Returns live workflow URLs
- Requires n8n API configuration

### Environment Variables Reference

| Variable             | Required | Description        | Example                 |
| -------------------- | -------- | ------------------ | ----------------------- |
| `OPENROUTER_API_KEY` | Yes\*    | OpenRouter API key | `sk-or-v1-...`          |
| `ANTHROPIC_API_KEY`  | Yes\*    | Anthropic API key  | `sk-ant-...`            |
| `N8N_BASE_URL`       | No       | n8n instance URL   | `http://localhost:5678` |
| `N8N_API_KEY`        | No       | n8n API key        | `n8n_api_...`           |
| `MOCK_DEPLOYMENT`    | No       | Enable mock mode   | `true` or `false`       |

\*One of the LLM provider keys is required

## Troubleshooting

### Common Issues

**1. Import Errors**

```bash
# Make sure you're in the project directory
cd da_forge_adk

# Install dependencies
pip install -r requirements.txt
```

**2. API Key Issues**

```bash
# Check if environment variable is set
echo $OPENROUTER_API_KEY

# Re-set the variable
export OPENROUTER_API_KEY="your_key_here"
```

**3. Streamlit Not Found**

```bash
# Install streamlit specifically
pip install streamlit

# Or reinstall all dependencies
pip install -r requirements.txt
```

**4. Port Already in Use**

```bash
# Use different port
streamlit run ui/app.py --server.port 8502
```

### Debug Mode

Enable debug information in the UI by checking "Show Debug Information" in the interface.

### Logs

Check the application logs for detailed error information:

- Console output when running `streamlit run ui/app.py`
- Error messages in the UI interface
- Debug information panel in the web interface

## Development

### Project Structure Details

**agents/**: Multi-agent system following ADK patterns

- `input_agent.py`: Validates and processes user input
- `planner_agent.py`: Uses LLM to plan workflow structure
- `team.py`: Coordinates all agents and manages execution

**tools/**: Specialized workflow tools

- `workflow_generator.py`: Converts plans to n8n JSON
- `deploy_tool.py`: Handles n8n deployment

**memory/**: Execution state management

- `short_term.py`: Stores context between agent interactions

**ui/**: User interface

- `app.py`: Main Streamlit application

**examples/**: Usage examples and testing

- `run_da_forge.py`: Programmatic usage examples

### Adding New Features

1. **New Node Types**: Add templates in `workflow_generator.py`
2. **New Agents**: Create in `agents/` following ADK patterns
3. **New Tools**: Add to `tools/` with proper Tool interface
4. **UI Enhancements**: Modify `ui/app.py`

### Testing

```bash
# Test core functionality
python examples/run_da_forge.py examples

# Interactive testing
python examples/run_da_forge.py interactive

# UI testing
streamlit run ui/app.py
```

## Advanced Configuration

### Custom LLM Models

```python
# Use specific OpenRouter models
team = DAForgeTeam(
    llm_provider="openrouter",
    model="anthropic/claude-3.5-sonnet"
)
```

### Progress Callbacks

```python
def progress_handler(stage: str, message: str):
    print(f"[{stage}] {message}")

team.set_progress_callback(progress_handler)
```

### Memory Management

```python
# Get execution summary
memory_summary = await team.get_memory_summary()

# Clear memory
team.clear_memory()
```

## Requirements

### System Requirements

- Python 3.9+
- 2GB RAM minimum
- Internet connection for LLM APIs

### Python Dependencies

See `requirements.txt` for complete list. Key dependencies:

- `streamlit` - Web interface
- `aiohttp` - Async HTTP requests
- `pydantic` - Data validation
- `python-dotenv` - Environment variable management

## Support

### Getting Help

1. Check this README for setup instructions
2. Review error messages in the UI
3. Check console output for detailed logs
4. Verify API keys are set correctly
5. Ensure internet connection for LLM access

### Known Limitations

- Requires active internet connection
- LLM API costs apply for usage
- Mock mode doesn't create actual n8n workflows
- Complex workflows may require manual refinement

## License

Built for Agent Development Kit Hackathon with Google Cloud.

## Acknowledgments

- Google Cloud Agent Development Kit team
- n8n.io for the workflow platform
- Anthropic for Claude API
- OpenRouter for LLM access
- Streamlit for the UI framework
