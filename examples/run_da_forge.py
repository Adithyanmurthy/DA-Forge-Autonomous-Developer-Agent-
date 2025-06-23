#!/usr/bin/env python3
"""
DA-Forge Example Runner
Demonstrates how to use the DA-Forge system programmatically
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.team import DAForgeTeam

def setup_environment():
    """Setup environment variables for demo"""
    # Set demo API keys (replace with your actual keys)
    if not os.getenv("OPENROUTER_API_KEY"):
        print("⚠️  OpenRouter API key not found. Set OPENROUTER_API_KEY environment variable.")
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable.")
    
    # Set n8n configuration for demo
    os.environ.setdefault("N8N_BASE_URL", "http://localhost:5678")
    os.environ.setdefault("MOCK_DEPLOYMENT", "true")
    
    print("🔧 Environment configured for demo mode")

def print_progress(stage: str, message: str):
    """Print progress updates"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    stage_emoji = {
        "input": "📝",
        "planning": "🧠", 
        "generation": "⚙️",
        "deployment": "🚀",
        "complete": "✅",
        "error": "❌"
    }.get(stage, "ℹ️")
    
    print(f"{stage_emoji} [{timestamp}] {message}")

async def run_example_workflow(user_input: str, llm_provider: str = "openrouter"):
    """Run an example workflow generation"""
    print(f"\n🤖 DA-Forge: Autonomous Developer Agent")
    print(f"{'='*50}")
    print(f"Input: {user_input}")
    print(f"LLM Provider: {llm_provider}")
    print(f"{'='*50}\n")
    
    # Initialize team
    team = DAForgeTeam(llm_provider=llm_provider)
    team.set_progress_callback(print_progress)
    
    # Execute workflow generation
    result = await team.execute_workflow_generation(user_input)
    
    # Print results
    print(f"\n{'='*50}")
    if result["success"]:
        print("✅ SUCCESS: Workflow generated and deployed!")
        print(f"🔗 Workflow URL: {result.get('workflow_url', 'N/A')}")
        print(f"🆔 Workflow ID: {result.get('workflow_id', 'N/A')}")
        print(f"📛 Workflow Name: {result.get('workflow_name', 'N/A')}")
        
        if result.get('execution_summary'):
            summary = result['execution_summary']
            print(f"📊 Total Nodes: {summary.get('total_nodes', 0)}")
            print(f"🎯 Complexity: {summary.get('complexity', 'unknown').title()}")
    else:
        print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
        print(f"🔍 Failed at stage: {result.get('stage', 'unknown')}")
    
    print(f"{'='*50}\n")
    
    # Show memory summary
    memory_summary = await team.get_memory_summary()
    print("💾 Memory Summary:")
    for key, value in memory_summary.items():
        if value:
            print(f"  {key}: ✓")
        else:
            print(f"  {key}: ✗")
    
    return result

async def run_multiple_examples():
    """Run multiple example workflows"""
    examples = [
        "Create a webhook that receives JSON data and sends a Slack notification",
        "Monitor an RSS feed and save new items to a Google Sheet",
        "Process uploaded CSV files and generate summary statistics",
        "Create a scheduled workflow that fetches data from an API and stores it in a database"
    ]
    
    print("🚀 Running multiple workflow examples...\n")
    
    results = []
    for i, example in enumerate(examples, 1):
        print(f"\n🔄 Example {i}/{len(examples)}")
        result = await run_example_workflow(example)
        results.append({"input": example, "result": result})
        
        # Short delay between examples
        await asyncio.sleep(1)
    
    # Summary
    print(f"\n📊 SUMMARY")
    print(f"{'='*50}")
    successful = sum(1 for r in results if r["result"]["success"])
    print(f"✅ Successful: {successful}/{len(results)}")
    print(f"❌ Failed: {len(results) - successful}/{len(results)}")
    
    return results

def interactive_mode():
    """Run in interactive mode"""
    print("🎮 Interactive Mode - Enter 'quit' to exit")
    print("="*50)
    
    while True:
        try:
            user_input = input("\n💬 Describe your workflow: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                print("Please enter a workflow description.")
                continue
            
            # Choose LLM provider
            provider = input("🧠 LLM Provider (openrouter/anthropic) [openrouter]: ").strip().lower()
            if provider not in ['openrouter', 'anthropic']:
                provider = 'openrouter'
            
            # Run workflow
            result = asyncio.run(run_example_workflow(user_input, provider))
            
            # Ask if user wants to see JSON
            show_json = input("\n📄 Show generated JSON? (y/n) [n]: ").strip().lower()
            if show_json == 'y' and result.get("workflow_json"):
                print("\n📄 Generated Workflow JSON:")
                print(json.dumps(result["workflow_json"], indent=2))
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    """Main function"""
    setup_environment()
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "interactive":
            interactive_mode()
        elif mode == "examples":
            await run_multiple_examples()
        elif mode == "single":
            user_input = input("Enter workflow description: ")
            await run_example_workflow(user_input)
        else:
            print(f"Unknown mode: {mode}")
            print("Available modes: interactive, examples, single")
    else:
        # Default: run single example
        example_input = "Create a webhook that processes incoming data and sends email notifications"
        await run_example_workflow(example_input)

if __name__ == "__main__":
    print("🤖 DA-Forge Example Runner")
    print("Usage:")
    print("  python run_da_forge.py               # Run single example")
    print("  python run_da_forge.py interactive   # Interactive mode")  
    print("  python run_da_forge.py examples      # Run multiple examples")
    print("  python run_da_forge.py single        # Run single custom example")
    print()
    
    asyncio.run(main())