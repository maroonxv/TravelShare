"""
Template repository interface
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app_travel.domain.aggregate.trip_template import TripTemplate
from app_travel.domain.value_objects.template_value_objects import TemplateId


class ITemplateRepository(ABC):
    """Template repository interface"""
    
    @abstractmethod
    def save(self, template: TripTemplate) -> None:
        """Save template (create or update)
        
        Args:
            template: Template aggregate root
        """
        pass
    
    @abstractmethod
    def find_by_id(self, template_id: TemplateId) -> Optional[TripTemplate]:
        """Find template by ID
        
        Args:
            template_id: Template ID
            
        Returns:
            Template instance or None if not found
        """
        pass
    
    @abstractmethod
    def find_all(
        self,
        limit: int = 20,
        offset: int = 0,
        keyword: Optional[str] = None,
        tag: Optional[str] = None
    ) -> List[TripTemplate]:
        """Find all templates with optional filters
        
        Args:
            limit: Page size
            offset: Offset
            keyword: Optional keyword search
            tag: Optional tag filter
            
        Returns:
            List of templates
        """
        pass
    
    @abstractmethod
    def count_all(
        self,
        keyword: Optional[str] = None,
        tag: Optional[str] = None
    ) -> int:
        """Count templates with optional filters
        
        Args:
            keyword: Optional keyword search
            tag: Optional tag filter
            
        Returns:
            Count of templates
        """
        pass
    
    @abstractmethod
    def delete(self, template_id: TemplateId) -> None:
        """Delete template
        
        Args:
            template_id: Template ID
        """
        pass
    
    @abstractmethod
    def exists(self, template_id: TemplateId) -> bool:
        """Check if template exists
        
        Args:
            template_id: Template ID
            
        Returns:
            True if exists
        """
        pass
