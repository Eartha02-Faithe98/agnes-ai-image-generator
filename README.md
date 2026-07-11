# Agnes AI 圖片生成工具 (Agnes AI Image Generator)

一個使用 Python 呼叫 **Agnes AI** 圖片生成服務的工具。本專案與 OpenAI API 格式完全相容，並提供兩種簡便的實作方式。

---

## 🎨 專案特點
- **雙方案支援**：提供 `requests` 直接呼叫（適合輕量整合）與 `OpenAI SDK` 封裝（適合現有 OpenAI 專案遷移）兩種版本。
- **安全的憑證管理**：使用 `.env` 檔案管理 API 金鑰，避免金鑰外洩。
- **強大的命令列介面**：支援自訂提示詞、模型選擇、輸出尺寸、生成數量，並能自動下載圖片至本地。
- **Windows 相容修正**：內建解決 Windows CMD `cp950` 編碼無法正常顯示 Unicode Emoji 的問題。

---

## 📂 專案結構
```text
agnes-ai-image-generator/
├── .env.example              # 環境變數範例檔
├── .env                      # 實際環境變數（包含 API Key，已被 Git 忽略）
├── .gitignore                # Git 忽略設定
├── requirements.txt          # Python 依賴清單
├── generate_image.py         # 主程式：使用 requests 直接呼叫 API (CLI 工具)
├── generate_image_openai_sdk.py # 方案二：使用 OpenAI SDK 呼叫 API
└── output/                   # 自動下載圖片後的本地儲存目錄
```

---

## 🚀 快速開始

### 1. 取得 API Key
請先至 [Agnes AI API Platform](https://platform.agnes-ai.com/) 註冊並取得您的 API Key。

### 2. 環境設定與安裝
在專案根目錄下執行以下指令以建立虛擬環境並安裝套件：

```cmd
# 建立虛擬環境
python -m venv .venv

# 啟用虛擬環境 (Windows)
.venv\Scripts\activate

# 安裝依賴套件
pip install -r requirements.txt
```
*(備註：如欲執行 `generate_image_openai_sdk.py`，請另外安裝官方 SDK：`pip install openai`)*

### 3. 設定環境變數
將 `.env.example` 複製並命名為 `.env`：
```cmd
copy .env.example .env
```
編輯 `.env` 檔案，填入您的 API Key：
```env
AGNES_API_KEY=sk-your_actual_api_key_here
```

---

## 💻 使用說明

### 方案一：使用 generate_image.py (命令列工具)

本工具已內建「Hello Kitty 台灣守護天使」的 16:9 插畫提示詞作為預設值。

```cmd
# 直接執行（使用預設 Hello Kitty 提示詞）
python generate_image.py

# 自訂提示詞
python generate_image.py --prompt "A futuristic city skyline at sunset"

# 自訂尺寸與模型
python generate_image.py --prompt "Abstract art" --size 1024x768 --model agnes-image-2.1-flash

# 一次生成多張圖片
python generate_image.py --prompt "Cute cartoon cat" --n 2

# 只取得雲端 URL，不自動下載到本地
python generate_image.py --prompt "Sunset" --no-download
```

### 方案二：使用 generate_image_openai_sdk.py (OpenAI SDK)

Agnes AI 的 API 接口與 OpenAI 完全相容。只需將 `base_url` 重新導向至 Agnes AI 即可：

```python
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_AGNES_API_KEY",
    base_url="https://apihub.agnes-ai.com/v1"  # 指向 Agnes AI Hub
)

response = client.images.generate(
    model="agnes-image-2.1-flash",
    prompt="A beautiful sunset",
    size="1024x768",
    n=1
)

print("圖片 URL:", response.data[0].url)
```

---

## 🛠️ API 規格說明

- **Base URL**: `https://apihub.agnes-ai.com/v1`
- **圖片生成端點**: `POST /images/generations`
- **認證方式**: Bearer Token (`Authorization: Bearer <API_KEY>`)
- **支援模型**:
  - `agnes-image-2.1-flash` (推薦，文字生成圖片效果極佳)
  - `agnes-image-2.0-flash` (適合圖生圖場景)
- **支援尺寸**: `512x512`, `768x1024`, `1024x768` (16:9), `1024x1024`

---

## 🔒 安全性備忘
- 請勿將 `.env` 檔案提交至 Git。
- 請勿在程式碼中硬編碼 (Hardcode) 您的 API 金鑰。
- 本專案預設已透過 `.gitignore` 排除敏感資訊，可放心開發與協作。
