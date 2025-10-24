"""
ALB 访问控制 API 路由
实现 AddEntriesToAcl 和 RemoveEntriesFromAcl 接口
"""

from fastapi import APIRouter, Depends
from loguru import logger
from core.config import settings
from services.alicloud import AliCloudClient
from api.models import (
    AddEntriesToAclRequest,
    AddEntriesToAclResponse,
    RemoveEntriesFromAclRequest,
    RemoveEntriesFromAclResponse,
    ErrorResponse,
    APIDocumentation
)

# 创建路由器实例
router = APIRouter()

# 初始化阿里云客户端
aliyun_client = AliCloudClient()

# API 文档信息
add_entries_to_acl_doc = APIDocumentation(
    title="添加ALB访问控制条目",
    url="https://help.aliyun.com/zh/slb/application-load-balancer/developer-reference/api-alb-2020-06-16-addentriestoacl",
    description="添加 ALB 访问控制条目，支持设置来源 IP 地址段和描述信息。支持从环境变量获取默认ACL ID。",
    parameter_info="参数说明: SourceCidrIp - 来源IP地址段（CIDR格式，如192.168.1.0/24）；AclId - 访问控制列表ID（可选，默认从环境变量DEFAULT_ALB_ACL_ID获取）；Description - 描述信息（可选，默认为添加时间和日期）"
)

remove_entries_from_acl_doc = APIDocumentation(
    title="删除ALB访问控制条目",
    url="https://help.aliyun.com/zh/slb/application-load-balancer/developer-reference/api-alb-2020-06-16-removeentriesfromacl",
    description="删除 ALB 访问控制条目，支持从指定ACL中移除单个IP地址段。支持从环境变量获取默认ACL ID。",
    parameter_info="参数说明: SourceCidrIp - 来源IP地址段（CIDR格式，如192.168.1.0/24）；AclId - 访问控制列表ID（可选，默认从环境变量DEFAULT_ALB_ACL_ID获取）"
)

@router.get("/examples", tags=["ALB 使用示例"])
async def get_alb_examples():
    """获取 ALB API 使用示例"""
    return {
        "add_entries_to_acl": [
            {
                "description": "添加单个IP地址到默认ACL",
                "request": {
                    "source_cidr_ip": "192.168.1.100/32",
                    "description": "服务器IP地址"
                },
                "endpoint": "POST /api/v1/alb/add-entries"
            },
            {
                "description": "添加IP地址段到指定ACL",
                "request": {
                    "acl_id": "acl-nnd9vclvwdcorsg1rm",
                    "source_cidr_ip": "192.168.1.0/24",
                    "description": "内网IP段"
                },
                "endpoint": "POST /api/v1/alb/add-entries"
            }
        ],
        "remove_entries_from_acl": [
            {
                "description": "从默认ACL删除IP地址",
                "request": {
                    "source_cidr_ip": "192.168.1.100/32"
                },
                "endpoint": "POST /api/v1/alb/remove-entries"
            }
        ],
        "parameter_requirements": [
            "所有IP地址必须使用CIDR格式（如192.168.1.0/24）",
            "ACL ID可选，不提供时使用环境变量DEFAULT_ALB_ACL_ID的值",
            "描述信息可选，不提供时使用自动生成的时间戳"
        ]
    }


@router.get("/docs", tags=["ALB 文档"])
async def get_alb_documentation():
    """获取 ALB API 文档信息"""
    return {
        "add_entries_to_acl": add_entries_to_acl_doc,
        "remove_entries_from_acl": remove_entries_from_acl_doc
    }

@router.post("/add-entries", response_model=AddEntriesToAclResponse, tags=["ALB 添加访问控制"])
async def add_entries_to_acl(
    request: AddEntriesToAclRequest
):
    """添加 ALB 访问控制条目 (AddEntriesToAcl)"""
    logger.info(f"收到添加 ALB 访问控制请求: {request.source_cidr_ip}")

    try:
        # 使用默认ACL ID或请求中的ACL ID
        acl_id = request.acl_id or settings.default_alb_acl_id

        # 调用阿里云客户端
        result = aliyun_client.add_entries_to_acl(
            acl_id=acl_id,
            source_cidr_ip=request.source_cidr_ip,
            description=request.description
        )

        if result["success"]:
            logger.info(f"成功添加 ALB 访问控制条目: {request.source_cidr_ip}")
            return AddEntriesToAclResponse(
                success=True,
                message="添加 ALB 访问控制条目成功",
                acl_entry_ip=request.source_cidr_ip,
                description=request.description or f"添加于 {aliyun_client._get_current_time()}",
                acl_id=acl_id
            )
        else:
            logger.error(f"添加 ALB 访问控制条目失败: {result['error']}")
            return AddEntriesToAclResponse(
                success=False,
                message=f"添加失败: {result['error']}",
                acl_entry_ip=request.source_cidr_ip,
                description=request.description or f"添加于 {aliyun_client._get_current_time()}",
                acl_id=acl_id
            )

    except Exception as e:
        logger.error(f"添加 ALB 访问控制条目异常: {str(e)}")
        raise Exception(f"添加 ALB 访问控制条目时发生错误: {str(e)}")

@router.post("/remove-entries", response_model=RemoveEntriesFromAclResponse, tags=["ALB 删除访问控制"])
async def remove_entries_from_acl(
    request: RemoveEntriesFromAclRequest
):
    """删除 ALB 访问控制条目 (RemoveEntriesFromAcl)"""
    logger.info(f"收到删除 ALB 访问控制请求: {request.source_cidr_ip}")

    try:
        # 使用默认ACL ID或请求中的ACL ID
        acl_id = request.acl_id or settings.default_alb_acl_id

        # 调用阿里云客户端
        result = aliyun_client.remove_entries_from_acl(
            acl_id=acl_id,
            source_cidr_ip=request.source_cidr_ip
        )

        if result["success"]:
            logger.info(f"成功删除 ALB 访问控制条目: {request.source_cidr_ip}")
            return RemoveEntriesFromAclResponse(
                success=True,
                message="删除 ALB 访问控制条目成功",
                acl_entry_ip=request.source_cidr_ip,
                acl_id=acl_id
            )
        else:
            logger.error(f"删除 ALB 访问控制条目失败: {result['error']}")
            return RemoveEntriesFromAclResponse(
                success=False,
                message=f"删除失败: {result['error']}",
                acl_entry_ip=request.source_cidr_ip,
                acl_id=acl_id
            )

    except Exception as e:
        logger.error(f"删除 ALB 访问控制条目异常: {str(e)}")
        raise Exception(f"删除 ALB 访问控制条目时发生错误: {str(e)}")