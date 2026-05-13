from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from beanie import Link


class BaseModelJsonSerializable(BaseModel):
    """
    Base class for all DTOs that provides custom JSON serialization.
    
    This class handles:
    - Pydantic models (using model_dump())
    - Beanie Link objects (extracting IDs)
    - Datetime objects (converting to ISO format)
    - Lists and nested structures
    - Enum values
    """
    
    def to_json(self) -> Dict[str, Any]:
        """
        Convert the DTO to a JSON-serializable dictionary.
        
        Returns:
            Dict[str, Any]: A dictionary that can be safely serialized to JSON
        """
        return self._serialize_object(self)
    
    def _serialize_object(self, obj: Any) -> Any:
        """
        Recursively serialize an object to make it JSON-compatible.
        
        Args:
            obj: The object to serialize
            
        Returns:
            The serialized object
        """
        if obj is None:
            return None
        
        # Handle Pydantic models
        if isinstance(obj, BaseModel):
            return self._serialize_pydantic_model(obj)
        
        # Handle Beanie Link objects
        if self._is_link_object(obj):
            return self._serialize_link(obj)
        
        # Handle datetime objects
        if isinstance(obj, datetime):
            return obj.isoformat()
        
        # Handle lists
        if isinstance(obj, list):
            return [self._serialize_object(item) for item in obj]
        
        # Handle dictionaries
        if isinstance(obj, dict):
            return {key: self._serialize_object(value) for key, value in obj.items()}
        
        # Handle enums (convert to their values)
        if hasattr(obj, 'value'):
            return obj.value
        
        # Handle primitive types (str, int, float, bool)
        if isinstance(obj, (str, int, float, bool)):
            return obj
        
        # For any other types, try to convert to string
        try:
            return str(obj)
        except Exception:
            return None
    
    def _serialize_pydantic_model(self, model: BaseModel) -> Dict[str, Any]:
        """
        Serialize a Pydantic model by converting it to a dict and then serializing each field.
        
        Args:
            model: The Pydantic model to serialize
            
        Returns:
            Dict[str, Any]: The serialized model
        """
        try:
            # Convert Pydantic model to dict
            model_dict = model.model_dump()
            # Recursively serialize the dict
            return self._serialize_object(model_dict)
        except Exception:
            # Fallback: try to serialize as string
            return str(model)
    
    def _is_link_object(self, obj: Any) -> bool:
        """
        Check if an object is a Beanie Link object.
        
        Args:
            obj: The object to check
            
        Returns:
            bool: True if it's a Link object, False otherwise
        """
        # Check if it has the Link class name or if it's imported from beanie
        return (hasattr(obj, '__class__') and 
                'Link' in str(obj.__class__) and 
                hasattr(obj, 'id'))
    
    def _serialize_link(self, link_obj: Any) -> Optional[str]:
        """
        Serialize a Beanie Link object by extracting its ID.
        
        Args:
            link_obj: The Link object to serialize
            
        Returns:
            Optional[str]: The ID as a string, or None if serialization fails
        """
        try:
            if hasattr(link_obj, 'id') and link_obj.id is not None:
                return str(link_obj.id)
            return None
        except Exception:
            return None
    
    def _serialize_field(self, field_value: Any) -> Any:
        """
        Serialize a single field value.
        
        Args:
            field_value: The field value to serialize
            
        Returns:
            The serialized field value
        """
        return self._serialize_object(field_value)
