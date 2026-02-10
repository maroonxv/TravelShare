"""
Template repository implementation

Implements ITemplateRepository interface.
Handles persistence of TripTemplate aggregate root.
"""
from typing import List, Optional

from app_travel.domain.demand_interface.i_template_repository import ITemplateRepository
from app_travel.domain.aggregate.trip_template import TripTemplate
from app_travel.domain.value_objects.template_value_objects import TemplateId
from app_travel.infrastructure.database.dao_interface.i_template_dao import ITemplateDAO
from app_travel.infrastructure.database.persistent_model.template_po import TripTemplatePO


class TemplateRepositoryImpl(ITemplateRepository):
    """Template repository implementation"""
    
    def __init__(self, template_dao: ITemplateDAO):
        """Initialize repository
        
        Args:
            template_dao: Template data access object
        """
        self._template_dao = template_dao
    
    def save(self, template: TripTemplate) -> None:
        """Save template (create or update)
        
        Args:
            template: Template aggregate root
        """
        existing_po = self._template_dao.get_by_id(template.id.value)
        
        if existing_po:
            # Update existing template (though templates are typically immutable)
            # For now, we'll just replace it
            self._template_dao.delete(template.id.value)
        
        # Create new template PO
        template_po = TripTemplatePO.from_domain(template)
        self._template_dao.create(template_po)
    
    def find_by_id(self, template_id: TemplateId) -> Optional[TripTemplate]:
        """Find template by ID
        
        Args:
            template_id: Template ID
            
        Returns:
            Template instance or None if not found
        """
        template_po = self._template_dao.get_by_id(template_id.value)
        if template_po:
            return template_po.to_domain()
        return None
    
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
        template_pos = self._template_dao.list_all(
            limit=limit,
            offset=offset,
            keyword=keyword,
            tag=tag
        )
        return [po.to_domain() for po in template_pos]
    
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
        return self._template_dao.count_all(keyword=keyword, tag=tag)
    
    def delete(self, template_id: TemplateId) -> None:
        """Delete template
        
        Args:
            template_id: Template ID
        """
        self._template_dao.delete(template_id.value)
    
    def exists(self, template_id: TemplateId) -> bool:
        """Check if template exists
        
        Args:
            template_id: Template ID
            
        Returns:
            True if exists
        """
        template_po = self._template_dao.get_by_id(template_id.value)
        return template_po is not None
