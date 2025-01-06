# Word 文件文字替換工具

這是一個 Python 工具，用於操作 Microsoft Word 文件，主要功能是在保持原始格式的同時替換文件中的文字。

## 功能特點

- 在保持格式的同時替換 Word 文件中的文字
- 支持批量處理文件
- 安全的臨時文件處理機制
- 可自定義的文字替換映射

## 系統需求

- Python 3.x
- 必需的 Python 套件（通過 pip 安裝）：
  ```
  python-docx
  pywin32
  ```

## 安裝說明

1. 克隆此倉庫或下載源代碼
2. 安裝必需的套件：
   ```bash
   pip install -r requirements.txt
   ```

## 專案結構

- `main.py`: 文字替換的核心功能
- `convert.py`: 文件轉換工具
- `data_storage.py`: 數據處理和存儲操作
- `test_main.py`: 主要功能的測試用例

## 使用方法

```python
from main import replace_text_within_percent_signs

# 使用範例
replace_dict = {
    "舊文字": "新文字",
    "佔位符": "替換文字"
}

replace_text_within_percent_signs("文件路徑/document.docx", replace_dict, "輸出資料夾")
```

## 主要特性

- 百分號(%)之間的文字替換
- 安全的文件處理機制，包含臨時文件處理
- 保持原始文件格式
- 錯誤處理和備份創建

## 參與貢獻

歡迎提交問題和功能改進建議！

## 授權條款

本專案採用 MIT 授權條款 - 詳情請見 LICENSE 文件。

## 聯絡方式

如有任何問題或疑慮，請在專案倉庫中開啟一個問題單（Issue）。
