FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --quiet --no-cache-dir \
    fastapi==0.109.2 \
    uvicorn==0.27.1 \
    pydantic==2.6.1 \
    click==8.1.7 \
    requests==2.31.0 \
    pytest==8.0.0 \
    pytest-cov==4.1.0 \
    PyYAML==6.0.1
COPY . .
RUN pip install --quiet --no-cache-dir -e .
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7890", "--loop", "asyncio"]
