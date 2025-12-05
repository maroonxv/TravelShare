import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 读取配置
# 默认使用 SQLite 以防止未配置环境变量时报错，但在生产环境中应确保配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./travel_sharing.db")

# 创建 Engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

# 创建 SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 定义全局 Base
Base = declarative_base()

def get_db():
    """获取数据库会话生成器"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
