"""
Template DAO interface
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app_travel.infrastructure.database.persistent_model.template_po import TripTemplatePO


class ITemplateDAO(ABC):
    """Template data access object interface"""
    
    @abstractmethod
    def create(self, template_po: TripTemplatePO) -> TripTemplatePO:
        """Create a new template"""
        pass
    
    @abstractmethod
    def get_by_id(self, template_id: str) -> Optional[TripTemplatePO]:
        """Get template by ID"""
        pass
    
    @abstractmethod
    def list_all(
        self,
        limit: int = 20,
        offset: int = 0,
        keyword: Optional[str] = None,
        tag: Optional[str] = None
    ) -> List[TripTemplatePO]:
        """List templates with optional filters"""
        pass
    
    @abstractmethod
    def count_all(
        self,
        keyword: Optional[str] = None,
        tag: Optional[str] = None
    ) -> int:
        """Count templates with optional filters"""
        pass
    
    @abstractmethod
    def delete(self, template_id: str) -> bool:
        """Delete template by ID"""
        pass
