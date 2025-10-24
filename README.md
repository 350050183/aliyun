# 阿里云云资源管理服务部署文档

## 项目概述

本项目是一个基于 Docker Compose 和 FastAPI 的阿里云资源管理服务，提供 ALB 访问控制和 ECS 安全组管理的 API 接口。

## 功能特性

- ✅ API 安全保护（IP 白名单验证）
- ✅ 完整的请求日志记录
- ✅ 健康检查和监控
- ✅ 支持多架构（arm64/amd64）
- ✅ 容器化部署
- ✅ OpenAPI 文档自动生成

## 快速开始

### 1. 环境准备

确保已安装：
- Docker 20.10+
- Docker Compose 2.0+

### 2. 配置环境变量

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑 .env 文件，配置阿里云 AK/SK
ACCESS_KEY_ID=your_access_key_id
ACCESS_KEY_SECRET=your_access_key_secret
```

### 3. 启动服务

```bash
# 生产模式启动
./start.sh

# 开发模式启动（启用热重载）
./start.sh -d

# 重新构建并启动
./start.sh -b
```

### 4. 验证服务

```bash
# 检查服务状态
curl http://localhost:6060/health

# 访问 API 文档
open http://localhost:6060/docs
```

## API 接口文档

### 健康检查
- `GET /health` - 服务健康状态检查

### 访问控制
- `POST /api/v1/banip/ban`
- `POST /api/v1/banip/unban`

### ALB 访问控制
- `GET /api/v1/alb/docs` - ALB API 文档
- `POST /api/v1/alb/add-entries` - 添加访问控制条目
- `POST /api/v1/alb/remove-entries` - 删除访问控制条目

### ECS 安全组
- `GET /api/v1/ecs/docs` - ECS API 文档
- `POST /api/v1/ecs/authorize` - 添加安全组规则
- `POST /api/v1/ecs/revoke` - 删除安全组规则

## 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| ACCESS_KEY_ID |  | 阿里云 Access Key ID |
| ACCESS_KEY_SECRET |  | 阿里云 Access Key Secret |
| DEFAULT_REGION | cn-hangzhou | 默认地区 |
| DEFAULT_SECURITY_GROUP_ID | 1111 | 默认安全组 ID |
| LOG_LEVEL | INFO | 日志级别 |
| WHITELIST_IPS |  | 白名单 IP 列表 |

### 白名单配置

白名单支持以下格式：
- 单个 IP：`192.168.1.1`
- CIDR 表示：`192.168.1.0/24`

配置示例：
```bash
WHITELIST_IPS=100.127.0.0/16,172.0.0.0/24,120.26.104.119
```

## 测试

```bash
# 运行单元测试
./start.sh -t

# 或者进入容器运行测试
docker compose exec aliyun-manager python -m pytest tests/ -v
```

## 日志管理

```bash
# 查看容器日志
docker compose logs -f

# 查看应用日志文件
docker compose exec aliyun-manager tail -f logs/app.log
```

## 常用操作

```bash
# 重启服务
./start.sh -r

# 停止服务
./start.sh -s

# 查看容器状态
docker compose ps

# 清理所有容器和镜像
docker compose down -v --rmi all
```

## 故障排除

### 服务无法启动

1. 检查 Docker 是否正常运行
2. 检查端口 6060 是否被占用
3. 查看容器日志：`docker compose logs`

### API 调用失败

1. 检查 AK/SK 配置是否正确
2. 检查 IP 是否在白名单中
3. 查看请求日志：`docker compose logs aliyun-manager`

### 网络连接问题

确保容器网络配置正确：
```bash
docker network ls | grep aliyun
```

## 安全建议

1. **使用环境变量**：避免在代码中硬编码 AK/SK
2. **IP 白名单**：仅允许必要的 IP 访问
3. **定期轮换**：定期更新 AK/SK
4. **最小权限**：使用具有最小必要权限的 RAM 用户
5. **HTTPS 访问**：在生产环境中使用 HTTPS

## 更新日志

- v1.0.0 (2024-10-24)
  - 初始版本发布
  - 支持 ALB 访问控制管理
  - 支持 ECS 安全组管理
  - 完整的 IP 白名单保护
  - 多架构容器支持

## 技术支持

如有问题，请检查：
1. 项目 README 文档
2. 容器日志输出
3. API 响应错误信息

测试 IP：34.1.28.44