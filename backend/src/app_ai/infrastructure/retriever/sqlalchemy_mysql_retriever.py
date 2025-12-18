from typing import List
import string
import jieba
from sqlalchemy import or_, literal, func
from sqlalchemy.orm import Session
from app_ai.domain.demand_interface.i_retriever import IRetriever
from app_ai.domain.value_objects.retrieved_document import RetrievedDocument
from app_travel.infrastructure.database.persistent_model.trip_po import ActivityPO, TripPO, TripDayPO
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
        query_clean = query_clean.strip()
        if any('\u4e00' <= c <= '\u9fff' for c in query_clean):
            seg_list = jieba.cut_for_search(query_clean)
            keywords = [query_clean]
            seen = {query_clean}
            for w in seg_list:
                w = w.strip()
                if len(w) < 2 or w in seen:
                    continue
                seen.add(w)
                keywords.append(w)
        else:
            keywords = [w for w in query_clean.split() if len(w) >= 2]

        if not keywords:
            keywords = [query.strip()]

        # Activity Filters
        activity_filters = []
        for kw in keywords:
            activity_filters.append(ActivityPO.name.like(f'%{kw}%'))
            activity_filters.append(ActivityPO.location_name.like(f'%{kw}%'))
            activity_filters.append(ActivityPO.activity_type.like(f'%{kw}%'))
            
        activities = self.session.query(ActivityPO, TripPO.id.label('trip_id')).join(
            TripDayPO, ActivityPO.trip_day_id == TripDayPO.id
        ).join(
            TripPO, TripDayPO.trip_id == TripPO.id
        ).filter(
            or_(*activity_filters),
            TripPO.visibility == 'public' # Only public trips
        ).limit(limit).all()
        
        activity_docs = []
        for act, trip_id in activities:
            content = f"Name: {act.name}\nType: {act.activity_type}\nLocation: {act.location_name} ({act.location_address or ''})\nNotes: {act.notes or 'None'}"
            activity_docs.append(RetrievedDocument(
                content=content,
                source_type="activity",
                reference_id=act.id,
                title=act.name,
                score=1.0, # Simple match, no scoring yet
                metadata={'trip_id': trip_id}
            ))
            
        # Trip Filters
        trip_filters = []
        for kw in keywords:
            trip_filters.append(TripPO.name.like(f'%{kw}%'))
            trip_filters.append(TripPO.description.like(f'%{kw}%'))
            
        trips = self.session.query(TripPO).filter(
            or_(*trip_filters),
            TripPO.visibility == 'public'
        ).limit(limit).all()
        
        trip_docs = []
        for trip in trips:
            content = f"Trip: {trip.name}\nDescription: {trip.description}\nDays: {(trip.end_date - trip.start_date).days + 1}"
            trip_docs.append(RetrievedDocument(
                content=content,
                source_type="trip",
                reference_id=trip.id,
                title=trip.name,
                score=1.0
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
        
        post_docs = []
        for post in posts:
            # Truncate text to avoid context window overflow
            text_preview = post.text[:500] + "..." if len(post.text) > 500 else post.text
            content = f"Title: {post.title}\nContent: {text_preview}"
            post_docs.append(RetrievedDocument(
                content=content,
                source_type="post",
                reference_id=post.id,
                title=post.title,
                score=1.0
            ))
            
        # Interleave results to ensure diversity in top results (used for attachments)
        documents = []
        max_len = max(len(activity_docs), len(trip_docs), len(post_docs)) if (activity_docs or trip_docs or post_docs) else 0
        
        for i in range(max_len):
            if i < len(activity_docs):
                documents.append(activity_docs[i])
            if i < len(trip_docs):
                documents.append(trip_docs[i])
            if i < len(post_docs):
                documents.append(post_docs[i])

        return documents
