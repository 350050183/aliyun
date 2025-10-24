# 简化版 Dockerfile - 最小化配置
FROM python:3.9-slim

# 安装依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# 创建非 root 用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 创建应用目录
WORKDIR /app

# 创建 logs 目录并设置正确权限
RUN mkdir -p logs && chown appuser:appuser logs

# 安装 Python 依赖（使用默认源）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 6060

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:6060/health || exit 1

# 注释掉非root用户切换，先用root用户测试
# USER appuser

# 启动应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "6060"]