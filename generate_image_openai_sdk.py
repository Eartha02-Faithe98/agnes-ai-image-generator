"""
Agnes AI 圖片生成 — 使用 OpenAI SDK 的替代方案
================================================
因為 Agnes AI 的 API 與 OpenAI 完全相容，
所以你也可以直接使用 openai 官方 Python SDK 來呼叫！

只需要把 base_url 改為 Agnes AI 的端點即可。

依賴套件：
    pip install openai python-dotenv
"""

import os
import sys
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("❌ 缺少 openai 套件，請執行：pip install openai")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("❌ 缺少 python-dotenv 套件，請執行：pip install python-dotenv")
    sys.exit(1)


def main():
    # 載入環境變數
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path)

    api_key = os.getenv("AGNES_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("❌ 請先在 .env 中設定 AGNES_API_KEY")
        sys.exit(1)

    # ── 關鍵：建立 OpenAI client，但指向 Agnes AI 的 Base URL ──
    # 這就是 "OpenAI 相容" 的意思：
    #   只要把 base_url 換成 Agnes AI 的端點，其他用法完全一樣！
    client = OpenAI(
        api_key=api_key,
        base_url="https://apihub.agnes-ai.com/v1",
    )

    # ── 預設提示詞（可在此直接修改） ──
    prompt = (
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

    print("🎨 使用 OpenAI SDK 呼叫 Agnes AI 生成圖片...")
    print(f"   提示: {prompt[:60]}...")
    print()

    response = client.images.generate(
        model="agnes-image-2.1-flash",  # Agnes AI 的圖片模型
        prompt=prompt,
        size="1024x768",
        n=1,
    )

    # ── 取得結果 ──
    image_url = response.data[0].url
    print(f"✅ 圖片生成成功！")
    print(f"📷 URL: {image_url}")
    print()
    print("💡 提示：你可以修改上方的 prompt 來生成不同的圖片")


if __name__ == "__main__":
    main()
