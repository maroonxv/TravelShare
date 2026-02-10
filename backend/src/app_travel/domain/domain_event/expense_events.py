"""
费用相关领域事件定义
"""
from dataclasses import dataclass
from typing import Optional
from shared.domain_event import DomainEvent


@dataclass(frozen=True)
class ExpenseAddedEvent(DomainEvent):
    """费用添加事件
    
    跨上下文事件：通知 app_notification 创建通知
    """
    trip_id: str = ""
    expense_id: str = ""
    payer_id: str = ""
    amount: str = ""  # Decimal as string
    currency: str = ""
    description: str = ""


@dataclass(frozen=True)
class ExpenseDeletedEvent(DomainEvent):
    """费用删除事件"""
    trip_id: str = ""
    expense_id: str = ""
    deleted_by: str = ""


@dataclass(frozen=True)
class SettlementMarkedEvent(DomainEvent):
    """结算标记事件"""
    trip_id: str = ""
    from_user_id: str = ""
    to_user_id: str = ""
    amount: str = ""  # Decimal as string
    currency: str = ""
