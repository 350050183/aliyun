"""
BanIP 聚合接口路由
提供一键封禁和解封IP的功能，同时操作ALB和ECS安全组
"""

from fastapi import APIRouter, Depends
from loguru import logger
from services.alicloud import AliCloudClient
from api.models import (
    BanIPRequest,
    BanIPResponse,
    UnbanIPRequest,
    UnbanIPResponse,
    AddEntriesToAclRequest,
    AuthorizeSecurityGroupRequest,
    RemoveEntriesFromAclRequest,
    RevokeSecurityGroupRequest,
    ErrorResponse,
    AddEntriesToAclResponse,
    AuthorizeSecurityGroupResponse,
    RemoveEntriesFromAclResponse,
    RevokeSecurityGroupResponse
)
from core.config import settings

# 创建路由器实例
router = APIRouter()

# 初始化阿里云客户端
aliyun_client = AliCloudClient()

@router.post("/ban", response_model=BanIPResponse, tags=["IP封禁聚合接口"])
async def ban_ip(request: BanIPRequest):
    """一键封禁IP：同时添加到ALB黑名单和ECS拒绝规则"""
    logger.info(f"收到封禁IP请求: {request.ip}")

    # 转换为CIDR格式
    cidr_ip = f"{request.ip}/32" if "/" not in request.ip else request.ip
    description = request.description or f"IP封禁 - {request.ip}"

    alb_result = None
    ecs_result = None
    success_count = 0

    try:
        # 尝试封禁ALB访问
        try:
            result = aliyun_client.add_entries_to_acl(
                acl_id=settings.default_alb_acl_id,
                source_cidr_ip=cidr_ip,
                description=description
            )

            if result["success"]:
                logger.info(f"ALB封禁成功: {request.ip}")
                alb_result = AddEntriesToAclResponse(
                    success=True,
                    message="ALB封禁成功",
                    acl_entry_ip=cidr_ip,
                    description=description,
                    acl_id=settings.default_alb_acl_id
                )
                success_count += 1
            else:
                logger.error(f"ALB封禁失败: {result['error']}")
                alb_result = AddEntriesToAclResponse(
                    success=False,
                    message=f"ALB封禁失败: {result['error']}",
                    acl_entry_ip=cidr_ip,
                    description=description,
                    acl_id=settings.default_alb_acl_id
                )
        except Exception as e:
            logger.error(f"ALB封禁异常: {str(e)}")
            alb_result = AddEntriesToAclResponse(
                success=False,
                message=f"ALB封禁异常: {str(e)}",
                acl_entry_ip=cidr_ip,
                description=description,
                acl_id=aliyun_client.default_alb_acl_id
            )

        # 尝试封禁ECS访问（拒绝规则）
        try:
            result = aliyun_client.authorize_security_group(
                source_cidr_ip=cidr_ip,
                policy="Drop",  # 拒绝访问
                description=description,
                security_group_id=settings.default_security_group_id
            )

            if result["success"]:
                logger.info(f"ECS封禁成功: {request.ip}")
                ecs_result = AuthorizeSecurityGroupResponse(
                    success=True,
                    message="ECS封禁成功",
                    source_cidr_ip=cidr_ip,
                    security_group_id=settings.default_security_group_id,
                    authorization_rule_id="generated_rule_id"
                )
                success_count += 1
            else:
                logger.error(f"ECS封禁失败: {result['error']}")
                ecs_result = AuthorizeSecurityGroupResponse(
                    success=False,
                    message=f"ECS封禁失败: {result['error']}",
                    source_cidr_ip=cidr_ip,
                    security_group_id=settings.default_security_group_id,
                    authorization_rule_id=""
                )
        except Exception as e:
            logger.error(f"ECS封禁异常: {str(e)}")
            ecs_result = AuthorizeSecurityGroupResponse(
                success=False,
                message=f"ECS封禁异常: {str(e)}",
                source_cidr_ip=cidr_ip,
                security_group_id=settings.default_security_group_id,
                authorization_rule_id=""
            )

        # 判断整体成功率
        if success_count >= 1:
            # 至少有一个成功就算成功
            overall_success = True
            message = f"IP封禁完成（成功{success_count}/2）"
        else:
            overall_success = False
            message = "IP封禁失败（ALB和ECS均失败）"

        return BanIPResponse(
            success=overall_success,
            message=message,
            ip=request.ip,
            alb_result=alb_result,
            ecs_result=ecs_result
        )

    except Exception as e:
        logger.error(f"IP封禁聚合接口异常: {str(e)}")
        raise Exception(f"IP封禁时发生错误: {str(e)}")

@router.post("/unban", response_model=UnbanIPResponse, tags=["IP解封聚合接口"])
async def unban_ip(request: UnbanIPRequest):
    """一键解封IP：同时从ALB黑名单和ECS规则中删除"""
    logger.info(f"收到解封IP请求: {request.ip}")

    # 转换为CIDR格式
    cidr_ip = f"{request.ip}/32" if "/" not in request.ip else request.ip

    alb_result = None
    ecs_result = None
    success_count = 0

    try:
        # 尝试解封ALB访问
        try:
            result = aliyun_client.remove_entries_from_acl(
                acl_id=settings.default_alb_acl_id,
                source_cidr_ip=cidr_ip
            )

            if result["success"]:
                logger.info(f"ALB解封成功: {request.ip}")
                alb_result = RemoveEntriesFromAclResponse(
                    success=True,
                    message="ALB解封成功",
                    acl_entry_ip=cidr_ip,
                    acl_id=settings.default_alb_acl_id
                )
                success_count += 1
            else:
                logger.error(f"ALB解封失败: {result['error']}")
                alb_result = RemoveEntriesFromAclResponse(
                    success=False,
                    message=f"ALB解封失败: {result['error']}",
                    acl_entry_ip=cidr_ip,
                    acl_id=settings.default_alb_acl_id
                )
        except Exception as e:
            logger.error(f"ALB解封异常: {str(e)}")
            alb_result = RemoveEntriesFromAclResponse(
                success=False,
                message=f"ALB解封异常: {str(e)}",
                acl_entry_ip=cidr_ip,
                acl_id=settings.default_alb_acl_id
            )

        # 尝试解封ECS访问
        try:
            result = aliyun_client.revoke_security_group(
                source_cidr_ip=cidr_ip,
                policy="Drop",  # 删除拒绝规则
                security_group_id=settings.default_security_group_id
            )

            if result["success"]:
                logger.info(f"ECS解封成功: {request.ip}")
                ecs_result = RevokeSecurityGroupResponse(
                    success=True,
                    message="ECS解封成功",
                    source_cidr_ip=cidr_ip,
                    security_group_id=settings.default_security_group_id
                )
                success_count += 1
            else:
                logger.error(f"ECS解封失败: {result['error']}")
                ecs_result = RevokeSecurityGroupResponse(
                    success=False,
                    message=f"ECS解封失败: {result['error']}",
                    source_cidr_ip=cidr_ip,
                    security_group_id=settings.default_security_group_id
                )
        except Exception as e:
            logger.error(f"ECS解封异常: {str(e)}")
            ecs_result = RevokeSecurityGroupResponse(
                success=False,
                message=f"ECS解封异常: {str(e)}",
                source_cidr_ip=cidr_ip,
                security_group_id=settings.default_security_group_id
            )

        # 判断整体成功率
        if success_count >= 1:
            # 至少有一个成功就算成功
            overall_success = True
            message = f"IP解封完成（成功{success_count}/2）"
        else:
            overall_success = False
            message = "IP解封失败（ALB和ECS均失败）"

        return UnbanIPResponse(
            success=overall_success,
            message=message,
            ip=request.ip,
            alb_result=alb_result,
            ecs_result=ecs_result
        )

    except Exception as e:
        logger.error(f"IP解封聚合接口异常: {str(e)}")
        raise Exception(f"IP解封时发生错误: {str(e)}")

@router.get("/examples", tags=["BanIP 使用示例"])
async def get_banip_examples():
    """获取BanIP API使用示例"""
    return {
        "ban_ip": [
            {
                "description": "封禁恶意IP地址",
                "request": {
                    "ip": "34.1.28.44",
                    "description": "恶意扫描IP"
                },
                "endpoint": "POST /api/v1/banip/ban"
            },
            {
                "description": "封禁IP段",
                "request": {
                    "ip": "192.168.1.100/24",
                    "description": "内部网络攻击"
                },
                "endpoint": "POST /api/v1/banip/ban"
            }
        ],
        "unban_ip": [
            {
                "description": "解封误封IP",
                "request": {
                    "ip": "34.1.28.44",
                    "description": "误封解除"
                },
                "endpoint": "POST /api/v1/banip/unban"
            }
        ],
        "parameter_requirements": [
            "IP地址可以是单个IP（如34.1.28.44）或CIDR格式（如34.1.28.44/32）",
            "描述信息可选，用于记录封禁原因",
            "封禁操作会同时作用于ALB和ECS安全组",
            "解封操作需要确保之前有对应的封禁规则"
        ]
    }