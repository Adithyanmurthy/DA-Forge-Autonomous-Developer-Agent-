from typing import Dict, Any
import json
import aiohttp
import asyncio
import os
from datetime import datetime
# Mock ADK Classes
from typing import Dict, Any
from abc import ABC, abstractmethod
from datetime import datetime

class Tool(ABC):
    def __init__(self, name: str):
        self.name = name
        self.description = ""
        self.created_at = datetime.now().isoformat()
    
    @abstractmethod
    async def run(self, input_data: Any) -> Any:
        pass

class DeployTool(Tool):
    def __init__(self):
        super().__init__(name="deploy_tool")
        self.description = "Deploys n8n workflows to n8n instance"
        self.n8n_base_url = os.getenv("N8N_BASE_URL", "http://localhost:5678")
        self.n8n_api_key = os.getenv("N8N_API_KEY", "")
        self.mock_mode = os.getenv("MOCK_DEPLOYMENT", "true").lower() == "true"
    
    async def deploy_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy workflow to n8n instance"""
        try:
            if self.mock_mode or not self.n8n_api_key:
                return await self._mock_deployment(workflow_data)
            
            return await self._real_deployment(workflow_data)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _real_deployment(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy to actual n8n instance"""
        headers = {
            "Content-Type": "application/json",
            "X-N8N-API-KEY": self.n8n_api_key
        }
        
        async with aiohttp.ClientSession() as session:
            # Create workflow
            create_url = f"{self.n8n_base_url}/api/v1/workflows"
            
            async with session.post(
                create_url,
                json=workflow_data,
                headers=headers,
                timeout=30
            ) as response:
                
                if response.status == 201:
                    result = await response.json()
                    workflow_id = result.get("id")
                    
                    # Activate workflow if it has a trigger
                    activation_result = await self._activate_workflow(session, workflow_id, headers)
                    
                    return {
                        "success": True,
                        "workflow_id": workflow_id,
                        "workflow_url": f"{self.n8n_base_url}/workflow/{workflow_id}",
                        "activation_status": activation_result,
                        "n8n_response": result,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"N8N API error: {response.status} - {error_text}",
                        "status_code": response.status,
                        "timestamp": datetime.now().isoformat()
                    }
    
    async def _activate_workflow(self, session: aiohttp.ClientSession, workflow_id: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Activate workflow if it has triggers"""
        try:
            activate_url = f"{self.n8n_base_url}/api/v1/workflows/{workflow_id}/activate"
            
            async with session.post(activate_url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    return {"activated": True, "status": "success"}
                else:
                    error_text = await response.text()
                    return {
                        "activated": False, 
                        "status": "failed",
                        "error": f"{response.status} - {error_text}"
                    }
        except Exception as e:
            return {
                "activated": False,
                "status": "error", 
                "error": str(e)
            }
    
    async def _mock_deployment(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock deployment for testing/demo purposes"""
        # Simulate deployment delay
        await asyncio.sleep(2)
        
        workflow_id = workflow_data.get("id", "mock-workflow-id")
        workflow_name = workflow_data.get("name", "Mock Workflow")
        
        # Mock successful deployment
        return {
            "success": True,
            "workflow_id": workflow_id,
            "workflow_url": f"https://demo-n8n.example.com/workflow/{workflow_id}",
            "workflow_name": workflow_name,
            "mock_deployment": True,
            "activation_status": {
                "activated": True,
                "status": "success"
            },
            "deployment_details": {
                "nodes_deployed": len(workflow_data.get("nodes", [])),
                "connections_created": len(workflow_data.get("connections", {})),
                "deployment_time": "2.1s",
                "status": "active"
            },
            "access_info": {
                "editor_url": f"https://demo-n8n.example.com/workflow/{workflow_id}",
                "execution_url": f"https://demo-n8n.example.com/executions/workflow/{workflow_id}",
                "webhook_url": f"https://demo-n8n.example.com/webhook/{workflow_id}" if self._has_webhook_trigger(workflow_data) else None
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _has_webhook_trigger(self, workflow_data: Dict[str, Any]) -> bool:
        """Check if workflow has webhook trigger"""
        nodes = workflow_data.get("nodes", [])
        for node in nodes:
            if node.get("type") == "n8n-nodes-base.webhook":
                return True
        return False
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of deployed workflow"""
        try:
            if self.mock_mode:
                return {
                    "workflow_id": workflow_id,
                    "status": "active",
                    "last_execution": datetime.now().isoformat(),
                    "execution_count": 5,
                    "mock": True
                }
            
            headers = {
                "X-N8N-API-KEY": self.n8n_api_key
            }
            
            async with aiohttp.ClientSession() as session:
                status_url = f"{self.n8n_base_url}/api/v1/workflows/{workflow_id}"
                
                async with session.get(status_url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "workflow_data": result,
                            "status": "active" if result.get("active") else "inactive"
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Status check failed: {response.status}"
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def run(self, input_data: Any) -> Any:
        """Tool interface method"""
        if isinstance(input_data, dict):
            return await self.deploy_workflow(input_data)
        else:
            return {
                "success": False,
                "error": "Invalid input data for deployment"
            }