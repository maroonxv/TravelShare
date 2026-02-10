"""
费用相关持久化对象 (PO - Persistent Object)

用于 SQLAlchemy ORM 映射，与数据库表对应。
包含 ExpensePO, ExpenseSharePO, SettlementTransferPO。
"""
from datetime import datetime
from decimal import Decimal
from typing import List

from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship
from shared.database.core import Base

from app_travel.domain.entity.expense import Expense
from app_travel.domain.value_objects.expense_value_objects import (
    SplitMode, ExpenseCategory, ExpenseShare, SettlementTransfer
)


class ExpenseSharePO(Base):
    """费用分摊明细持久化对象"""
    
    __tablename__ = 'expense_shares'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    expense_id = Column(String(36), ForeignKey('expenses.id'), nullable=False, index=True)
    user_id = Column(String(36), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    percentage = Column(Numeric(5, 2), nullable=True)
    
    # 关联
    expense = relationship('ExpensePO', back_populates='shares')
    
    def to_domain(self) -> ExpenseShare:
        """转换为领域值对象"""
        return ExpenseShare(
            user_id=self.user_id,
            amount=self.amount,
            percentage=self.percentage
        )
    
    @classmethod
    def from_domain(cls, share: ExpenseShare, expense_id: str) -> 'ExpenseSharePO':
        """从领域值对象创建"""
        return cls(
            expense_id=expense_id,
            user_id=share.user_id,
            amount=share.amount,
            percentage=share.percentage
        )


class ExpensePO(Base):
    """费用持久化对象"""
    
    __tablename__ = 'expenses'
    
    id = Column(String(36), primary_key=True)
    trip_id = Column(String(36), nullable=False, index=True)
    description = Column(String(200), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default='CNY')
    category = Column(String(30), nullable=False)
    payer_id = Column(String(36), nullable=False)
    split_mode = Column(String(20), nullable=False)
    created_by = Column(String(36), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 关联
    shares = relationship('ExpenseSharePO', back_populates='expense', cascade='all, delete-orphan')
    
    def to_domain(self) -> Expense:
        """转换为领域实体"""
        domain_shares = [share.to_domain() for share in self.shares]
        
        return Expense(
            id=self.id,
            trip_id=self.trip_id,
            description=self.description,
            amount=self.amount,
            currency=self.currency,
            category=ExpenseCategory.from_string(self.category),
            payer_id=self.payer_id,
            split_mode=SplitMode.from_string(self.split_mode),
            shares=domain_shares,
            created_by=self.created_by,
            created_at=self.created_at
        )
    
    @classmethod
    def from_domain(cls, expense: Expense) -> 'ExpensePO':
        """从领域实体创建"""
        po = cls(
            id=expense.id,
            trip_id=expense.trip_id,
            description=expense.description,
            amount=expense.amount,
            currency=expense.currency,
            category=expense.category.value,
            payer_id=expense.payer_id,
            split_mode=expense.split_mode.value,
            created_by=expense.created_by,
            created_at=expense.created_at
        )
        
        # 分摊明细
        po.shares = [ExpenseSharePO.from_domain(share, expense.id) for share in expense.shares]
        
        return po


class SettlementTransferPO(Base):
    """结算转账持久化对象"""
    
    __tablename__ = 'settlement_transfers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    trip_id = Column(String(36), nullable=False, index=True)
    from_user_id = Column(String(36), nullable=False)
    to_user_id = Column(String(36), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default='CNY')
    is_settled = Column(Boolean, nullable=False, default=False)
    settled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def to_domain(self) -> SettlementTransfer:
        """转换为领域值对象"""
        return SettlementTransfer(
            from_user_id=self.from_user_id,
            to_user_id=self.to_user_id,
            amount=self.amount,
            currency=self.currency,
            is_settled=self.is_settled
        )
    
    @classmethod
    def from_domain(cls, transfer: SettlementTransfer, trip_id: str) -> 'SettlementTransferPO':
        """从领域值对象创建"""
        return cls(
            trip_id=trip_id,
            from_user_id=transfer.from_user_id,
            to_user_id=transfer.to_user_id,
            amount=transfer.amount,
            currency=transfer.currency,
            is_settled=transfer.is_settled,
            settled_at=datetime.utcnow() if transfer.is_settled else None
        )
