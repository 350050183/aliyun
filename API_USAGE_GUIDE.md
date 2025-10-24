# 阿里云云资源管理服务 API 使用指南

## 服务概述

阿里云云资源管理服务是一个基于 FastAPI 开发的 Web 服务，提供 ALB 访问控制和 ECS 安全组管理的 API 接口。该服务使用 Docker 容器化部署，支持多架构（arm64/amd64）。

### 服务信息
- **服务名称**: aliyun-manager
- **监听端口**: 8080
- **服务状态**: 运行中
- **版本**: 1.0.0

## API 接口列表

### ALB 访问控制接口

#### 1. 添加 ALB 访问控制条目
- **接口地址**: `POST /api/v1/alb/add-entries`
- **功能描述**: 向指定的 ALB ACL 中添加 IP 地址段访问控制规则
- **请求参数**:
  - `acl_id` (可选): 访问控制列表 ID，不提供时使用环境变量 `DEFAULT_ALB_ACL_ID`
  - `source_cidr_ip` (必填): 来源 IP 地址段，必须使用 CIDR 格式（如 192.168.1.0/24）
  - `description` (可选): 描述信息，不提供时自动生成时间戳

**请求示例**:
```json
{
  "source_cidr_ip": "192.168.1.100/32",
  "description": "服务器IP地址"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "添加 ALB 访问控制条目成功",
  "acl_entry_ip": "192.168.1.100",
  "description": "服务器IP地址",
  "acl_id": "acl-nnd9vclvwdcorsg1rm"
}
```

#### 2. 删除 ALB 访问控制条目
- **接口地址**: `POST /api/v1/alb/remove-entries`
- **功能描述**: 从指定的 ALB ACL 中删除 IP 地址段访问控制规则
- **请求参数**:
  - `acl_id` (可选): 访问控制列表 ID
  - `source_cidr_ip` (必填): 要删除的 IP 地址段

**请求示例**:
```json
{
  "source_cidr_ip": "192.168.1.100/32"
}
```

### ECS 安全组接口

#### 1. 添加 ECS 安全组规则
- **接口地址**: `POST /api/v1/ecs/authorize`
- **功能描述**: 向指定安全组添加入方向访问规则
- **请求参数**:
  - `security_group_id` (可选): 安全组 ID，不提供时使用环境变量 `DEFAULT_SECURITY_GROUP_ID`
  - `source_cidr_ip` (必填): 来源 IP 地址段（CIDR 格式）
  - `description` (可选): 描述信息
  - `policy` (可选): 访问策略，默认 "Drop"
  - `port_range` (可选): 端口范围，默认 "-1/-1"
  - `ip_protocol` (可选): 协议类型，默认 "ALL"

**请求示例**:
```json
{
  "source_cidr_ip": "192.168.1.100/32",
  "description": "允许SSH访问",
  "policy": "Accept",
  "port_range": "22/22",
  "ip_protocol": "TCP"
}
```

#### 2. 删除 ECS 安全组规则
- **接口地址**: `POST /api/v1/ecs/revoke`
- **功能描述**: 从指定安全组删除入方向访问规则
- **重要提示**: 删除规则时，所有参数必须与添加规则时完全一致

**请求示例**:
```json
{
  "source_cidr_ip": "192.168.1.100/32",
  "policy": "Accept",
  "port_range": "22/22",
  "ip_protocol": "TCP"
}
```

## 参数格式要求

### IP 地址格式
- 所有 IP 地址必须使用 CIDR 格式
- 单个 IP: `192.168.1.100/32`
- IP 段: `192.168.1.0/24`
- 错误格式: `192.168.1.100` (缺少 CIDR 后缀)

### 协议类型格式
- 必须使用大写字母
- 支持: `TCP`, `UDP`, `ICMP`, `ALL`
- 错误格式: `tcp`, `all`, `Tcp`

### 端口范围格式
- 格式: `起始端口/结束端口`
- 单端口: `22/22`
- 端口范围: `80/443`
- 全端口: `-1/-1`
- 错误格式: `22`, `1/65535`

## 环境变量配置

```bash
# 阿里云访问凭证
ACCESS_KEY_ID=your_access_key_id
ACCESS_KEY_SECRET=your_access_key_secret

# 默认资源配置
DEFAULT_SECURITY_GROUP_ID=sg-bp19nke7purenpearpmb
DEFAULT_ALB_ACL_ID=acl-nnd9vclvwdcorsg1rm

# 日志配置
LOG_LEVEL=INFO
```

## 使用示例

### 快速测试
使用示例IP进行接口功能验证：

1. **添加 ALB 规则**:
```bash
curl -X POST "http://localhost:6060/api/v1/alb/add-entries" \
  -H "Content-Type: application/json" \
  -d '{"source_cidr_ip": "192.168.1.100/32", "description": "测试IP"}'
```

2. **添加 ECS 安全组规则**:
```bash
curl -X POST "http://localhost:6060/api/v1/ecs/authorize" \
  -H "Content-Type: application/json" \
  -d '{
    "source_cidr_ip": "192.168.1.100/32",
    "description": "测试SSH访问",
    "policy": "Accept",
    "port_range": "22/22",
    "ip_protocol": "TCP"
  }'
```

### 删除操作
使用相同的 IP 进行删除测试：
```bash
curl -X POST "http://localhost:6060/api/v1/alb/remove-entries" \
  -H "Content-Type: application/json" \
  -d '{"source_cidr_ip": "192.168.1.100/32"}'
```

## 文档接口

- **API 文档汇总**: `GET /api/docs`
- **ALB 文档**: `GET /api/v1/alb/docs`
- **ECS 文档**: `GET /api/v1/ecs/docs`
- **ALB 使用示例**: `GET /api/v1/alb/examples`
- **ECS 使用示例**: `GET /api/v1/ecs/examples`

## 错误处理

### 常见错误类型
- **IP 格式错误**: 参数验证失败，返回 422 状态码
- **网络连接错误**: 阿里云 API 连接失败
- **权限错误**: 访问密钥无效或权限不足
- **参数不匹配**: 删除规则时参数与添加时不一致

### 错误响应格式
```json
{
  "error": "错误类型",
  "detail": "错误详情",
  "timestamp": "错误发生时间"
}
```

## 开发和部署

### Docker 部署
```bash
# 构建镜像
docker build -t aliyun-manager .

# 运行容器
docker run -d \
  -p 6060:6060 \
  --env-file .env \
  --name aliyun-manager \
  aliyun-manager
```

### Docker Compose 部署
```bash
docker compose up -d
```

### 开发模式
使用目录挂载进行开发：
```bash
docker compose up --build -d
```

## 技术栈

- **Web 框架**: FastAPI
- **容器化**: Docker
- **云服务**: 阿里云 ALB 和 ECS
- **开发语言**: Python 3.9
- **依赖管理**: pip

本指南持续更新，如有问题请联系开发团队。