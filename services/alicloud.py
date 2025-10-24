"""
阿里云客户端服务
封装 ACCESS_KEY_ID 和 ACCESS_KEY_SECRET 的认证方式
"""

from typing import Optional, Dict, Any
import json
from alibabacloud_tea_openapi.models import Config as TeaConfig
from alibabacloud_tea_util import models as UtilModels
from alibabacloud_ecs20140526.client import Client as EcsClient
from alibabacloud_alb20200616.client import Client as AlbClient
from alibabacloud_ecs20140526 import models as EcsModels
from alibabacloud_alb20200616 import models as AlbModels
from core.config import settings
from loguru import logger

class AliCloudClient:
    """阿里云 API 客户端管理类"""

    def __init__(self):
        self.ak_id = settings.access_key_id
        self.ak_secret = settings.access_key_secret
        self.default_region = settings.default_region
        self.default_security_group_id = settings.default_security_group_id

        # 初始化客户端
        self._init_clients()

    def _init_clients(self):
        """初始化阿里云客户端"""
        if not self.ak_id or not self.ak_secret:
            logger.warning("阿里云 AK/SK 未配置，将使用默认凭证")
            # 在容器环境中，可以依赖阿里云容器服务的默认凭证
            config = TeaConfig()
        else:
            config = TeaConfig(
                access_key_id=self.ak_id,
                access_key_secret=self.ak_secret
            )

        # 设置endpoint（使用全局域名）
        config.endpoint = "ecs.aliyuncs.com"
        self.ecs_client = EcsClient(config)

        config.endpoint = "alb.cn-hangzhou.aliyuncs.com"  # 使用区域特定的ALB域名
        self.alb_client = AlbClient(config)

        logger.info("阿里云客户端初始化完成")

    def _make_request(self, client, request, operation_name: str, action: str, version: str) -> Dict[str, Any]:
        """执行 API 请求的通用方法"""
        try:
            logger.info(f"执行阿里云 API: {operation_name}")

            # 直接调用client的方法，不使用call_api
            if hasattr(client, action):
                method = getattr(client, action)
                response = method(request)
            else:
                # 如果没有直接方法，尝试直接调用call_api
                response = client.call_api(request)

            logger.info(f"API 响应: {operation_name} - 成功")

            return {
                "success": True,
                "data": response,
                "operation": operation_name
            }

        except Exception as e:
            logger.error(f"API 错误: {operation_name} - {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "operation": operation_name
            }

    # ==== ALB 访问控制相关方法 ====

    def add_entries_to_acl(self, acl_id: str, source_cidr_ip: str, description: Optional[str] = None) -> Dict[str, Any]:
        """添加 ALB 访问控制条目"""

        # 创建AclEntries对象，并显式设置description为None
        acl_entries = AlbModels.AddEntriesToAclRequestAclEntries(
            entry=source_cidr_ip,
            description=None
        )

        # 创建请求
        request = AlbModels.AddEntriesToAclRequest()
        request.acl_id = acl_id
        request.acl_entries = [acl_entries]

        try:
            logger.info(f"执行阿里云 API: AddEntriesToAcl")

            # 使用带options的方法调用，需要runtime参数
            runtime = UtilModels.RuntimeOptions()
            response = self.alb_client.add_entries_to_acl_with_options(request, runtime)
            logger.info(f"API 响应: AddEntriesToAcl - 成功")

            return {
                "success": True,
                "data": response,
                "operation": "AddEntriesToAcl"
            }

        except Exception as e:
            logger.error(f"API 错误: AddEntriesToAcl - {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "operation": "AddEntriesToAcl"
            }

    def remove_entries_from_acl(self, acl_id: str, source_cidr_ip: str) -> Dict[str, Any]:
        """删除 ALB 访问控制条目"""
        request = AlbModels.RemoveEntriesFromAclRequest()
        request.acl_id = acl_id
        request.entries = [source_cidr_ip]

        try:
            logger.info(f"执行阿里云 API: RemoveEntriesFromAcl")

            # 使用直接方法
            response = self.alb_client.remove_entries_from_acl(request)
            logger.info(f"API 响应: RemoveEntriesFromAcl - 成功")

            return {
                "success": True,
                "data": response,
                "operation": "RemoveEntriesFromAcl"
            }

        except Exception as e:
            logger.error(f"API 错误: RemoveEntriesFromAcl - {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "operation": "RemoveEntriesFromAcl"
            }

    # ==== ECS 安全组相关方法 ====

    def authorize_security_group(
        self,
        source_cidr_ip: str,
        security_group_id: Optional[str] = None,
        description: Optional[str] = None,
        policy: str = "Drop",
        port_range: str = "-1/-1",
        ip_protocol: str = "ALL"
    ) -> Dict[str, Any]:
        """添加 ECS 安全组入方向规则"""
        logger.info(f"authorize_security_group 被调用，ip_protocol={ip_protocol}")

        # 创建权限对象
        permissions = EcsModels.AuthorizeSecurityGroupRequestPermissions(
            source_cidr_ip=source_cidr_ip,
            port_range=port_range,
            ip_protocol=ip_protocol,
            policy=policy
        )

        # 创建请求
        request = EcsModels.AuthorizeSecurityGroupRequest()
        request.region_id = self.default_region
        request.security_group_id = security_group_id or self.default_security_group_id
        request.permissions = [permissions]

        try:
            logger.info(f"执行阿里云 API: AuthorizeSecurityGroup")
            logger.info(f"实际传递的协议值: {ip_protocol}")

            # 使用直接方法
            response = self.ecs_client.authorize_security_group(request)
            logger.info(f"API 响应: AuthorizeSecurityGroup - 成功")

            return {
                "success": True,
                "data": response,
                "operation": "AuthorizeSecurityGroup"
            }

        except Exception as e:
            logger.error(f"API 错误: AuthorizeSecurityGroup - {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "operation": "AuthorizeSecurityGroup"
            }

    def revoke_security_group(
        self,
        source_cidr_ip: str,
        security_group_id: Optional[str] = None,
        policy: str = "Drop",
        port_range: str = "-1/-1",
        ip_protocol: str = "ALL"
    ) -> Dict[str, Any]:
        """删除 ECS 安全组入方向规则"""
        # 创建权限对象
        permissions = EcsModels.RevokeSecurityGroupRequestPermissions(
            source_cidr_ip=source_cidr_ip,
            port_range=port_range,
            ip_protocol=ip_protocol,
            policy=policy
        )

        # 创建请求
        request = EcsModels.RevokeSecurityGroupRequest()
        request.region_id = self.default_region
        request.security_group_id = security_group_id or self.default_security_group_id
        request.permissions = [permissions]

        try:
            logger.info(f"执行阿里云 API: RevokeSecurityGroup")

            # 使用直接方法
            response = self.ecs_client.revoke_security_group(request)
            logger.info(f"API 响应: RevokeSecurityGroup - 成功")

            return {
                "success": True,
                "data": response,
                "operation": "RevokeSecurityGroup"
            }

        except Exception as e:
            logger.error(f"API 错误: RevokeSecurityGroup - {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "operation": "RevokeSecurityGroup"
            }

    def _get_current_time(self) -> str:
        """获取当前时间格式化字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")