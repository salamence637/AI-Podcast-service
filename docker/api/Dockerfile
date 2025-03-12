# 使用官方 Python 3.12 slim 版本
FROM python:3.12-slim

WORKDIR /app

# 复制依赖文件并安装依赖
COPY ./api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y ffmpeg

# 复制项目代码
COPY ./api .


ENTRYPOINT [ "./scripts/start.sh" ]

