"""
Agnes AI 圖片生成工具
=====================
使用 Agnes AI API (OpenAI 相容格式) 進行文字轉圖片 (Text-to-Image) 生成。

API 基礎資訊：
- Base URL: https://apihub.agnes-ai.com/v1
- Endpoint: /images/generations
- 支援模型: agnes-image-2.0-flash, agnes-image-2.1-flash
- 認證方式: Bearer Token

使用前請確認：
1. 已在 https://platform.agnes-ai.com/ 註冊並取得 API Key
2. 已建立 .env 檔並填入 AGNES_API_KEY

依賴套件：
    pip install requests python-dotenv
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path

# ── Windows 終端機 UTF-8 相容性修正 ──
# Windows CMD 預設使用 cp950 (Big5)，無法顯示 emoji 和部分 Unicode 字元。
# 這段程式碼將 stdout/stderr 重新設定為 UTF-8，並允許無法顯示的字元用 '?' 替代。
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


try:
    import requests
except ImportError:
    print("❌ 缺少 requests 套件，請執行：pip install requests")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("❌ 缺少 python-dotenv 套件，請執行：pip install python-dotenv")
    sys.exit(1)


# ──────────────────────────────────────────────
# 常數定義
# ──────────────────────────────────────────────
BASE_URL = "https://apihub.agnes-ai.com/v1"
IMAGE_ENDPOINT = f"{BASE_URL}/images/generations"

# Agnes AI 支援的圖片生成模型
AVAILABLE_MODELS = [
    "agnes-image-2.0-flash",
    "agnes-image-2.1-flash",  # 推薦使用
]

# 支援的圖片尺寸
AVAILABLE_SIZES = [
    "512x512",
    "768x1024",
    "1024x768",
    "1024x1024",
]

# 預設設定
DEFAULT_MODEL = "agnes-image-2.1-flash"
DEFAULT_SIZE = "1024x768"
DEFAULT_N = 1
OUTPUT_DIR = Path(__file__).parent / "output"


def load_api_key() -> str:
    """
    從 .env 檔案載入 API Key。

    為什麼用 .env 而不是直接寫在程式碼裡？
    → 避免 API Key 被提交到 Git，這是資安最佳實踐。
    """
    # 載入專案根目錄的 .env 檔案
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path)

    api_key = os.getenv("AGNES_API_KEY")

    if not api_key or api_key == "your_api_key_here":
        print("❌ 找不到有效的 API Key！")
        print()
        print("請依照以下步驟設定：")
        print("  1. 複製 .env.example 為 .env")
        print("  2. 在 .env 中填入你的 Agnes AI API Key")
        print("  3. API Key 可在 https://platform.agnes-ai.com/ 取得")
        sys.exit(1)

    return api_key


def generate_image(
    prompt: str,
    model: str = DEFAULT_MODEL,
    size: str = DEFAULT_SIZE,
    n: int = DEFAULT_N,
    api_key: str | None = None,
) -> dict:
    """
    呼叫 Agnes AI API 生成圖片。

    參數說明：
        prompt (str): 圖片描述文字（英文效果較佳）
        model (str): 使用的模型名稱
            - agnes-image-2.1-flash（推薦，高品質文字轉圖片）
            - agnes-image-2.0-flash（適合圖生圖場景）
        size (str): 圖片尺寸，例如 "1024x1024"
        n (int): 一次生成幾張圖片
        api_key (str): API 金鑰，若為 None 則從 .env 載入

    回傳：
        dict: API 回應的 JSON，包含圖片 URL 等資訊

    為什麼使用 OpenAI 相容格式？
    → Agnes AI 的 API 設計與 OpenAI 相容，這表示：
       1. 可以直接使用 openai Python SDK（換 base_url 即可）
       2. 回傳格式與 OpenAI 一致，容易整合到現有專案
    """
    if api_key is None:
        api_key = load_api_key()

    # 組裝請求標頭（Bearer Token 認證）
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # 組裝請求內容
    payload = {
        "model": model,
        "prompt": prompt,
        "n": n,
        "size": size,
    }

    print(f"🎨 正在生成圖片...")
    print(f"   模型: {model}")
    print(f"   尺寸: {size}")
    print(f"   數量: {n}")
    print(f"   提示: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
    print()

    try:
        response = requests.post(
            IMAGE_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=120,  # 圖片生成可能需要較長時間
        )

        # 檢查 HTTP 狀態碼
        response.raise_for_status()

        result = response.json()
        return result

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else "未知"
        error_body = ""
        try:
            error_body = e.response.json()
        except Exception:
            error_body = e.response.text if e.response else ""

        print(f"❌ API 請求失敗 (HTTP {status_code})")
        print(f"   錯誤詳情: {error_body}")

        if status_code == 401:
            print("   → API Key 無效或已過期，請重新確認")
        elif status_code == 429:
            print("   → 請求頻率過高，請稍後再試")
        elif status_code == 402:
            print("   → 額度不足，請至 platform.agnes-ai.com 查看餘額")

        sys.exit(1)

    except requests.exceptions.ConnectionError:
        print("❌ 無法連線到 Agnes AI API，請檢查網路連線")
        sys.exit(1)

    except requests.exceptions.Timeout:
        print("❌ 請求逾時（超過 120 秒），請稍後再試")
        sys.exit(1)


def download_image(url: str, save_path: Path) -> Path:
    """
    下載圖片並儲存到本地。

    參數：
        url (str): 圖片的 URL
        save_path (Path): 儲存路徑

    回傳：
        Path: 實際儲存的檔案路徑
    """
    response = requests.get(url, timeout=60)
    response.raise_for_status()

    # 確保輸出目錄存在
    save_path.parent.mkdir(parents=True, exist_ok=True)

    with open(save_path, "wb") as f:
        f.write(response.content)

    return save_path


def main():
    """
    命令列入口點。

    使用範例：
        # 直接執行（使用預設提示詞）
        python generate_image.py

        # 自訂提示詞
        python generate_image.py --prompt "A cute cat sitting on a rainbow"

        # 指定模型和尺寸
        python generate_image.py --prompt "A futuristic city" --model agnes-image-2.1-flash --size 1024x768

        # 一次生成多張
        python generate_image.py --prompt "Abstract art" --n 2

        # 不自動下載，只取得 URL
        python generate_image.py --prompt "Sunset" --no-download
    """
    # ── 預設提示詞（可在此直接修改） ──
    default_prompt = (
        "一幅 16:9 的 Hello Kitty 風格插畫，展示 Hello Kitty 作為一個守護天使。"
        "她穿著一件點綴著藍色蝴蝶結的精緻粉色雨衣，頭戴一頂帶有更大蝴蝶結和翅膀的可愛帽子。"
        "她站在一個被颱風包圍的台灣島的微縮立體模型上方，但一切都顯得安全。"
        "她用一把巨大的、透明的傘覆蓋著台灣，這把傘發出柔和的金色光芒，形成一個保護圓頂。"
        "外面，程式化且可愛的風暴雲和雨點被這個圓頂彈開。"
        "在圓頂內，微小的、微笑的台灣村莊和人民在安全中閃耀。"
        "在背景的風暴天空中，出現了以下繁體中文創意祝福："
        "『風雨無憂，吉蒂守護，願台灣永保平安』。"
        "這些文字看起來像是由光點組成，並帶有小小的星星和蝴蝶結裝飾。"
        "整個場景充滿溫暖、舒適和安全的感覺，使用乾淨的線條、豐富的粉彩和 Sanrio 特有的可愛美學。"
    )

    parser = argparse.ArgumentParser(
        description="Agnes AI 圖片生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例：
  python generate_image.py
  python generate_image.py --prompt "A cute cat sitting on a rainbow"
  python generate_image.py --prompt "A futuristic city" --model agnes-image-2.1-flash --size 1024x768
  python generate_image.py --prompt "Abstract art" --n 2
  python generate_image.py --prompt "Sunset" --no-download
        """,
    )

    parser.add_argument(
        "--prompt",
        type=str,
        default=default_prompt,
        help="圖片描述文字（未指定則使用預設提示詞）",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        choices=AVAILABLE_MODELS,
        help=f"使用的模型（預設: {DEFAULT_MODEL}）",
    )
    parser.add_argument(
        "--size",
        type=str,
        default=DEFAULT_SIZE,
        choices=AVAILABLE_SIZES,
        help=f"圖片尺寸（預設: {DEFAULT_SIZE}）",
    )
    parser.add_argument(
        "--n",
        type=int,
        default=DEFAULT_N,
        help=f"生成數量（預設: {DEFAULT_N}）",
    )
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="不自動下載圖片，僅顯示 URL",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(OUTPUT_DIR),
        help=f"圖片儲存目錄（預設: {OUTPUT_DIR}）",
    )

    args = parser.parse_args()

    # ── 執行圖片生成 ──
    result = generate_image(
        prompt=args.prompt,
        model=args.model,
        size=args.size,
        n=args.n,
    )

    # ── 處理回傳結果 ──
    images = result.get("data", [])

    if not images:
        print("⚠️  API 回傳成功但沒有圖片資料")
        print(f"   完整回應: {json.dumps(result, indent=2, ensure_ascii=False)}")
        sys.exit(1)

    print(f"✅ 成功生成 {len(images)} 張圖片！")
    print()

    for i, img_data in enumerate(images, start=1):
        # Agnes AI 回傳格式可能是 url 或 b64_json
        image_url = img_data.get("url")
        b64_data = img_data.get("b64_json")

        if image_url:
            print(f"  📷 圖片 {i}: {image_url}")

            # 自動下載到本地
            if not args.no_download:
                output_path = Path(args.output_dir)
                timestamp = int(time.time())
                filename = f"agnes_{timestamp}_{i}.png"
                save_path = output_path / filename

                try:
                    saved = download_image(image_url, save_path)
                    print(f"     💾 已儲存: {saved}")
                except Exception as e:
                    print(f"     ⚠️  下載失敗: {e}")

        elif b64_data:
            # 若回傳 base64 編碼的圖片
            import base64

            output_path = Path(args.output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            timestamp = int(time.time())
            filename = f"agnes_{timestamp}_{i}.png"
            save_path = output_path / filename

            with open(save_path, "wb") as f:
                f.write(base64.b64decode(b64_data))

            print(f"  📷 圖片 {i} (base64): 已儲存至 {save_path}")

    print()
    print("🎉 完成！")


if __name__ == "__main__":
    main()
