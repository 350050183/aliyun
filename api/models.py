"""
API 请求和响应模型
定义所有接口的数据结构
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from core.config import settings

# ==== 公共响应模型 ====

class ApiResponse(BaseModel):
    """API 通用响应模型"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")

class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str = Field(..., description="错误类型")
    detail: str = Field(..., description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="错误时间")

# ==== ALB 访问控制模型 ====

class AddEntriesToAclRequest(BaseModel):
    """添加 ALB 访问控制条目请求"""
    acl_id: Optional[str] = None
    source_cidr_ip: str = Field(..., description="来源 IP 地址段")
    description: Optional[str] = Field(None, description="描述信息")

class AddEntriesToAclResponse(ApiResponse):
    """添加 ALB 访问控制条目响应"""
    acl_entry_ip: str = Field(..., description="已添加的 IP 地址")
    description: str = Field(..., description="描述信息")
    acl_id: str = Field(..., description="访问控制列表 ID")

class RemoveEntriesFromAclRequest(BaseModel):
    """删除 ALB 访问控制条目请求"""
    acl_id: Optional[str] = None
    source_cidr_ip: str = Field(..., description="来源 IP 地址段")

class RemoveEntriesFromAclResponse(ApiResponse):
    """删除 ALB 访问控制条目响应"""
    acl_entry_ip: str = Field(..., description="已删除的 IP 地址")
    acl_id: str = Field(..., description="访问控制列表 ID")

# ==== ECS 安全组模型 ====

class AuthorizeSecurityGroupRequest(BaseModel):
    """添加 ECS 安全组规则请求"""
    source_cidr_ip: str = Field(..., description="来源 IP 地址段")
    security_group_id: Optional[str] = Field(None, description="安全组 ID")
    description: Optional[str] = Field(None, description="描述信息")
    policy: str = Field(default="Drop", description="访问策略")
    port_range: str = Field(default="1/65535", description="端口范围")
    ip_protocol: str = Field(default="ALL", description="协议类型")

class AuthorizeSecurityGroupResponse(ApiResponse):
    """添加 ECS 安全组规则响应"""
    source_cidr_ip: str = Field(..., description="已添加的 IP 地址")
    security_group_id: str = Field(..., description="安全组 ID")
    authorization_rule_id: str = Field(..., description="授权规则 ID")

class RevokeSecurityGroupRequest(BaseModel):
    """删除 ECS 安全组规则请求"""
    source_cidr_ip: str = Field(..., description="来源 IP 地址段")
    security_group_id: Optional[str] = Field(None, description="安全组 ID")
    policy: str = Field(default="Drop", description="访问策略")
    port_range: str = Field(default="1/65535", description="端口范围")
    ip_protocol: str = Field(default="ALL", description="协议类型")

class RevokeSecurityGroupResponse(ApiResponse):
    """删除 ECS 安全组规则响应"""
    source_cidr_ip: str = Field(..., description="已删除的 IP 地址")
    security_group_id: str = Field(..., description="安全组 ID")

# ==== API 文档响应模型 ====

# ==== BanIP 聚合接口模型 ====

class BanIPRequest(BaseModel):
    """BanIP 封禁请求模型"""
    ip: str = Field(..., description="要封禁的IP地址")
    description: Optional[str] = Field(None, description="封禁描述")

class BanIPResponse(ApiResponse):
    """BanIP 封禁响应模型"""
    ip: str = Field(..., description="被封禁的IP地址")
    alb_result: Optional[AddEntriesToAclResponse] = Field(None, description="ALB封禁结果")
    ecs_result: Optional[AuthorizeSecurityGroupResponse] = Field(None, description="ECS封禁结果")

class UnbanIPRequest(BaseModel):
    """BanIP 解封请求模型"""
    ip: str = Field(..., description="要解封的IP地址")
    description: Optional[str] = Field(None, description="解封描述")

class UnbanIPResponse(ApiResponse):
    """BanIP 解封响应模型"""
    ip: str = Field(..., description="被解封的IP地址")
    alb_result: Optional[RemoveEntriesFromAclResponse] = Field(None, description="ALB解封结果")
    ecs_result: Optional[RevokeSecurityGroupResponse] = Field(None, description="ECS解封结果")

class APIDocumentation(BaseModel):
    """API 文档模型"""
    title: str = Field(..., description="接口名称")
    url: str = Field(..., description="文档链接")
    description: str = Field(..., description="接口说明")
    parameter_info: str = Field(..., description="参数说明")