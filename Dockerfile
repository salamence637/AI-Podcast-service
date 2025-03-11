# 使用官方 Python 3.9 slim 版本
FROM python:3.9-slim

WORKDIR /app

# 复制依赖文件并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y ffmpeg

# 复制项目代码
COPY . .

# 暴露 FastAPI 默认端口
EXPOSE 8000

# 启动 FastAPI 服务
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
