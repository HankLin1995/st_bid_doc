#FROM python:3.11-slim

#WORKDIR /app

#COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt

#COPY . .

#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


FROM python:3.11-slim

WORKDIR /app

# 安裝 ca-certificates，確保 HTTPS 可以驗證
#RUN apt-get update && apt-get install -y --no-install-recommends \
#        ca-certificates \
#        curl \
#    && update-ca-certificates \
#    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt
COPY requirements.txt .

# 環境變數：延長 pip timeout，防止 M4 容器因網路慢 timeout
#ENV PIP_DEFAULT_TIMEOUT=120
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# 安裝套件
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼
COPY . .

# CMD 使用 JSON 陣列，並先檢查 TLS 1.2 再啟動 uvicorn
#CMD ["sh", "-c", "python -c \"import ssl, http.client; ctx = ssl.create_default_context(); ctx.minimum_version = ssl.TLSVersion.TLSv1_2; ctx.maximum_version = ssl.TLSVersion.TLSv1_2; conn = http.client.HTTPSConnection('pypi.org', context=ctx); conn.request('GET', '/'); r = conn.getresponse(); print('TLS 1.2 check: status', r.status, 'reason:', r.reason)\" && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
