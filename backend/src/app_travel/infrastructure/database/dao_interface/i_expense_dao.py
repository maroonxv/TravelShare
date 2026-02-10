"""
费用 DAO 接口

定义费用数据访问对象的接口。
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app_travel.infrastructure.database.persistent_model.expense_po import (
    ExpensePO, SettlementTransferPO
)


class IExpenseDAO(ABC):
    """费用 DAO 接口"""
    
    @abstractmethod
    def create(self, expense_po: ExpensePO) -> ExpensePO:
        """创建费用"""
        pass
    
    @abstractmethod
    def get_by_id(self, expense_id: str) -> Optional[ExpensePO]:
        """根据ID获取费用"""
        pass
    
    @abstractmethod
    def get_by_trip_id(self, trip_id: str) -> List[ExpensePO]:
        """获取行程的所有费用"""
        pass
    
    @abstractmethod
    def delete(self, expense_id: str) -> bool:
        """删除费用"""
        pass
    
    @abstractmethod
    def create_settlement_transfer(self, transfer_po: SettlementTransferPO) -> SettlementTransferPO:
        """创建结算转账记录"""
        pass
    
    @abstractmethod
    def get_settlement_transfers_by_trip_id(self, trip_id: str) -> List[SettlementTransferPO]:
        """获取行程的所有结算转账记录"""
        pass
    
    @abstractmethod
    def update_settlement_transfer(self, transfer_po: SettlementTransferPO) -> SettlementTransferPO:
        """更新结算转账记录"""
        pass
