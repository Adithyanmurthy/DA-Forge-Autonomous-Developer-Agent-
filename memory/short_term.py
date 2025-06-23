from typing import Dict, Any, Optional
import json
from datetime import datetime
# Mock ADK Classes
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime

class Memory(ABC):
    def __init__(self, name: str):
        self.name = name
        self.created_at = datetime.now().isoformat()
    
    @abstractmethod
    def store(self, key: str, data: Any) -> bool:
        pass
    
    @abstractmethod
    def retrieve(self, key: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        pass

class ShortTermMemory(Memory):
    def __init__(self):
        super().__init__(name="short_term_memory")
        self.storage: Dict[str, Any] = {}
        self.timestamps: Dict[str, str] = {}
        self.max_items = 100
    
    def store(self, key: str, data: Any) -> bool:
        """Store data with key"""
        try:
            # Clean old entries if we're at capacity
            if len(self.storage) >= self.max_items:
                self._cleanup_oldest()
            
            self.storage[key] = data
            self.timestamps[key] = datetime.now().isoformat()
            return True
            
        except Exception as e:
            print(f"Error storing data: {e}")
            return False
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data by key"""
        return self.storage.get(key)
    
    def update(self, key: str, data: Any) -> bool:
        """Update existing data"""
        if key in self.storage:
            self.storage[key] = data
            self.timestamps[key] = datetime.now().isoformat()
            return True
        return False
    
    def delete(self, key: str) -> bool:
        """Delete data by key"""
        if key in self.storage:
            del self.storage[key]
            if key in self.timestamps:
                del self.timestamps[key]
            return True
        return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return key in self.storage
    
    def get_all_keys(self) -> list:
        """Get all stored keys"""
        return list(self.storage.keys())
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "total_items": len(self.storage),
            "max_capacity": self.max_items,
            "keys": list(self.storage.keys()),
            "oldest_entry": min(self.timestamps.values()) if self.timestamps else None,
            "newest_entry": max(self.timestamps.values()) if self.timestamps else None
        }
    
    def clear_all(self) -> bool:
        """Clear all stored data"""
        try:
            self.storage.clear()
            self.timestamps.clear()
            return True
        except Exception as e:
            print(f"Error clearing memory: {e}")
            return False
    
    def _cleanup_oldest(self):
        """Remove oldest entries to make space"""
        if not self.timestamps:
            return
        
        # Sort by timestamp and remove oldest 10%
        sorted_items = sorted(self.timestamps.items(), key=lambda x: x[1])
        items_to_remove = max(1, len(sorted_items) // 10)
        
        for i in range(items_to_remove):
            key_to_remove = sorted_items[i][0]
            self.delete(key_to_remove)
    
    def export_memory(self) -> Dict[str, Any]:
        """Export all memory data"""
        return {
            "storage": self.storage,
            "timestamps": self.timestamps,
            "exported_at": datetime.now().isoformat()
        }
    
    def import_memory(self, memory_data: Dict[str, Any]) -> bool:
        """Import memory data"""
        try:
            if "storage" in memory_data:
                self.storage = memory_data["storage"]
            if "timestamps" in memory_data:
                self.timestamps = memory_data["timestamps"]
            return True
        except Exception as e:
            print(f"Error importing memory: {e}")
            return False