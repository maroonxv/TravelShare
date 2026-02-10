"""
SQLAlchemy implementation of template DAO
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from app_travel.infrastructure.database.dao_interface.i_template_dao import ITemplateDAO
from app_travel.infrastructure.database.persistent_model.template_po import TripTemplatePO


class SQLAlchemyTemplateDAO(ITemplateDAO):
    """SQLAlchemy implementation of template DAO"""
    
    def __init__(self, session: Session):
        self._session = session
    
    def create(self, template_po: TripTemplatePO) -> TripTemplatePO:
        """Create a new template"""
        self._session.add(template_po)
        self._session.flush()
        return template_po
    
    def get_by_id(self, template_id: str) -> Optional[TripTemplatePO]:
        """Get template by ID"""
        return self._session.query(TripTemplatePO).filter(
            TripTemplatePO.id == template_id
        ).first()
    
    def list_all(
        self,
        limit: int = 20,
        offset: int = 0,
        keyword: Optional[str] = None,
        tag: Optional[str] = None
    ) -> List[TripTemplatePO]:
        """List templates with optional filters"""
        query = self._session.query(TripTemplatePO)
        
        # Apply keyword filter
        if keyword:
            search_pattern = f"%{keyword}%"
            query = query.filter(
                or_(
                    TripTemplatePO.name.like(search_pattern),
                    TripTemplatePO.description.like(search_pattern)
                )
            )
        
        # Apply tag filter
        if tag:
            tag_pattern = f'%"{tag}"%'
            query = query.filter(TripTemplatePO.tags_json.like(tag_pattern))
        
        # Order by creation time descending
        query = query.order_by(desc(TripTemplatePO.created_at))
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        return query.all()
    
    def count_all(
        self,
        keyword: Optional[str] = None,
        tag: Optional[str] = None
    ) -> int:
        """Count templates with optional filters"""
        query = self._session.query(TripTemplatePO)
        
        # Apply keyword filter
        if keyword:
            search_pattern = f"%{keyword}%"
            query = query.filter(
                or_(
                    TripTemplatePO.name.like(search_pattern),
                    TripTemplatePO.description.like(search_pattern)
                )
            )
        
        # Apply tag filter
        if tag:
            tag_pattern = f'%"{tag}"%'
            query = query.filter(TripTemplatePO.tags_json.like(tag_pattern))
        
        return query.count()
    
    def delete(self, template_id: str) -> bool:
        """Delete template by ID"""
        template = self.get_by_id(template_id)
        if template:
            self._session.delete(template)
            self._session.flush()
            return True
        return False
