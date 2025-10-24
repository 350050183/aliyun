"""
包含ALB路由的FastAPI应用
"""

import os
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create logs directory with proper permissions
os.makedirs("logs", exist_ok=True)

# Create FastAPI application（不添加任何中间件）
app = FastAPI(
    title="阿里云云资源管理服务",
    description="提供 ALB 访问控制和 ECS 安全组管理的 API 服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "service": "aliyun-manager"
    }

# 暂时注释掉有问题的导入
try:
    from api.v1.alb_router import router as alb_router
    app.include_router(alb_router, prefix="/api/v1/alb", tags=["ALB"])
    print("ALB router loaded successfully")

    from api.v1.ecs_router import router as ecs_router
    app.include_router(ecs_router, prefix="/api/v1/ecs", tags=["ECS"])
    print("ECS router loaded successfully")

    from api.v1.banip_router import router as banip_router
    app.include_router(banip_router, prefix="/api/v1/banip", tags=["BanIP"])
    print("BanIP router loaded successfully - ROUTE REGISTERED!")
except Exception as e:
    print(f"Failed to load routers: {e}")
    import traceback
    traceback.print_exc()

@app.get("/api/docs", tags=["API 文档汇总"])
async def get_api_documentation():
    """获取完整的API文档汇总"""
    return {
        "service_info": {
            "name": "阿里云云资源管理服务",
            "version": "1.0.0",
            "description": "提供 ALB 访问控制和 ECS 安全组管理的 API 服务",
            "status": "运行中"
        },
        "api_endpoints": {
            "alb_access_control": {
                "base_endpoint": "/api/v1/alb",
                "description": "ALB访问控制相关接口",
                "endpoints": [
                    {
                        "method": "POST",
                        "path": "/add-entries",
                        "description": "添加ALB访问控制条目",
                        "documentation": "/api/v1/alb/docs",
                        "examples": "/api/v1/alb/examples"
                    },
                    {
                        "method": "POST",
                        "path": "/remove-entries",
                        "description": "删除ALB访问控制条目",
                        "documentation": "/api/v1/alb/docs",
                        "examples": "/api/v1/alb/examples"
                    }
                ]
            },
            "ecs_security_group": {
                "base_endpoint": "/api/v1/ecs",
                "description": "ECS安全组相关接口",
                "endpoints": [
                    {
                        "method": "POST",
                        "path": "/authorize",
                        "description": "添加ECS安全组入方向规则",
                        "documentation": "/api/v1/ecs/docs",
                        "examples": "/api/v1/ecs/examples"
                    },
                    {
                        "method": "POST",
                        "path": "/revoke",
                        "description": "删除ECS安全组入方向规则",
                        "documentation": "/api/v1/ecs/docs",
                        "examples": "/api/v1/ecs/examples"
                    }
                ]
            }
        },
        "parameter_requirements": {
            "ip_format": "所有IP地址必须使用CIDR格式（如192.168.1.0/24）",
            "default_values": "ACL ID和Security Group ID可选，不提供时使用环境变量中的默认值",
            "protocol_format": "协议类型使用大写格式（TCP、UDP、ICMP、ALL）",
            "port_format": "端口范围格式：起始端口/结束端口（如22/22或80/443）"
        },
        "environment_variables": {
            "DEFAULT_ALB_ACL_ID": "默认ALB访问控制列表ID",
            "DEFAULT_SECURITY_GROUP_ID": "默认安全组ID",
            "ACCESS_KEY_ID": "阿里云访问密钥ID",
            "ACCESS_KEY_SECRET": "阿里云访问密钥密钥"
        },
        "quick_test": {
            "description": "快速测试接口功能",
            "test_ip": "34.1.28.44/32",
            "alb_add_test": {
                "endpoint": "POST /api/v1/alb/add-entries",
                "payload": {
                    "source_cidr_ip": "34.1.28.44/32",
                    "description": "测试IP地址"
                }
            },
            "ecs_add_test": {
                "endpoint": "POST /api/v1/ecs/authorize",
                "payload": {
                    "source_cidr_ip": "34.1.28.44/32",
                    "description": "测试SSH访问",
                    "policy": "Accept",
                    "port_range": "22/22",
                    "ip_protocol": "TCP"
                }
            }
        }
    }

# 暂时注释掉有问题的导入
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP 异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "detail": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "服务器内部错误",
            "timestamp": datetime.now().isoformat()
        }
    )