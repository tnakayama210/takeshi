#!/usr/bin/env python3
"""第2話のサムネイル（note見出し画像 1280x670）を生成する。

背景画像の生成元は次の順で選ぶ:
  1. OPENAI_API_KEY があれば OpenAI (DALL-E 3)
  2. GEMINI_API_KEY があれば Google Gemini API (gemini-2.5-flash-image)
  3. どちらも無い / 失敗した場合は Pillow で水彩風の背景をローカル描画（フォールバック）

その上に Pillow でタイトルとキャッチコピーを合成して thumbnail_ep2.png を出力する。

使い方:
  python generate_thumbnail_ep2.py [--out thumbnail_ep2.png] [--offline]
"""
import argparse
import base64
import io
import math
import os
import random
import sys
import urllib.request

from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH, HEIGHT = 1280, 670

IMAGE_PROMPT = (
    "A bright, cheerful Japanese kindergarten playground with three little young "
    "sisters playing cheerfully in the sunny morning. Modern warm watercolor "
    "illustration style, energetic and peaceful family atmosphere, 16:9 aspect ratio. "
    "No text, no letters, no watermark."
)
TITLE_LINE1 = "『3人の娘（双子含む）を育てた父の19年』"
TITLE_LINE2 = "【第2話】"
CATCH_COPY = "毎朝の通園バトルと、たくましく育った幼稚園期"

FONT_CANDIDATES = [
    os.environ.get("THUMBNAIL_FONT", ""),
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
    "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",  # macOS
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "C:/Windows/Fonts/meiryob.ttc",  # Windows
    "C:/Windows/Fonts/YuGothB.ttc",
]


# ---------------------------------------------------------------- 背景生成
def generate_with_openai() -> Image.Image:
    from openai import OpenAI

    client = OpenAI()
    res = client.images.generate(
        model="dall-e-3",
        prompt=IMAGE_PROMPT,
        size="1792x1024",
        quality="hd",
        n=1,
        response_format="b64_json",
    )
    return Image.open(io.BytesIO(base64.b64decode(res.data[0].b64_json))).convert("RGB")


def generate_with_gemini() -> Image.Image:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    model = os.environ.get("GEMINI_FLASH_IMAGE_MODEL", "gemini-2.5-flash-image")
    res = client.models.generate_content(
        model=model,
        contents=IMAGE_PROMPT,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="16:9"),
        ),
    )
    for part in res.candidates[0].content.parts:
        if part.inline_data and part.inline_data.data:
            return Image.open(io.BytesIO(part.inline_data.data)).convert("RGB")
    raise RuntimeError("Gemini から画像が返りませんでした")


def generate_fallback() -> Image.Image:
    """API が使えない場合の水彩風背景（朝の園庭：空・太陽・丘・3人のシルエット）。"""
    rnd = random.Random(2)
    img = Image.new("RGB", (WIDTH, HEIGHT))
    d = ImageDraw.Draw(img)
    # 空のグラデーション
    for y in range(HEIGHT):
        t = y / HEIGHT
        d.line([(0, y), (WIDTH, y)], fill=(int(255 - 60 * t), int(236 - 20 * t), int(200 + 40 * t)))

    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    # 太陽
    for r, a in ((170, 40), (120, 70), (80, 200)):
        ld.ellipse([1080 - r, 120 - r, 1080 + r, 120 + r], fill=(255, 214, 120, a))
    # にじんだ雲
    for _ in range(14):
        x, y = rnd.randint(0, WIDTH), rnd.randint(30, 260)
        w, h = rnd.randint(90, 220), rnd.randint(30, 70)
        ld.ellipse([x, y, x + w, y + h], fill=(255, 255, 255, 90))
    # 丘（園庭の芝）
    for base, col in ((470, (170, 210, 140, 200)), (530, (140, 195, 115, 230)), (590, (205, 170, 120, 255))):
        pts = [(0, HEIGHT)]
        for x in range(0, WIDTH + 40, 40):
            pts.append((x, base + 25 * math.sin(x / 170 + base)))
        pts.append((WIDTH, HEIGHT))
        ld.polygon(pts, fill=col)
    # 3人の女の子（大・小・小）
    for cx, s, col in ((880, 1.15, (235, 120, 120)), (980, 0.95, (120, 170, 230)), (1060, 0.95, (250, 190, 90))):
        gy = 585
        ld.ellipse([cx - 22 * s, gy - 130 * s, cx + 22 * s, gy - 86 * s], fill=(250, 220, 195, 255))  # 顔
        ld.pieslice([cx - 26 * s, gy - 136 * s, cx + 26 * s, gy - 84 * s], 180, 360, fill=(80, 55, 40, 255))  # 髪
        ld.polygon([(cx, gy - 88 * s), (cx - 34 * s, gy - 20 * s), (cx + 34 * s, gy - 20 * s)], fill=col + (255,))
        ld.line([(cx - 12 * s, gy - 20 * s), (cx - 18 * s, gy)], fill=(250, 220, 195, 255), width=int(8 * s))
        ld.line([(cx + 12 * s, gy - 20 * s), (cx + 18 * s, gy)], fill=(250, 220, 195, 255), width=int(8 * s))
    layer = layer.filter(ImageFilter.GaussianBlur(2.5))
    img = Image.alpha_composite(img.convert("RGBA"), layer)
    # 紙の質感ノイズ
    noise = Image.effect_noise((WIDTH, HEIGHT), 18).convert("L").point(lambda p: p // 8)
    img = Image.composite(img, Image.new("RGBA", img.size, (255, 250, 240, 255)), noise.point(lambda p: 255 - p))
    return img.convert("RGB")


def get_background(offline: bool) -> Image.Image:
    if not offline and os.environ.get("OPENAI_API_KEY"):
        try:
            print("[thumbnail] OpenAI DALL-E 3 で画像を生成中...")
            return generate_with_openai()
        except Exception as e:  # noqa: BLE001
            print(f"[thumbnail] OpenAI 失敗: {e}", file=sys.stderr)
    if not offline and os.environ.get("GEMINI_API_KEY"):
        try:
            print("[thumbnail] Gemini で画像を生成中...")
            return generate_with_gemini()
        except Exception as e:  # noqa: BLE001
            print(f"[thumbnail] Gemini 失敗: {e}", file=sys.stderr)
    print("[thumbnail] API キーが無い/失敗したため、ローカルの水彩風背景を使用します")
    return generate_fallback()


# ---------------------------------------------------------------- 文字入れ
def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if path and os.path.exists(path):
            return ImageFont.truetype(path, size)
    raise SystemExit("日本語フォントが見つかりません。THUMBNAIL_FONT に .ttf/.ttc のパスを指定してください。")


def fit_font(draw, text, max_width, start):
    size = start
    while size > 16:
        font = load_font(size)
        if draw.textlength(text, font=font) <= max_width:
            return font
        size -= 2
    return load_font(size)


def cover_resize(img: Image.Image) -> Image.Image:
    """アスペクト比を保ったまま 1280x670 に中央クロップ。"""
    scale = max(WIDTH / img.width, HEIGHT / img.height)
    img = img.resize((math.ceil(img.width * scale), math.ceil(img.height * scale)), Image.LANCZOS)
    left, top = (img.width - WIDTH) // 2, (img.height - HEIGHT) // 2
    return img.crop((left, top, left + WIDTH, top + HEIGHT))


def compose(bg: Image.Image) -> Image.Image:
    img = cover_resize(bg).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)

    # 左側に半透明の白い帯（文字の可読性確保）
    panel = (50, 150, 790, 475)
    od.rounded_rectangle(panel, radius=28, fill=(255, 255, 255, 205))
    img = Image.alpha_composite(img, overlay)
    d = ImageDraw.Draw(img)

    inner_w = panel[2] - panel[0] - 70
    x = panel[0] + 35
    f1 = fit_font(d, TITLE_LINE1, inner_w, 44)
    f2 = load_font(78)
    f3 = fit_font(d, CATCH_COPY, inner_w, 36)

    y = panel[1] + 40
    d.text((x, y), TITLE_LINE1, font=f1, fill=(70, 50, 40))
    y += f1.size + 30
    d.text((x, y), TITLE_LINE2, font=f2, fill=(220, 95, 70))
    y += f2.size + 30
    d.line([(x, y), (x + inner_w, y)], fill=(230, 160, 90), width=4)
    y += 26
    d.text((x, y), CATCH_COPY, font=f3, fill=(60, 90, 60))
    return img.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="thumbnail_ep2.png")
    ap.add_argument("--offline", action="store_true", help="API を使わずローカル背景で生成")
    args = ap.parse_args()

    bg = get_background(args.offline)
    bg.save(os.path.splitext(args.out)[0] + "_bg.png")
    compose(bg).save(args.out)
    print(f"[thumbnail] 出力: {args.out} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
