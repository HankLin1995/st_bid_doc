# Backend API 測試文件

## 概述

本測試套件使用 Docker 容器化環境來測試 FastAPI 後端 API，確保所有端點正常運作。

## 測試內容

### 1. 專案管理測試
- ✅ 創建專案
- ✅ 創建重複專案編號（應失敗）
- ✅ 讀取專案列表
- ✅ 根據專案編號讀取專案
- ✅ 讀取不存在的專案（應返回404）
- ✅ 更新專案狀態
- ✅ 刪除專案

### 2. PDF檔案上傳測試
- ✅ 上傳生態檢核PDF（檔名格式：年度-工程名稱_生態檢核.pdf）
- ✅ 上傳碳排計算PDF（檔名格式：年度-工程名稱_碳排計算.pdf）
- ✅ 上傳非PDF檔案（應失敗）
- ✅ 上傳無效的PDF類型（應失敗）
- ✅ 檢查PDF檔案是否存在
- ✅ 檢查不存在的PDF

### 3. 計畫管理測試
- ✅ 創建計畫
- ✅ 讀取計畫列表
- ✅ 刪除計畫

## 執行測試

### Windows 系統

```bash
# 方法1: 使用批次檔
run_tests.bat

# 方法2: 使用 docker-compose
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
docker-compose -f docker-compose.test.yml down
```

### Linux/Mac 系統

```bash
# 方法1: 使用 shell 腳本
chmod +x run_tests.sh
./run_tests.sh

# 方法2: 使用 docker-compose
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
docker-compose -f docker-compose.test.yml down
```

## 測試環境

- **Python**: 3.11
- **測試框架**: pytest
- **HTTP客戶端**: httpx (FastAPI TestClient)
- **資料庫**: SQLite (測試用臨時資料庫)
- **容器化**: Docker

## 測試檔案結構

```
backend/
├── tests/
│   ├── __init__.py
│   ├── test_api.py          # API端點測試
│   └── README.md            # 本文件
├── Dockerfile.test          # 測試用 Dockerfile
├── docker-compose.test.yml  # 測試用 Docker Compose
├── run_tests.sh            # Linux/Mac 測試腳本
└── run_tests.bat           # Windows 測試腳本
```

## 測試結果

測試結果會以 JUnit XML 格式輸出到 `/app/test-results/junit.xml`，可用於 CI/CD 整合。

## 新增測試

要新增測試，請在 `tests/test_api.py` 中添加新的測試函數：

```python
def test_your_new_feature():
    """測試描述"""
    response = client.get("/your-endpoint")
    assert response.status_code == 200
    # 更多斷言...
```

## 注意事項

1. 每個測試執行前後會自動清理資料庫
2. PDF檔案會儲存在 `../data/pdfs/` 目錄
3. 測試使用獨立的測試資料庫，不會影響生產環境
4. 檔案命名格式已更新為：`年度-工程名稱_PDF類型.pdf`

## 常見問題

### Q: 測試失敗怎麼辦？
A: 查看詳細的錯誤訊息，使用 `-v` 參數可以看到更詳細的輸出。

### Q: 如何只執行特定測試？
A: 使用 pytest 的 `-k` 參數：
```bash
docker-compose -f docker-compose.test.yml run backend-test pytest tests/ -k "test_upload"
```

### Q: 如何查看測試覆蓋率？
A: 安裝 pytest-cov 並執行：
```bash
pytest tests/ --cov=. --cov-report=html
```
