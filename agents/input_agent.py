from typing import Dict, Any
import json
# Mock ADK Classes
from typing import Dict, Any, List, Optional
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

class InputAgent(LlmAgent):
    def __init__(self, name: str = "input_agent"):
        super().__init__(name=name)
        self.description = "Processes and validates user input for workflow generation"
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """Process and validate user input"""
        try:
            # Clean and validate input
            cleaned_input = user_input.strip()
            if not cleaned_input:
                raise ValueError("Input cannot be empty")
            
            # Extract key components
            processed_data = {
                "original_input": user_input,
                "cleaned_input": cleaned_input,
                "input_length": len(cleaned_input),
                "status": "valid",
                "timestamp": self._get_timestamp()
            }
            
            return processed_data
            
        except Exception as e:
            return {
                "original_input": user_input,
                "status": "error",
                "error": str(e),
                "timestamp": self._get_timestamp()
            }
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()
    
    async def run(self, message: Message) -> Message:
        """Main run method for ADK compatibility"""
        user_input = message.content
        result = self.process_input(user_input)
        
        return Message(
            content=json.dumps(result),
            sender=self.name,
            metadata={"processed": True}
        )