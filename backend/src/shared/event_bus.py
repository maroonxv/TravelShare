"""
事件总线 - 简单的进程内事件发布订阅机制

用于领域事件的发布和处理。
"""
from typing import Dict, List, Callable, Any, TYPE_CHECKING
from collections import defaultdict

if TYPE_CHECKING:
    from app_travel.domain.domain_event.travel_events import DomainEvent


class EventBus:
    """简单的进程内事件总线
    
    支持：
    - 按事件类型订阅处理器
    - 同步事件发布
    - 多处理器支持
    """
    
    _instance = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._handlers: Dict[str, List[Callable]] = defaultdict(list)
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> 'EventBus':
        """获取事件总线实例"""
        return cls()
    
    @classmethod
    def reset(cls) -> None:
        """重置事件总线（仅用于测试）"""
        if cls._instance:
            cls._instance._handlers.clear()
    
    def subscribe(self, event_type: str, handler: Callable[['DomainEvent'], None]) -> None:
        """订阅事件
        
        Args:
            event_type: 事件类型名称（通常是类名）
            handler: 事件处理函数，接收 DomainEvent 参数
        """
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: Callable[['DomainEvent'], None]) -> None:
        """取消订阅
        
        Args:
            event_type: 事件类型名称
            handler: 要取消的处理函数
        """
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
    
    def publish(self, event: 'DomainEvent') -> None:
        """发布单个事件
        
        同步调用所有订阅了该事件类型的处理器。
        
        Args:
            event: 领域事件
        """
        event_type = event.event_type
        handlers = self._handlers.get(event_type, [])
        
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                # 记录错误但不阻断其他处理器
                print(f"Event handler error for {event_type}: {e}")
    
    def publish_all(self, events: List['DomainEvent']) -> None:
        """发布多个事件
        
        按顺序发布所有事件。
        
        Args:
            events: 领域事件列表
        """
        for event in events:
            self.publish(event)
    
    def get_handlers(self, event_type: str) -> List[Callable]:
        """获取指定事件类型的所有处理器（用于调试）"""
        return self._handlers.get(event_type, []).copy()
    
    def clear_handlers(self, event_type: str = None) -> None:
        """清除处理器
        
        Args:
            event_type: 如果指定，只清除该类型的处理器；否则清除所有
        """
        if event_type:
            self._handlers[event_type].clear()
        else:
            self._handlers.clear()


# 便捷的全局事件总线访问
def get_event_bus() -> EventBus:
    """获取全局事件总线实例"""
    return EventBus.get_instance()
