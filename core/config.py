"""
配置管理模块
管理所有应用配置参数
"""

import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """应用配置设置"""

    # Alibaba Cloud 配置
    access_key_id: str = os.getenv("ACCESS_KEY_ID", "")
    access_key_secret: str = os.getenv("ACCESS_KEY_SECRET", "")
    default_region: str = os.getenv("DEFAULT_REGION", "cn-hangzhou")
    default_security_group_id: str = os.getenv("DEFAULT_SECURITY_GROUP_ID", "sg-bp19nke7purenpearpmb")
    default_alb_acl_id: str = os.getenv("DEFAULT_ALB_ACL_ID", "acl-nnd9vclvwdcorsg1rm")

    # 日志配置
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # 白名单配置
    whitelist_ips: str = os.getenv("WHITELIST_IPS", "")

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def WHITELIST_IPS(self) -> List[str]:
        """解析白名单 IP 列表"""
        if not self.whitelist_ips:
            return []
        return [ip.strip() for ip in self.whitelist_ips.split(",") if ip.strip()]

# 创建全局配置实例
settings = Settings()