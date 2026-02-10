"""
费用分摊相关值对象

包含费用分摊、结算相关的所有值对象。
"""
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional


class SplitMode(Enum):
    """费用分摊方式枚举"""
    EQUAL = "equal"           # 均摊
    EXACT = "exact"           # 精确金额
    PERCENTAGE = "percentage" # 按百分比
    
    @classmethod
    def from_string(cls, mode_str: str) -> 'SplitMode':
        mode_str = mode_str.lower()
        for mode in cls:
            if mode.value == mode_str:
                return mode
        raise ValueError(f"Unknown split mode: {mode_str}")


class ExpenseCategory(Enum):
    """费用分类枚举"""
    TRANSPORT = "transport"
    DINING = "dining"
    ACCOMMODATION = "accommodation"
    SIGHTSEEING = "sightseeing"
    SHOPPING = "shopping"
    OTHER = "other"
    
    @classmethod
    def from_string(cls, category_str: str) -> 'ExpenseCategory':
        category_str = category_str.lower()
        for category in cls:
            if category.value == category_str:
                return category
        raise ValueError(f"Unknown expense category: {category_str}")


@dataclass(frozen=True)
class ExpenseShare:
    """费用分摊明细值对象
    
    表示某个用户在一笔费用中应分摊的金额。
    """
    user_id: str
    amount: Decimal       # 该用户应分摊的金额
    percentage: Optional[Decimal] = None  # 百分比（percentage 模式下使用）
    
    def __post_init__(self):
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))
        if self.amount < 0:
            raise ValueError("Share amount cannot be negative")
        if self.percentage is not None:
            if not isinstance(self.percentage, Decimal):
                object.__setattr__(self, 'percentage', Decimal(str(self.percentage)))
            if self.percentage < 0 or self.percentage > 100:
                raise ValueError("Percentage must be between 0 and 100")


@dataclass(frozen=True)
class SettlementTransfer:
    """结算转账值对象
    
    表示一笔结算转账：from_user_id 应付给 to_user_id 指定金额。
    """
    from_user_id: str    # 付款方
    to_user_id: str      # 收款方
    amount: Decimal      # 金额
    currency: str
    is_settled: bool = False     # 是否已结清
    
    def __post_init__(self):
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))
        if self.amount <= 0:
            raise ValueError("Transfer amount must be positive")
        if not self.currency:
            raise ValueError("Currency cannot be empty")
