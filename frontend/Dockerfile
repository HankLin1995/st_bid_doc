#FROM python:3.11-slim

#WORKDIR /app

#COPY requirements.txt .

#RUN pip install --no-cache-dir -r requirements.txt

#COPY . .

#EXPOSE 8501

#ENTRYPOINT ["streamlit", "run", "streamlit_app.py"]

FROM python:3.11-slim

WORKDIR /app

# 安裝 ca-certificates 以確保 HTTPS 正常
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt
COPY requirements.txt .

# 延長 pip timeout，使用清華 PyPI 鏡像避免網路慢
ENV PIP_DEFAULT_TIMEOUT=120
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# 安裝套件
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼
COPY . .

# Streamlit 預設埠 8501
EXPOSE 8501

# 使用 JSON 陣列 ENTRYPOINT，確保信號能正確傳遞
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]

