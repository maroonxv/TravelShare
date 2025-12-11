from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    """领域事件基类"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def event_type(self) -> str:
        """返回事件类型名称"""
        return self.__class__.__name__
