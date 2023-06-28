# 指定基础镜像
FROM python:3.9

# 设置工作目录
WORKDIR /app

# 定义环境变量来传递主控端地址和端口以及节点验证密钥
ENV CONTROLLER_HOST="主控端地址"
ENV CONTROLLER_PORT="主控端端口"
ENV NODEID_KEY="节点验证密钥"

# 将项目文件复制到容器中
COPY . /app

# 安装项目所需的依赖项
RUN pip install --no-cache-dir -r requirements.txt

# 定义入口命令或脚本
CMD ["python", "spider.py"]
