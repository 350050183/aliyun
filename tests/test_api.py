"""
API 测试用例
用于验证接口功能是否正常
"""

import pytest
import json
from fastapi.testclient import TestClient
from main import app
from uuid import uuid4

# 创建测试客户端
client = TestClient(app)

# 测试用例使用的测试 IP
TEST_IP = "34.1.28.44"

class TestALBAPI:
    """ALB 访问控制 API 测试"""

    def test_add_entries_to_acl(self):
        """测试添加 ALB 访问控制条目"""
        test_acl_id = f"acl-test-{uuid4().hex[:8]}"
        test_ip = f"{TEST_IP}/32"

        response = client.post("/api/v1/alb/add-entries", json={
            "acl_id": test_acl_id,
            "source_cidr_ip": test_ip,
            "description": "测试添加 ALB 条目"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["acl_entry_ip"] == test_ip
        assert "添加成功" in data["message"]

    def test_remove_entries_from_acl(self):
        """测试删除 ALB 访问控制条目"""
        test_acl_id = f"acl-test-{uuid4().hex[:8]}"
        test_ip = f"{TEST_IP}/32"

        response = client.post("/api/v1/alb/remove-entries", json={
            "acl_id": test_acl_id,
            "source_cidr_ip": test_ip
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["acl_entry_ip"] == test_ip
        assert "删除成功" in data["message"]

    def test_alb_documentation(self):
        """测试 ALB API 文档接口"""
        response = client.get("/api/v1/alb/docs")

        assert response.status_code == 200
        data = response.json()

        assert "add_entries_to_acl" in data
        assert "remove_entries_from_acl" in data

        add_doc = data["add_entries_to_acl"]
        assert add_doc["title"] == "添加ALB访问控制条目"
        assert "addentriestoacl" in add_doc["url"]

        remove_doc = data["remove_entries_from_acl"]
        assert remove_doc["title"] == "删除ALB访问控制条目"
        assert "removeentriesfromacl" in remove_doc["url"]

class TestECSAPI:
    """ECS 安全组 API 测试"""

    def test_authorize_security_group(self):
        """测试添加 ECS 安全组规则"""
        test_security_group_id = f"sg-test-{uuid4().hex[:8]}"
        test_ip = f"{TEST_IP}/32"

        response = client.post("/api/v1/ecs/authorize", json={
            "source_cidr_ip": test_ip,
            "security_group_id": test_security_group_id,
            "description": "测试添加安全组规则",
            "policy": "Drop",
            "port_range": "22/22",
            "ip_protocol": "TCP"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["source_cidr_ip"] == test_ip
        assert test_security_group_id in data["security_group_id"]
        assert "添加成功" in data["message"]

    def test_revoke_security_group(self):
        """测试删除 ECS 安全组规则"""
        test_security_group_id = f"sg-test-{uuid4().hex[:8]}"
        test_ip = f"{TEST_IP}/32"

        response = client.post("/api/v1/ecs/revoke", json={
            "source_cidr_ip": test_ip,
            "security_group_id": test_security_group_id,
            "policy": "Drop",
            "port_range": "22/22",
            "ip_protocol": "TCP"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["source_cidr_ip"] == test_ip
        assert test_security_group_id in data["security_group_id"]
        assert "删除成功" in data["message"]

    def test_ecs_documentation(self):
        """测试 ECS 安全组 API 文档接口"""
        response = client.get("/api/v1/ecs/docs")

        assert response.status_code == 200
        data = response.json()

        assert "authorize_security_group" in data
        assert "revoke_security_group" in data

        auth_doc = data["authorize_security_group"]
        assert auth_doc["title"] == "添加ECS安全组入方向规则"
        assert "authorizesecuritygroup" in auth_doc["url"]

        revoke_doc = data["revoke_security_group"]
        assert revoke_doc["title"] == "删除ECS安全组入方向规则"
        assert "revokesecuritygroup" in revoke_doc["url"]

class TestHealthCheck:
    """健康检查接口测试"""

    def test_health_check(self):
        """测试健康检查接口"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "1.0.0"
        assert data["service"] == "aliyun-manager"

if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v"])