# 使用 Node.js 官方镜像作为基础镜像
FROM node:18-alpine

# 设置环境变量以运行 Next.js 生产模式
ENV NODE_ENV=production

# 设置工作目录
WORKDIR /app/client

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# 安装依赖，忽略开发依赖
RUN npm install

# 复制项目文件
COPY . .

# 构建项目
RUN npm run build

# 暴露端口以便 Nginx 代理
EXPOSE 3000

# 启动应用
CMD ["npm", "start"]
