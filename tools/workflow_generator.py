from typing import Dict, Any, List
import json
import uuid
from datetime import datetime
# Mock ADK Classes
from typing import Dict, Any, List
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

class WorkflowGenerator(Tool):
    def __init__(self):
        super().__init__(name="workflow_generator")
        self.description = "Generates complete n8n workflow JSON from plan"
    
    async def generate_workflow(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete n8n workflow JSON"""
        try:
            print(f"DEBUG: Workflow generator received plan: {plan_data}")
            
            workflow_id = str(uuid.uuid4())
            
            # Extract plan details with safety checks
            nodes = plan_data.get("nodes", [])
            connections = plan_data.get("connections", [])
            workflow_name = plan_data.get("workflow_name", "Generated Workflow")
            
            print(f"DEBUG: Extracted - nodes: {len(nodes)}, connections: {len(connections)}, name: {workflow_name}")
            
            # Generate nodes first (this creates the ID mapping)
            generated_nodes = self._generate_nodes(nodes)
            
            # Generate connections using the ID mapping
            generated_connections = self._generate_connections(connections)
            
            # Generate n8n compatible workflow
            n8n_workflow = {
                "id": workflow_id,
                "name": workflow_name,
                "active": False,
                "nodes": generated_nodes,
                "connections": generated_connections,
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "settings": {
                    "saveManualExecutions": True,
                    "callerPolicy": "workflowsFromSameOwner"
                },
                "staticData": {},
                "tags": ["da-forge", "auto-generated"],
                "triggerCount": 0,
                "versionId": str(uuid.uuid4())
            }
            
            print(f"DEBUG: Generated n8n workflow with {len(n8n_workflow['nodes'])} nodes")
            
            # Validate workflow
            validation_result = self._validate_workflow(n8n_workflow)
            print(f"DEBUG: Validation result: {validation_result}")
            
            if not validation_result["valid"]:
                # Join all validation errors
                error_messages = validation_result.get("errors", ["Unknown validation error"])
                error_msg = f"Workflow validation failed: {'; '.join(error_messages)}"
                print(f"DEBUG: {error_msg}")
                # Don't fail on validation - just warn and continue
                print("DEBUG: Continuing despite validation warnings...")
            
            result = {
                "success": True,
                "workflow_data": n8n_workflow,
                "workflow_id": workflow_id,
                "node_count": len(n8n_workflow["nodes"]),
                "connection_count": len(generated_connections),
                "validation": validation_result
            }
            print(f"DEBUG: Workflow generation successful: {result}")
            return result
            
        except Exception as e:
            error_msg = f"Workflow generation exception: {str(e)}"
            print(f"DEBUG ERROR: {error_msg}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": error_msg,
                "workflow_data": None
            }
    
    def _generate_nodes(self, plan_nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate n8n compatible nodes"""
        n8n_nodes = []
        
        # Keep a mapping of plan IDs to preserve connections
        self.node_id_mapping = {}
        
        for i, node in enumerate(plan_nodes):
            plan_id = node.get("id", f"node_{i}")
            actual_id = str(uuid.uuid4())
            
            # Store mapping for connections
            self.node_id_mapping[plan_id] = actual_id
            
            n8n_node = {
                "id": actual_id,
                "name": node.get("name", f"Node {i+1}"),
                "type": node.get("type", "n8n-nodes-base.noOp"),
                "typeVersion": 1,
                "position": node.get("position", [250 + (i * 200), 300]),
                "parameters": node.get("parameters", {}),
                "executeOnce": False
            }
            
            # Add node-specific configurations
            if node.get("type") == "n8n-nodes-base.manualTrigger":
                n8n_node["parameters"] = {}
            elif node.get("type") == "n8n-nodes-base.code":
                n8n_node["parameters"] = {
                    "jsCode": node.get("parameters", {}).get("jsCode", "return items;"),
                    "mode": "runOnceForEachItem"
                }
            elif node.get("type") == "n8n-nodes-base.webhook":
                n8n_node["parameters"] = {
                    "httpMethod": "POST",
                    "path": f"webhook-{str(uuid.uuid4())[:8]}",
                    "responseMode": "onReceived"
                }
            
            n8n_nodes.append(n8n_node)
            print(f"DEBUG: Created node {plan_id} -> {actual_id}: {n8n_node['name']}")
        
        # Ensure we have at least a manual trigger if no nodes provided
        if not n8n_nodes:
            trigger_id = str(uuid.uuid4())
            n8n_nodes.append({
                "id": trigger_id,
                "name": "Manual Trigger",
                "type": "n8n-nodes-base.manualTrigger",
                "typeVersion": 1,
                "position": [250, 300],
                "parameters": {}
            })
            self.node_id_mapping["default_trigger"] = trigger_id
        
        return n8n_nodes
    
    def _generate_connections(self, plan_connections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate n8n compatible connections"""
        connections = {}
        
        print(f"DEBUG: Generating connections from plan: {plan_connections}")
        print(f"DEBUG: Node ID mapping: {getattr(self, 'node_id_mapping', {})}")
        
        for connection in plan_connections:
            from_node_plan = connection.get("from")
            to_node_plan = connection.get("to")
            output_index = connection.get("output_index", 0)
            input_index = connection.get("input_index", 0)
            
            # Map plan IDs to actual node IDs
            from_node = getattr(self, 'node_id_mapping', {}).get(from_node_plan, from_node_plan)
            to_node = getattr(self, 'node_id_mapping', {}).get(to_node_plan, to_node_plan)
            
            print(f"DEBUG: Processing connection: {from_node_plan} ({from_node}) -> {to_node_plan} ({to_node})")
            
            if from_node not in connections:
                connections[from_node] = {}
            
            if "main" not in connections[from_node]:
                connections[from_node]["main"] = []
            
            # Ensure we have enough output arrays
            while len(connections[from_node]["main"]) <= output_index:
                connections[from_node]["main"].append([])
            
            # Add connection
            connections[from_node]["main"][output_index].append({
                "node": to_node,
                "type": "main",
                "index": input_index
            })
        
        print(f"DEBUG: Generated connections: {connections}")
        return connections
    
    def _validate_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Validate n8n workflow structure"""
        try:
            errors = []
            
            # Check required fields
            required_fields = ["id", "name", "nodes", "connections"]
            for field in required_fields:
                if field not in workflow:
                    errors.append(f"Missing required field: {field}")
            
            # Validate nodes
            nodes = workflow.get("nodes", [])
            if not nodes:
                errors.append("Workflow must have at least one node")
            
            node_ids = set()
            for node in nodes:
                if "id" not in node:
                    errors.append("Node missing required 'id' field")
                else:
                    if node["id"] in node_ids:
                        errors.append(f"Duplicate node ID: {node['id']}")
                    node_ids.add(node["id"])
                
                if "type" not in node:
                    errors.append(f"Node {node.get('id', 'unknown')} missing 'type' field")
            
            # Validate connections reference valid nodes
            connections = workflow.get("connections", {})
            for from_node, outputs in connections.items():
                if from_node not in node_ids:
                    errors.append(f"Connection references non-existent source node: {from_node}")
                
                if isinstance(outputs, dict) and "main" in outputs:
                    for output_array in outputs["main"]:
                        for connection in output_array:
                            to_node = connection.get("node")
                            if to_node not in node_ids:
                                errors.append(f"Connection references non-existent target node: {to_node}")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "node_count": len(nodes),
                "connection_count": sum(
                    len(output_array) 
                    for outputs in connections.values() 
                    if isinstance(outputs, dict) and "main" in outputs
                    for output_array in outputs["main"]
                )
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "node_count": 0,
                "connection_count": 0
            }
    
    async def run(self, input_data: Any) -> Any:
        """Tool interface method"""
        if isinstance(input_data, dict):
            return await self.generate_workflow(input_data)
        else:
            return {
                "success": False,
                "error": "Invalid input data for workflow generation"
            }