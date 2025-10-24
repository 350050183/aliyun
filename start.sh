#!/bin/bash

# Aliyun Manager 启动脚本
# 支持开发和生产环境

set -e

# 配置文件路径
ENV_FILE=".env.example"
DOCKER_COMPOSE_FILE="docker-compose.yml"

# 默认 Docker 标签
IMAGE_TAG="aliyun-manager:latest"

# 函数定义
print_usage() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help              显示此帮助信息"
    echo "  -d, --development       开发模式（启用热重载）"
    echo "  -p, --production        生产模式（默认）"
    echo "  -b, --build             强制重新构建镜像"
    echo "  -t, --test              运行测试"
    echo "  -r, --restart           重启服务"
    echo "  -s, --stop              停止服务"
    echo ""
    echo "示例:"
    echo "  $0                      启动生产环境"
    echo "  $0 -d                   启动开发环境"
    echo "  $0 -t                   运行测试"
    echo "  $0 -r                   重启服务"
}

check_requirements() {
    echo "检查系统要求..."

    # 检查 Docker 是否安装
    if ! command -v docker &> /dev/null; then
        echo "错误: 未找到 Docker，请先安装 Docker"
        exit 1
    fi

    # 检查 Docker Compose 是否安装
    if ! command -v docker compose &> /dev/null && ! command -v docker-compose &> /dev/null; then
        echo "错误: 未找到 Docker Compose，请先安装 Docker Compose"
        exit 1
    fi

    # 检查 .env 文件
    if [ ! -f ".env" ]; then
        echo "警告: 未找到 .env 文件，将使用 .env.example"
        if [ -f "$ENV_FILE" ]; then
            cp "$ENV_FILE" .env
            echo ".env 文件已创建，请根据需要修改配置"
        fi
    fi

    echo "系统要求检查完成 ✅"
}

build_image() {
    echo "构建 Docker 镜像..."
    docker compose build --no-cache 2>/dev/null || {
        echo "构建失败，尝试不使用缓存构建..."
        docker compose build --no-cache
    }
    echo "镜像构建完成 ✅"
}

start_service() {
    local mode=$1

    echo "启动 Aliyun Manager 服务..."

    if [ "$mode" = "development" ]; then
        echo "开发模式: 启用热重载和详细日志"
        # 开发模式配置可以在这里添加
    fi

    # 启动服务
    docker compose up -d

    # 等待服务启动
    echo "等待服务启动..."
    sleep 5

    # 检查服务健康状态
    if curl -f http://localhost:6060/health &> /dev/null; then
        echo "服务启动成功 ✅"
        echo "访问地址: http://localhost:6060"
        echo "API 文档: http://localhost:6060/docs"
        echo "健康检查: http://localhost:6060/health"
    else
        echo "服务启动失败 ❌"
        echo "请检查日志: docker compose logs"
        exit 1
    fi
}

run_tests() {
    echo "运行测试..."

    # 构建测试镜像
    docker compose build

    # 运行测试容器
    docker compose run --rm aliyun-manager python -m pytest tests/ -v

    echo "测试完成 ✅"
}

stop_service() {
    echo "停止服务..."
    docker compose down
    echo "服务已停止 ✅"
}

restart_service() {
    echo "重启服务..."
    docker compose restart
    echo "服务已重启 ✅"
}

# 主程序逻辑
main() {
    local mode="production"
    local force_build=false
    local action="start"

    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                print_usage
                exit 0
                ;;
            -d|--development)
                mode="development"
                shift
                ;;
            -p|--production)
                mode="production"
                shift
                ;;
            -b|--build)
                force_build=true
                shift
                ;;
            -t|--test)
                action="test"
                shift
                ;;
            -r|--restart)
                action="restart"
                shift
                ;;
            -s|--stop)
                action="stop"
                shift
                ;;
            *)
                echo "未知选项: $1"
                print_usage
                exit 1
                ;;
        esac
    done

    # 执行相应操作
    case $action in
        "test")
            check_requirements
            run_tests
            ;;
        "stop")
            stop_service
            ;;
        "restart")
            restart_service
            ;;
        *)
            check_requirements

            if [ "$force_build" = true ]; then
                build_image
            fi

            start_service "$mode"
            ;;
    esac
}

# 运行主程序
main "$@"