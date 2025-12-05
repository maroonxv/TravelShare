from typing import List, Optional
import json
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, desc, and_, exists, func

from app_social.infrastructure.database.dao_interface.i_post_dao import IPostDao
from app_social.infrastructure.database.persistent_model.post_po import PostPO

class SqlAlchemyPostDao(IPostDao):
    """基于 SQLAlchemy 的帖子 DAO 实现"""

    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, post_id: str) -> Optional[PostPO]:
        stmt = select(PostPO).where(PostPO.id == post_id)
        return self.session.execute(stmt).scalars().first()

    def find_by_author(
        self,
        author_id: str,
        include_deleted: bool = False,
        limit: int = 20,
        offset: int = 0
    ) -> List[PostPO]:
        stmt = select(PostPO).where(PostPO.author_id == author_id)
        
        if not include_deleted:
            stmt = stmt.where(PostPO.is_deleted == False)
            
        stmt = stmt.order_by(desc(PostPO.created_at)).limit(limit).offset(offset)
        return list(self.session.execute(stmt).scalars().all())

    def find_by_trip(self, trip_id: str) -> Optional[PostPO]:
        stmt = (
            select(PostPO)
            .where(
                and_(
                    PostPO.trip_id == trip_id,
                    PostPO.is_deleted == False
                )
            )
        )
        return self.session.execute(stmt).scalars().first()

    def find_public_feed(
        self,
        limit: int = 20,
        offset: int = 0,
        tags: Optional[List[str]] = None
    ) -> List[PostPO]:
        stmt = (
            select(PostPO)
            .where(
                and_(
                    PostPO.visibility == 'public',
                    PostPO.is_deleted == False
                )
            )
        )
        
        if tags:
            # 简单的标签过滤：任一标签匹配即可
            # tags_json LIKE '%"tag"%'
            # 组合 OR 条件
            from sqlalchemy import or_
            conditions = [PostPO.tags_json.like(f'%"{tag}"%') for tag in tags]
            stmt = stmt.where(or_(*conditions))
            
        stmt = stmt.order_by(desc(PostPO.created_at)).limit(limit).offset(offset)
        return list(self.session.execute(stmt).scalars().all())

    def find_by_visibility(
        self,
        visibility: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[PostPO]:
        stmt = (
            select(PostPO)
            .where(
                and_(
                    PostPO.visibility == visibility,
                    PostPO.is_deleted == False
                )
            )
            .order_by(desc(PostPO.created_at))
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.execute(stmt).scalars().all())

    def add(self, post_po: PostPO) -> None:
        self.session.add(post_po)
        self.session.flush()

    def update(self, post_po: PostPO) -> None:
        self.session.merge(post_po)
        self.session.flush()

    def delete(self, post_id: str) -> None:
        # 物理删除
        stmt = delete(PostPO).where(PostPO.id == post_id)
        self.session.execute(stmt)
        self.session.flush()

    def exists(self, post_id: str) -> bool:
        stmt = select(exists().where(PostPO.id == post_id))
        return self.session.execute(stmt).scalar()

    def count_by_author(self, author_id: str, include_deleted: bool = False) -> int:
        stmt = select(func.count()).select_from(PostPO).where(PostPO.author_id == author_id)
        if not include_deleted:
            stmt = stmt.where(PostPO.is_deleted == False)
        return self.session.execute(stmt).scalar()
