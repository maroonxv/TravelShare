"""
跨限界上下文事件处理器

处理需要在不同限界上下文之间同步的事件。
"""
from typing import Optional

# 从各个上下文导入事件类型
# 注意：实际部署时可能需要通过事件总线传递序列化的事件


class CrossContextSyncHandler:
    """跨上下文同步事件处理器
    
    处理：
    - 用户注册后在其他上下文创建用户档案
    - 用户停用后在其他上下文标记用户状态
    - 旅行完成后在社交上下文触发游记提示
    """
    
    def __init__(
        self,
        travel_user_profile_service=None,
        social_user_profile_service=None,
        notification_service=None
    ):
        """
        Args:
            travel_user_profile_service: app_travel 的用户档案服务
            social_user_profile_service: app_social 的用户档案服务
            notification_service: 通知服务
        """
        self._travel_user_profile_service = travel_user_profile_service
        self._social_user_profile_service = social_user_profile_service
        self._notification_service = notification_service
    
    def handle_user_registered(self, event) -> None:
        """处理用户注册事件
        
        在 app_travel 和 app_social 创建对应的用户档案。
        
        Args:
            event: UserRegisteredEvent
        """
        user_id = event.user_id
        username = event.username
        
        # 在 app_travel 创建旅行者档案
        if self._travel_user_profile_service:
            try:
                self._travel_user_profile_service.create_traveler_profile(
                    user_id=user_id,
                    username=username
                )
            except Exception as e:
                # 记录错误但不阻断流程
                print(f"Failed to create traveler profile: {e}")
        
        # 在 app_social 创建社交档案
        if self._social_user_profile_service:
            try:
                self._social_user_profile_service.create_social_profile(
                    user_id=user_id,
                    username=username
                )
            except Exception as e:
                print(f"Failed to create social profile: {e}")
    
    def handle_user_deactivated(self, event) -> None:
        """处理用户停用事件
        
        在其他上下文标记用户状态为停用。
        
        Args:
            event: UserDeactivatedEvent
        """
        user_id = event.user_id
        
        # 在 app_travel 标记用户状态
        if self._travel_user_profile_service:
            try:
                self._travel_user_profile_service.deactivate_user(user_id)
            except Exception as e:
                print(f"Failed to deactivate user in travel: {e}")
        
        # 在 app_social 标记用户状态
        if self._social_user_profile_service:
            try:
                self._social_user_profile_service.deactivate_user(user_id)
            except Exception as e:
                print(f"Failed to deactivate user in social: {e}")
    
    def handle_trip_completed(self, event) -> None:
        """处理旅行完成事件
        
        在 app_social 触发游记创建提示。
        
        Args:
            event: TripCompletedEvent
        """
        trip_id = event.trip_id
        creator_id = event.creator_id
        trip_name = event.name
        
        # 通知用户可以创建游记
        if self._notification_service:
            self._notification_service.send_push(
                user_id=creator_id,
                title="旅行已完成，记录精彩瞬间 ✨",
                body=f"您的「{trip_name}」旅行已完成！现在可以分享您的旅行故事了。",
                data={
                    "type": "trip_completed",
                    "trip_id": trip_id,
                    "action": "create_travel_log"
                }
            )
        
        # 如果有社交档案服务，可以在用户的待办中添加"创建游记"提示
        if self._social_user_profile_service:
            try:
                self._social_user_profile_service.add_travel_log_prompt(
                    user_id=creator_id,
                    trip_id=trip_id,
                    trip_name=trip_name
                )
            except Exception as e:
                print(f"Failed to add travel log prompt: {e}")
    
    def handle_user_reactivated(self, event) -> None:
        """处理用户重新激活事件
        
        在其他上下文恢复用户状态。
        
        Args:
            event: UserReactivatedEvent
        """
        user_id = event.user_id
        
        if self._travel_user_profile_service:
            try:
                self._travel_user_profile_service.reactivate_user(user_id)
            except Exception as e:
                print(f"Failed to reactivate user in travel: {e}")
        
        if self._social_user_profile_service:
            try:
                self._social_user_profile_service.reactivate_user(user_id)
            except Exception as e:
                print(f"Failed to reactivate user in social: {e}")
