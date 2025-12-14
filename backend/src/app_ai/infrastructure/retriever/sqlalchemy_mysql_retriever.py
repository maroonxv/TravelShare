from typing import List
import string
from sqlalchemy import or_, literal, func
from sqlalchemy.orm import Session
from app_ai.domain.demand_interface.i_retriever import IRetriever
from app_ai.domain.value_objects.retrieved_document import RetrievedDocument
from app_travel.infrastructure.database.persistent_model.trip_po import ActivityPO
from app_social.infrastructure.database.persistent_model.post_po import PostPO

class SqlAlchemyMysqlRetriever(IRetriever):
    def __init__(self, session: Session):
        self.session = session

    def search(self, query: str, limit: int = 5) -> List[RetrievedDocument]:
        documents = []
        
        # Search by keyword matching
        # Clean punctuation and split query into keywords
        # Relaxed length constraint to >= 2 to support short words (especially Chinese)
        query_clean = query.translate(str.maketrans('', '', string.punctuation))
        keywords = [w for w in query_clean.split() if len(w) >= 2]
        if not keywords:
             keywords = [query]

        # Activity Filters
        activity_filters = []
        for kw in keywords:
            activity_filters.append(ActivityPO.name.like(f'%{kw}%'))
            activity_filters.append(ActivityPO.location_name.like(f'%{kw}%'))
            activity_filters.append(ActivityPO.activity_type.like(f'%{kw}%'))
            
        activities = self.session.query(ActivityPO).filter(
            or_(*activity_filters)
        ).limit(limit).all()
        
        for act in activities:
            content = f"Name: {act.name}\nType: {act.activity_type}\nLocation: {act.location_name} ({act.location_address or ''})\nNotes: {act.notes or 'None'}"
            documents.append(RetrievedDocument(
                content=content,
                source_type="activity",
                reference_id=act.id,
                title=act.name,
                score=1.0 # Simple match, no scoring yet
            ))
            
        # Post Filters
        post_filters = []
        for kw in keywords:
            post_filters.append(PostPO.title.like(f'%{kw}%'))
            post_filters.append(PostPO.text.like(f'%{kw}%'))

        posts = self.session.query(PostPO).filter(
             or_(*post_filters),
             PostPO.is_deleted == False,
             PostPO.visibility == 'public'
        ).limit(limit).all()
        
        for post in posts:
            # Truncate text to avoid context window overflow
            text_preview = post.text[:500] + "..." if len(post.text) > 500 else post.text
            content = f"Title: {post.title}\nContent: {text_preview}"
            documents.append(RetrievedDocument(
                content=content,
                source_type="post",
                reference_id=post.id,
                title=post.title,
                score=1.0
            ))
            
        return documents[:limit]
