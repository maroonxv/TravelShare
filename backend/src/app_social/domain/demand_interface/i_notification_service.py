"""
通知服务接口

调用外部推送服务的抽象接口。
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List


class INotificationService(ABC):
    """通知服务接口"""
    
    @abstractmethod
    def send_push(
        self,
        user_id: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """发送推送通知
        
        Args:
            user_id: 目标用户ID
            title: 通知标题
            body: 通知内容
            data: 附加数据（可选）
            
        Returns:
            是否发送成功
        """
        pass
    
    @abstractmethod
    def send_push_batch(
        self,
        user_ids: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, bool]:
        """批量发送推送通知
        
        Args:
            user_ids: 目标用户ID列表
            title: 通知标题
            body: 通知内容
            data: 附加数据（可选）
            
        Returns:
            用户ID到发送结果的映射
        """
        pass
    
    @abstractmethod
    def send_email(
        self,
        email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """发送邮件通知
        
        Args:
            email: 目标邮箱
            subject: 邮件主题
            body: 邮件内容（纯文本）
            html_body: 邮件内容（HTML，可选）
            
        Returns:
            是否发送成功
        """
        pass
    
    @abstractmethod
    def send_sms(self, phone: str, message: str) -> bool:
        """发送短信通知
        
        Args:
            phone: 目标手机号
            message: 短信内容
            
        Returns:
            是否发送成功
        """
        pass
