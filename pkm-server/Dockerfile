# Business image - based on pre-built base image
# Fast rebuild when only code changes

FROM ghcr.io/eviljoker/pkm:base-latest

# 复制业务代码并安装
COPY . .
RUN pip install --quiet --no-cache-dir -e .
RUN pip install --quiet --no-cache-dir pytest pytest-cov

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7890", "--loop", "asyncio"]
