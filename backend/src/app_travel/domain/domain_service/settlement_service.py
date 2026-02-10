"""
结算服务 - 领域服务

负责计算费用结算方案，使用贪心算法最小化转账次数。
"""
import json
from decimal import Decimal
from typing import List, Dict

from app_travel.domain.entity.expense import Expense
from app_travel.domain.value_objects.expense_value_objects import SettlementTransfer


class SettlementService:
    """结算服务
    
    提供费用结算计算功能，包括余额计算和转账最小化。
    """
    
    @staticmethod
    def calculate_balances(expenses: List[Expense]) -> Dict[str, Decimal]:
        """计算每个成员的净余额
        
        净余额 = 总付出 - 总应付
        正数表示应收，负数表示应付
        
        Args:
            expenses: 费用列表
            
        Returns:
            Dict[str, Decimal]: 用户ID到净余额的映射
        """
        balances: Dict[str, Decimal] = {}
        
        for expense in expenses:
            # 付款人增加余额（付出）
            if expense.payer_id not in balances:
                balances[expense.payer_id] = Decimal('0')
            balances[expense.payer_id] += expense.amount
            
            # 参与者减少余额（应付）
            for share in expense.shares:
                if share.user_id not in balances:
                    balances[share.user_id] = Decimal('0')
                balances[share.user_id] -= share.amount
        
        return balances
    
    @staticmethod
    def minimize_transfers(balances: Dict[str, Decimal]) -> List[SettlementTransfer]:
        """使用贪心算法最小化转账次数
        
        算法：
        1. 分离债务人（余额<0）和债权人（余额>0）
        2. 排序：债务人按余额升序，债权人按余额降序
        3. 循环匹配：最大债务人向最大债权人转账
        4. 转账金额为 min(|债务|, 债权)
        5. 更新余额，移除已清零的成员
        6. 重复直到所有余额为0
        
        Args:
            balances: 用户ID到净余额的映射
            
        Returns:
            List[SettlementTransfer]: 最小化的转账列表
        """
        # 过滤出非零余额
        debtors = []  # (user_id, debt_amount) debt_amount > 0
        creditors = []  # (user_id, credit_amount) credit_amount > 0
        
        for user_id, balance in balances.items():
            if balance < 0:
                debtors.append([user_id, -balance])  # 转为正数
            elif balance > 0:
                creditors.append([user_id, balance])
        
        # 排序：债务人按债务降序，债权人按债权降序
        debtors.sort(key=lambda x: x[1], reverse=True)
        creditors.sort(key=lambda x: x[1], reverse=True)
        
        transfers = []
        
        # 贪心匹配
        i, j = 0, 0
        while i < len(debtors) and j < len(creditors):
            debtor_id, debt = debtors[i]
            creditor_id, credit = creditors[j]
            
            # 转账金额为两者中较小的
            transfer_amount = min(debt, credit)
            
            # 获取货币（假设所有费用使用相同货币，这里使用CNY）
            # 在实际应用中，应该从费用中获取货币信息
            currency = "CNY"
            
            transfers.append(SettlementTransfer(
                from_user_id=debtor_id,
                to_user_id=creditor_id,
                amount=transfer_amount,
                currency=currency,
                is_settled=False
            ))
            
            # 更新余额
            debtors[i][1] -= transfer_amount
            creditors[j][1] -= transfer_amount
            
            # 移除已清零的
            if debtors[i][1] == 0:
                i += 1
            if creditors[j][1] == 0:
                j += 1
        
        return transfers
    
    @staticmethod
    def to_json(transfers: List[SettlementTransfer]) -> str:
        """序列化结算结果为 JSON
        
        Args:
            transfers: 转账列表
            
        Returns:
            str: JSON字符串
        """
        data = []
        for transfer in transfers:
            data.append({
                'from_user_id': transfer.from_user_id,
                'to_user_id': transfer.to_user_id,
                'amount': str(transfer.amount),
                'currency': transfer.currency,
                'is_settled': transfer.is_settled
            })
        return json.dumps(data)
    
    @staticmethod
    def from_json(json_str: str) -> List[SettlementTransfer]:
        """从 JSON 反序列化结算结果
        
        Args:
            json_str: JSON字符串
            
        Returns:
            List[SettlementTransfer]: 转账列表
        """
        data = json.loads(json_str)
        transfers = []
        for item in data:
            transfers.append(SettlementTransfer(
                from_user_id=item['from_user_id'],
                to_user_id=item['to_user_id'],
                amount=Decimal(item['amount']),
                currency=item['currency'],
                is_settled=item['is_settled']
            ))
        return transfers
