"""
费用 DAO SQLAlchemy 实现

使用 SQLAlchemy 实现费用数据访问。
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app_travel.infrastructure.database.dao_interface.i_expense_dao import IExpenseDAO
from app_travel.infrastructure.database.persistent_model.expense_po import (
    ExpensePO, SettlementTransferPO
)


class SQLAlchemyExpenseDAO(IExpenseDAO):
    """费用 DAO SQLAlchemy 实现"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, expense_po: ExpensePO) -> ExpensePO:
        """创建费用"""
        self.session.add(expense_po)
        self.session.flush()
        return expense_po
    
    def get_by_id(self, expense_id: str) -> Optional[ExpensePO]:
        """根据ID获取费用"""
        return self.session.query(ExpensePO).filter(ExpensePO.id == expense_id).first()
    
    def get_by_trip_id(self, trip_id: str) -> List[ExpensePO]:
        """获取行程的所有费用"""
        return self.session.query(ExpensePO).filter(
            ExpensePO.trip_id == trip_id
        ).order_by(ExpensePO.created_at.desc()).all()
    
    def delete(self, expense_id: str) -> bool:
        """删除费用"""
        expense = self.get_by_id(expense_id)
        if expense:
            self.session.delete(expense)
            self.session.flush()
            return True
        return False
    
    def create_settlement_transfer(self, transfer_po: SettlementTransferPO) -> SettlementTransferPO:
        """创建结算转账记录"""
        self.session.add(transfer_po)
        self.session.flush()
        return transfer_po
    
    def get_settlement_transfers_by_trip_id(self, trip_id: str) -> List[SettlementTransferPO]:
        """获取行程的所有结算转账记录"""
        return self.session.query(SettlementTransferPO).filter(
            SettlementTransferPO.trip_id == trip_id
        ).order_by(SettlementTransferPO.created_at.desc()).all()
    
    def update_settlement_transfer(self, transfer_po: SettlementTransferPO) -> SettlementTransferPO:
        """更新结算转账记录"""
        self.session.merge(transfer_po)
        self.session.flush()
        return transfer_po
