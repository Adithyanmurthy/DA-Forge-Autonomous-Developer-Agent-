"""
Mock Agent Development Kit (ADK) Implementation
This provides the base classes needed for the DA-Forge system
"""

from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime
import json


class Message:
    """Message class for agent communication"""
    
    def __init__(self, content: str, sender: str, metadata: Optional[Dict[str, Any]] = None):
        self.content = content
        self.sender = sender
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
        self.id = f"msg_{hash(content + sender + str(datetime.now()))}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "sender": self.sender,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
    
    def __str__(self) -> str:
        return f"Message(sender={self.sender}, content={self.content[:50]}...)"


class LlmAgent(ABC):
    """Base class for LLM-powered agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.description = ""
        self.created_at = datetime.now().isoformat()
        self.message_history: List[Message] = []
    
    @abstractmethod
    async def run(self, message: Message) -> Message:
        """Main agent execution method"""
        pass
    
    def add_message(self, message: Message):
        """Add message to history"""
        self.message_history.append(message)
    
    def get_history(self) -> List[Message]:
        """Get message history"""
        return self.message_history
    
    def clear_history(self):
        """Clear message history"""
        self.message_history.clear()
    
    def __str__(self) -> str:
        return f"LlmAgent(name={self.name})"


class Tool(ABC):
    """Base class for tools"""
    
    def __init__(self, name: str):
        self.name = name
        self.description = ""
        self.created_at = datetime.now().isoformat()
        self.usage_count = 0
    
    @abstractmethod
    async def run(self, input_data: Any) -> Any:
        """Execute the tool"""
        pass
    
    def increment_usage(self):
        """Increment usage counter"""
        self.usage_count += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tool statistics"""
        return {
            "name": self.name,
            "description": self.description,
            "usage_count": self.usage_count,
            "created_at": self.created_at
        }
    
    def __str__(self) -> str:
        return f"Tool(name={self.name})"


class Memory(ABC):
    """Base class for memory systems"""
    
    def __init__(self, name: str):
        self.name = name
        self.created_at = datetime.now().isoformat()
    
    @abstractmethod
    def store(self, key: str, data: Any) -> bool:
        """Store data"""
        pass
    
    @abstractmethod
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete data"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        pass
    
    def __str__(self) -> str:
        return f"Memory(name={self.name})"


class AgentTeam:
    """Team coordinator for multiple agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.agents: List[LlmAgent] = []
        self.tools: List[Tool] = []
        self.memory: Optional[Memory] = None
        self.created_at = datetime.now().isoformat()
        self.execution_history: List[Dict[str, Any]] = []
    
    def add_agent(self, agent: LlmAgent):
        """Add agent to team"""
        self.agents.append(agent)
    
    def remove_agent(self, agent_name: str) -> bool:
        """Remove agent from team"""
        self.agents = [a for a in self.agents if a.name != agent_name]
        return True
    
    def add_tool(self, tool: Tool):
        """Add tool to team"""
        self.tools.append(tool)
    
    def remove_tool(self, tool_name: str) -> bool:
        """Remove tool from team"""
        self.tools = [t for t in self.tools if t.name != tool_name]
        return True
    
    def set_memory(self, memory: Memory):
        """Set team memory"""
        self.memory = memory
    
    def get_agent(self, name: str) -> Optional[LlmAgent]:
        """Get agent by name"""
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get tool by name"""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None
    
    async def execute_workflow(self, workflow: List[Dict[str, Any]]) -> List[Message]:
        """Execute a workflow of agent/tool calls"""
        results = []
        
        for step in workflow:
            step_type = step.get("type")  # "agent" or "tool"
            name = step.get("name")
            input_data = step.get("input")
            
            if step_type == "agent":
                agent = self.get_agent(name)
                if agent:
                    message = Message(content=json.dumps(input_data), sender="workflow")
                    result = await agent.run(message)
                    results.append(result)
            
            elif step_type == "tool":
                tool = self.get_tool(name)
                if tool:
                    result = await tool.run(input_data)
                    message = Message(content=json.dumps(result), sender=f"tool_{name}")
                    results.append(message)
        
        return results
    
    def get_team_status(self) -> Dict[str, Any]:
        """Get team status"""
        return {
            "name": self.name,
            "agents": [{"name": a.name, "description": a.description} for a in self.agents],
            "tools": [{"name": t.name, "description": t.description} for t in self.tools],
            "memory": self.memory.name if self.memory else None,
            "created_at": self.created_at,
            "execution_count": len(self.execution_history)
        }
    
    def log_execution(self, execution_data: Dict[str, Any]):
        """Log execution for history"""
        execution_data["timestamp"] = datetime.now().isoformat()
        self.execution_history.append(execution_data)
    
    def __str__(self) -> str:
        return f"AgentTeam(name={self.name}, agents={len(self.agents)}, tools={len(self.tools)})"


# Utility functions
def create_message(content: str, sender: str, **kwargs) -> Message:
    """Helper function to create messages"""
    return Message(content=content, sender=sender, metadata=kwargs)


def create_agent_team(name: str) -> AgentTeam:
    """Helper function to create agent teams"""
    return AgentTeam(name=name)


# Export all classes
__all__ = [
    "Message",
    "LlmAgent", 
    "Tool",
    "Memory",
    "AgentTeam",
    "create_message",
    "create_agent_team"
]