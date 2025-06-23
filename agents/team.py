from typing import Dict, Any, List, Callable
import json
import asyncio
# Mock ADK Classes
from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod
from datetime import datetime
import json

class Message:
    def __init__(self, content: str, sender: str, metadata: Optional[Dict[str, Any]] = None):
        self.content = content
        self.sender = sender
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
        self.id = f"msg_{hash(content + sender + str(datetime.now()))}"

class LlmAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.description = ""
        self.created_at = datetime.now().isoformat()
        self.message_history: List[Message] = []
    
    @abstractmethod
    async def run(self, message: Message) -> Message:
        pass

class AgentTeam:
    def __init__(self, name: str):
        self.name = name
        self.agents: List[LlmAgent] = []
        self.created_at = datetime.now().isoformat()
    
    def add_agent(self, agent: LlmAgent):
        self.agents.append(agent)
from .input_agent import InputAgent
from .planner_agent import PlannerAgent
from tools.workflow_generator import WorkflowGenerator
from tools.deploy_tool import DeployTool
from memory.short_term import ShortTermMemory

class DAForgeTeam(AgentTeam):
    def __init__(self, llm_provider: str = "openrouter"):
        super().__init__(name="da_forge_team")
        
        # Initialize agents
        self.input_agent = InputAgent()
        self.planner_agent = PlannerAgent(llm_provider=llm_provider)
        
        # Initialize tools
        self.workflow_generator = WorkflowGenerator()
        self.deploy_tool = DeployTool()
        
        # Initialize memory
        self.memory = ShortTermMemory()
        
        # Add agents to team
        self.add_agent(self.input_agent)
        self.add_agent(self.planner_agent)
        
        self.progress_callback = None
    
    def set_progress_callback(self, callback: Callable[[str, str], None]):
        """Set callback function for progress updates"""
        self.progress_callback = callback
    
    def _update_progress(self, stage: str, message: str):
        """Update progress if callback is set"""
        if self.progress_callback:
            self.progress_callback(stage, message)
    
    async def execute_workflow_generation(self, user_input: str) -> Dict[str, Any]:
        """Main execution pipeline for workflow generation"""
        try:
            self._update_progress("input", "Processing user input...")
            print(f"DEBUG: Starting workflow generation for: {user_input}")
            
            # Step 1: Process input
            input_message = Message(content=user_input, sender="user")
            processed_input = await self.input_agent.run(input_message)
            input_data = json.loads(processed_input.content)
            print(f"DEBUG: Input processed: {input_data}")
            
            # Store in memory
            self.memory.store("user_input", input_data)
            
            if input_data.get("status") == "error":
                error_msg = f"Input processing failed: {input_data.get('error')}"
                print(f"DEBUG: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "stage": "input"
                }
            
            self._update_progress("planning", "Creating workflow plan...")
            print("DEBUG: Starting planning phase...")
            
            # Step 2: Plan workflow
            plan_message = Message(content=processed_input.content, sender="input_agent")
            plan_result = await self.planner_agent.run(plan_message)
            plan_data = json.loads(plan_result.content)
            print(f"DEBUG: Plan result: {plan_data}")
            
            # Store in memory
            self.memory.store("workflow_plan", plan_data)
            
            if plan_data.get("status") == "error":
                error_msg = f"Planning failed: {plan_data.get('error')}"
                print(f"DEBUG: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "stage": "planning",
                    "fallback_available": "fallback_plan" in plan_data
                }
            
            self._update_progress("generation", "Generating n8n workflow JSON...")
            print("DEBUG: Starting workflow generation...")
            
            # Step 3: Generate workflow JSON
            workflow_json = await self.workflow_generator.generate_workflow(plan_data)
            print(f"DEBUG: Workflow generation result: {workflow_json}")
            
            # Store in memory
            self.memory.store("workflow_json", workflow_json)
            
            if not workflow_json.get("success", False):
                error_msg = f"Workflow generation failed: {workflow_json.get('error')}"
                print(f"DEBUG: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "stage": "generation"
                }
            
            self._update_progress("deployment", "Deploying workflow to n8n...")
            print("DEBUG: Starting deployment...")
            
            # Step 4: Deploy workflow
            deployment_result = await self.deploy_tool.deploy_workflow(
                workflow_json.get("workflow_data", {})
            )
            print(f"DEBUG: Deployment result: {deployment_result}")
            
            # Store in memory
            self.memory.store("deployment_result", deployment_result)
            
            if not deployment_result.get("success", False):
                error_msg = f"Deployment failed: {deployment_result.get('error')}"
                print(f"DEBUG: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "stage": "deployment",
                    "workflow_json": workflow_json.get("workflow_data")
                }
            
            self._update_progress("complete", "Workflow successfully deployed!")
            print("DEBUG: Workflow generation completed successfully!")
            
            # Return success result
            return {
                "success": True,
                "workflow_url": deployment_result.get("workflow_url"),
                "workflow_id": deployment_result.get("workflow_id"),
                "workflow_name": plan_data.get("workflow_name"),
                "workflow_json": workflow_json.get("workflow_data"),
                "execution_summary": {
                    "input_processed": True,
                    "plan_created": True,
                    "workflow_generated": True,
                    "deployment_successful": True,
                    "total_nodes": len(plan_data.get("nodes", [])),
                    "complexity": plan_data.get("estimated_complexity", "unknown")
                }
            }
            
        except Exception as e:
            error_msg = f"Execution pipeline failed: {str(e)}"
            print(f"DEBUG ERROR: {error_msg}")
            import traceback
            traceback.print_exc()
            self._update_progress("error", error_msg)
            return {
                "success": False,
                "error": error_msg,
                "stage": "execution"
            }
    
    async def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of stored memory"""
        return {
            "user_input": self.memory.retrieve("user_input"),
            "workflow_plan": self.memory.retrieve("workflow_plan"),
            "workflow_json": self.memory.retrieve("workflow_json"),
            "deployment_result": self.memory.retrieve("deployment_result")
        }
    
    def clear_memory(self):
        """Clear all stored memory"""
        self.memory.clear_all()