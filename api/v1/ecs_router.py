"""
ECS 安全组 API 路由
实现 AuthorizeSecurityGroup 和 RevokeSecurityGroup 接口
"""

from fastapi import APIRouter, Depends
from loguru import logger
from services.alicloud import AliCloudClient
from api.models import (
    AuthorizeSecurityGroupRequest,
    AuthorizeSecurityGroupResponse,
    RevokeSecurityGroupRequest,
    RevokeSecurityGroupResponse,
    ErrorResponse,
    APIDocumentation
)

# 创建路由器实例
router = APIRouter()

# 初始化阿里云客户端
aliyun_client = AliCloudClient()

# API 文档信息
authorize_security_group_doc = APIDocumentation(
    title="添加ECS安全组入方向规则",
    url="https://help.aliyun.com/zh/ecs/developer-reference/api-ecs-2014-05-26-authorizesecuritygroup",
    description="添加 ECS 安全组入方向规则，支持配置IP地址段、端口范围、协议类型等参数来控制网络访问权限。",
    parameter_info="参数说明: SourceCidrIp - 来源IP地址段（CIDR格式，如192.168.1.0/24）；SecurityGroupId - 安全组ID（可选，默认从环境变量DEFAULT_SECURITY_GROUP_ID获取）；Policy - 访问策略（Drop或Accept，默认Drop）；PortRange - 端口范围（如22/22或1/65535，默认1/65535）；IpProtocol - 协议类型（TCP、UDP、ICMP或ALL，默认ALL）；Description - 描述信息（可选）"
)

revoke_security_group_doc = APIDocumentation(
    title="删除ECS安全组入方向规则",
    url="https://help.aliyun.com/zh/ecs/developer-reference/api-ecs-2014-05-26-revokesecuritygroup",
    description="删除 ECS 安全组入方向规则，通过指定权限参数删除指定的访问规则。",
    parameter_info="参数说明: SourceCidrIp - 来源IP地址段（CIDR格式）；SecurityGroupId - 安全组ID（可选，默认从环境变量DEFAULT_SECURITY_GROUP_ID获取）；Policy - 访问策略；PortRange - 端口范围；IpProtocol - 协议类型。所有参数必须与添加规则时保持一致"
)

@router.get("/examples", tags=["ECS 使用示例"])
async def get_ecs_examples():
    """获取 ECS API 使用示例"""
    return {
        "authorize_security_group": [
            {
                "description": "添加SSH访问规则",
                "request": {
                    "security_group_id": "sg-bp19nke7purenpearpmb",
                    "source_cidr_ip": "192.168.1.100/32",
                    "description": "允许SSH访问",
                    "policy": "Accept",
                    "port_range": "22/22",
                    "ip_protocol": "TCP"
                },
                "endpoint": "POST /api/v1/ecs/authorize"
            },
            {
                "description": "添加Web访问规则",
                "request": {
                    "source_cidr_ip": "192.168.1.0/24",
                    "description": "允许HTTP和HTTPS访问",
                    "policy": "Accept",
                    "port_range": "80/443",
                    "ip_protocol": "TCP"
                },
                "endpoint": "POST /api/v1/ecs/authorize"
            }
        ],
        "revoke_security_group": [
            {
                "description": "删除SSH访问规则",
                "request": {
                    "security_group_id": "sg-bp19nke7purenpearpmb",
                    "source_cidr_ip": "192.168.1.100/32",
                    "policy": "Accept",
                    "port_range": "22/22",
                    "ip_protocol": "TCP"
                },
                "endpoint": "POST /api/v1/ecs/revoke"
            }
        ],
        "parameter_requirements": [
            "所有IP地址必须使用CIDR格式（如192.168.1.0/24）",
            "安全组ID可选，不提供时使用环境变量DEFAULT_SECURITY_GROUP_ID的值",
            "端口范围格式：起始端口/结束端口（如22/22或80/443）",
            "协议类型：TCP、UDP、ICMP或ALL（大写）",
            "删除规则时，所有参数必须与添加时完全一致"
        ]
    }


@router.get("/docs", tags=["ECS 安全文档"])
async def get_ecs_documentation():
    """获取 ECS 安全组 API 文档信息"""
    return {
        "authorize_security_group": authorize_security_group_doc,
        "revoke_security_group": revoke_security_group_doc
    }

@router.post("/authorize", response_model=AuthorizeSecurityGroupResponse, tags=["ECS 添加安全组规则"])
async def authorize_security_group(
    request: AuthorizeSecurityGroupRequest
):
    """添加 ECS 安全组入方向规则 (AuthorizeSecurityGroup)"""
    logger.info(f"收到添加 ECS 安全组规则请求: {request.source_cidr_ip}")

    try:
        # 调用阿里云客户端
        result = aliyun_client.authorize_security_group(
            source_cidr_ip=request.source_cidr_ip,
            security_group_id=request.security_group_id,
            description=request.description,
            policy=request.policy,
            port_range=request.port_range,
            ip_protocol=request.ip_protocol
        )

        if result["success"]:
            logger.info(f"成功添加 ECS 安全组规则: {request.source_cidr_ip}")
            return AuthorizeSecurityGroupResponse(
                success=True,
                message="添加 ECS 安全组规则成功",
                source_cidr_ip=request.source_cidr_ip,
                security_group_id=request.security_group_id or aliyun_client.default_security_group_id,
                authorization_rule_id="generated_rule_id"  # 实际应从阿里云响应中获取
            )
        else:
            logger.error(f"添加 ECS 安全组规则失败: {result['error']}")
            return AuthorizeSecurityGroupResponse(
                success=False,
                message=f"添加失败: {result['error']}",
                source_cidr_ip=request.source_cidr_ip,
                security_group_id=request.security_group_id or aliyun_client.default_security_group_id,
                authorization_rule_id=""
            )

    except Exception as e:
        logger.error(f"添加 ECS 安全组规则异常: {str(e)}")
        raise Exception(f"添加 ECS 安全组规则时发生错误: {str(e)}")

@router.post("/revoke", response_model=RevokeSecurityGroupResponse, tags=["ECS 删除安全组规则"])
async def revoke_security_group(
    request: RevokeSecurityGroupRequest
):
    """删除 ECS 安全组入方向规则 (RevokeSecurityGroup)"""
    logger.info(f"收到删除 ECS 安全组规则请求: {request.source_cidr_ip}")

    try:
        # 调用阿里云客户端
        result = aliyun_client.revoke_security_group(
            source_cidr_ip=request.source_cidr_ip,
            security_group_id=request.security_group_id,
            policy=request.policy,
            port_range=request.port_range,
            ip_protocol=request.ip_protocol
        )

        if result["success"]:
            logger.info(f"成功删除 ECS 安全组规则: {request.source_cidr_ip}")
            return RevokeSecurityGroupResponse(
                success=True,
                message="删除 ECS 安全组规则成功",
                source_cidr_ip=request.source_cidr_ip,
                security_group_id=request.security_group_id or aliyun_client.default_security_group_id
            )
        else:
            logger.error(f"删除 ECS 安全组规则失败: {result['error']}")
            return RevokeSecurityGroupResponse(
                success=False,
                message=f"删除失败: {result['error']}",
                source_cidr_ip=request.source_cidr_ip,
                security_group_id=request.security_group_id or aliyun_client.default_security_group_id
            )

    except Exception as e:
        logger.error(f"删除 ECS 安全组规则异常: {str(e)}")
        raise Exception(f"删除 ECS 安全组规则时发生错误: {str(e)}")