from typing import Any, Dict, List, Optional, Tuple, Type
from sqlalchemy.orm import Session
from sqlalchemy import select, func, inspect

class AdminGenericDao:
    """通用 CRUD DAO，用于 Admin 模块"""
    
    def __init__(self, session: Session):
        self.session = session

    def get_list(self, model_class: Type[Any], page: int = 1, per_page: int = 20) -> Tuple[List[Any], int]:
        """分页获取列表"""
        # 获取总数
        # 注意：这里假设主键是 id，或者直接 count(*)
        count_stmt = select(func.count()).select_from(model_class)
        total = self.session.execute(count_stmt).scalar() or 0

        # 获取分页数据
        stmt = select(model_class).offset((page - 1) * per_page).limit(per_page)
        items = self.session.execute(stmt).scalars().all()
        
        return list(items), total

    def get_by_id(self, model_class: Type[Any], id: Any) -> Optional[Any]:
        """根据 ID 获取详情"""
        return self.session.get(model_class, id)

    def create(self, model_class: Type[Any], data: Dict[str, Any]) -> Any:
        """创建记录"""
        # 过滤掉不在 model 定义中的字段，防止报错
        valid_keys = self._get_valid_columns(model_class)
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        
        obj = model_class(**filtered_data)
        self.session.add(obj)
        self.session.flush()
        return obj

    def update(self, model_class: Type[Any], id: Any, data: Dict[str, Any]) -> Optional[Any]:
        """更新记录"""
        obj = self.session.get(model_class, id)
        if not obj:
            return None
        
        valid_keys = self._get_valid_columns(model_class)
        for key, value in data.items():
            if key in valid_keys:
                setattr(obj, key, value)
        
        self.session.flush()
        return obj

    def delete(self, model_class: Type[Any], id: Any) -> bool:
        """删除记录"""
        obj = self.session.get(model_class, id)
        if obj:
            self.session.delete(obj)
            self.session.flush()
            return True
        return False

    def _get_valid_columns(self, model_class: Type[Any]) -> List[str]:
        """获取模型的所有列名"""
        mapper = inspect(model_class)
        return [c.key for c in mapper.attrs]
