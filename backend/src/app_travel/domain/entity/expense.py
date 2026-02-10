"""
费用实体

表示旅行中的一笔费用记录，包含分摊逻辑。
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
import uuid

from app_travel.domain.value_objects.expense_value_objects import (
    SplitMode, ExpenseCategory, ExpenseShare
)


@dataclass
class Expense:
    """费用实体
    
    表示旅行中的一笔费用，包含付款人、分摊方式和分摊明细。
    """
    
    id: str                     # UUID
    trip_id: str                # 所属行程
    description: str            # 描述
    amount: Decimal             # 总金额
    currency: str               # 货币 (默认 CNY)
    category: ExpenseCategory   # 分类
    payer_id: str               # 付款人
    split_mode: SplitMode       # 分摊方式
    shares: List[ExpenseShare]  # 分摊明细
    created_by: str             # 创建者
    created_at: datetime
    
    @classmethod
    def create(
        cls,
        trip_id: str,
        description: str,
        amount: Decimal,
        payer_id: str,
        participant_ids: List[str],
        split_mode: SplitMode,
        category: ExpenseCategory = ExpenseCategory.OTHER,
        currency: str = "CNY",
        created_by: Optional[str] = None,
        exact_amounts: Optional[List[Decimal]] = None,
        percentages: Optional[List[Decimal]] = None
    ) -> 'Expense':
        """创建新费用
        
        Args:
            trip_id: 所属行程ID
            description: 费用描述
            amount: 总金额
            payer_id: 付款人ID
            participant_ids: 参与者ID列表
            split_mode: 分摊方式
            category: 费用分类
            currency: 货币
            created_by: 创建者ID（默认为付款人）
            exact_amounts: 精确金额列表（exact模式）
            percentages: 百分比列表（percentage模式）
            
        Returns:
            Expense: 新创建的费用实体
            
        Raises:
            ValueError: 验证失败
        """
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        if not participant_ids:
            raise ValueError("Participant list cannot be empty")
        
        if not description or not description.strip():
            raise ValueError("Description cannot be empty")
        
        # 计算分摊明细
        shares = cls._calculate_shares(
            participant_ids=participant_ids,
            total_amount=amount,
            split_mode=split_mode,
            exact_amounts=exact_amounts,
            percentages=percentages
        )
        
        return cls(
            id=str(uuid.uuid4()),
            trip_id=trip_id,
            description=description.strip(),
            amount=amount,
            currency=currency,
            category=category,
            payer_id=payer_id,
            split_mode=split_mode,
            shares=shares,
            created_by=created_by or payer_id,
            created_at=datetime.utcnow()
        )
    
    @staticmethod
    def _calculate_shares(
        participant_ids: List[str],
        total_amount: Decimal,
        split_mode: SplitMode,
        exact_amounts: Optional[List[Decimal]] = None,
        percentages: Optional[List[Decimal]] = None
    ) -> List[ExpenseShare]:
        """计算分摊明细
        
        Args:
            participant_ids: 参与者ID列表
            total_amount: 总金额
            split_mode: 分摊方式
            exact_amounts: 精确金额列表（exact模式）
            percentages: 百分比列表（percentage模式）
            
        Returns:
            List[ExpenseShare]: 分摊明细列表
            
        Raises:
            ValueError: 验证失败
        """
        shares = []
        
        if split_mode == SplitMode.EQUAL:
            # 均摊模式：总金额除以人数
            n = len(participant_ids)
            share_amount = (total_amount / Decimal(n)).quantize(Decimal('0.01'))
            
            # 处理舍入误差：最后一个人承担差额
            total_assigned = share_amount * (n - 1)
            last_share_amount = total_amount - total_assigned
            
            for i, user_id in enumerate(participant_ids):
                if i == n - 1:
                    shares.append(ExpenseShare(user_id=user_id, amount=last_share_amount))
                else:
                    shares.append(ExpenseShare(user_id=user_id, amount=share_amount))
        
        elif split_mode == SplitMode.EXACT:
            # 精确金额模式：验证金额总和
            if not exact_amounts:
                raise ValueError("Exact amounts are required for EXACT split mode")
            
            if len(exact_amounts) != len(participant_ids):
                raise ValueError("Number of exact amounts must match number of participants")
            
            # 转换为 Decimal 并验证
            decimal_amounts = []
            for amt in exact_amounts:
                if not isinstance(amt, Decimal):
                    amt = Decimal(str(amt))
                if amt < 0:
                    raise ValueError("Exact amount cannot be negative")
                decimal_amounts.append(amt)
            
            # 验证总和
            sum_amounts = sum(decimal_amounts)
            if sum_amounts != total_amount:
                raise ValueError(
                    f"Sum of shares ({sum_amounts}) does not equal total amount ({total_amount})"
                )
            
            for user_id, amt in zip(participant_ids, decimal_amounts):
                shares.append(ExpenseShare(user_id=user_id, amount=amt))
        
        elif split_mode == SplitMode.PERCENTAGE:
            # 百分比模式：验证百分比总和
            if not percentages:
                raise ValueError("Percentages are required for PERCENTAGE split mode")
            
            if len(percentages) != len(participant_ids):
                raise ValueError("Number of percentages must match number of participants")
            
            # 转换为 Decimal 并验证
            decimal_percentages = []
            for pct in percentages:
                if not isinstance(pct, Decimal):
                    pct = Decimal(str(pct))
                if pct < 0 or pct > 100:
                    raise ValueError("Percentage must be between 0 and 100")
                decimal_percentages.append(pct)
            
            # 验证总和
            sum_percentages = sum(decimal_percentages)
            if sum_percentages != Decimal('100'):
                raise ValueError(
                    f"Sum of percentages ({sum_percentages}) does not equal 100"
                )
            
            # 计算金额，处理舍入误差
            total_assigned = Decimal('0')
            for i, (user_id, pct) in enumerate(zip(participant_ids, decimal_percentages)):
                if i == len(participant_ids) - 1:
                    # 最后一个人承担舍入误差
                    share_amount = total_amount - total_assigned
                else:
                    share_amount = (total_amount * pct / Decimal('100')).quantize(Decimal('0.01'))
                    total_assigned += share_amount
                
                shares.append(ExpenseShare(
                    user_id=user_id,
                    amount=share_amount,
                    percentage=pct
                ))
        
        else:
            raise ValueError(f"Unknown split mode: {split_mode}")
        
        return shares
    
    def get_share_for_user(self, user_id: str) -> Optional[ExpenseShare]:
        """获取指定用户的分摊明细"""
        for share in self.shares:
            if share.user_id == user_id:
                return share
        return None
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Expense):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
