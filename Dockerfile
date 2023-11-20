# 使用 Python Slim 镜像作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

RUN echo "deb http://mirrors.ustc.edu.cn/debian/ buster main" > /etc/apt/sources.list \
    && echo "deb-src http://mirrors.ustc.edu.cn/debian/ buster main" >> /etc/apt/sources.list \
    && sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list \
    && sed -i 's/security.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list

# 安装 tzdata 包用于设置时区
RUN apt-get update && apt-get install -y tzdata

# 设置时区（例如，这里设置为亚洲/上海时区）
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 复制当前目录的内容到工作目录
COPY . /app

# 安装应用程序依赖（如果有requirements.txt文件）
RUN pip install --no-cache-dir -r requirements.txt

# 暴露应用程序的端口（如果需要）

# 启动应用程序
CMD ["python3", "main.py"]
