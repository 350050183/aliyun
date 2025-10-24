"""
中间件模块
包含 IP 白名单验证等中间件
"""

from fastapi import Request, HTTPException
from typing import List
import ipaddress
from core.config import settings

class IPWhitelistMiddleware:
    """IP 白名单验证中间件"""

    def __init__(self, app, whitelist_ips: List[str]):
        self.app = app
        self.whitelisted_networks = []
        self._parse_whitelist_ips(whitelist_ips)

    def _parse_whitelist_ips(self, whitelist_ips: List[str]):
        """解析白名单 IP 列表"""
        for ip in whitelist_ips:
            try:
                # 支持单个 IP 和 CIDR 表示法
                if '/' in ip:
                    # CIDR 表示法 (如 192.168.1.0/24)
                    network = ipaddress.ip_network(ip, strict=False)
                    self.whitelisted_networks.append(network)
                else:
                    # 单个 IP 地址
                    ip_addr = ipaddress.ip_address(ip)
                    self.whitelisted_networks.append(ipaddress.ip_network(f"{ip}/128" if ':' in ip else f"{ip}/32"))
            except ValueError as e:
                print(f"Invalid IP address in whitelist: {ip} - {e}")

    async def __call__(self, request: Request, call_next):
        """中间件调用"""
        client_ip = request.client.host if request.client else None

        if not client_ip:
            raise HTTPException(status_code=400, detail="无法获取客户端 IP 地址")

        # 检查 IP 是否在白名单中
        if not self._is_ip_allowed(client_ip):
            raise HTTPException(status_code=403, detail=f"IP 地址 {client_ip} 不在白名单中")

        response = await call_next(request)
        return response

    def _is_ip_allowed(self, client_ip: str) -> bool:
        """检查 IP 是否被允许"""
        try:
            ip_addr = ipaddress.ip_address(client_ip)

            # 检查是否在任一允许的网络中
            for network in self.whitelisted_networks:
                if ip_addr in network:
                    return True

            return False
        except ValueError:
            return False