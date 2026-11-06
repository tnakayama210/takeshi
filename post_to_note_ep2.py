#!/usr/bin/env python3
"""episode2.md と thumbnail_ep2.png を使って note に記事を下書き保存する（Playwright）。

前提:
  pip install -r requirements.txt && playwright install chromium

ログイン:
  - 環境変数 NOTE_EMAIL / NOTE_PASSWORD があれば自動ログイン
  - 無ければブラウザが開いた状態で待機するので、手動でログイン（2段階認証も手動で）
  - ログイン状態は ./.note_profile に保存され、次回以降は再利用される

使い方:
  python post_to_note_ep2.py               # 下書き保存まで（既定）
  python post_to_note_ep2.py --publish     # 「公開に進む」画面まで進めて止まる（最終公開は手動）
  python post_to_note_ep2.py --dry-run     # ブラウザを開かず、読み込んだ内容だけ確認
  python post_to_note_ep2.py --headless    # 画面なしで実行（手動ログインは不可）

note の画面構成は予告なく変わるため、失敗時は note_error.png のスクリーンショットを確認してください。
"""
import argparse
import html
import os
import re
import sys
from pathlib import Path

LOGIN_URL = "https://note.com/login"
NEW_ARTICLE_URL = "https://editor.note.com/new"
PROFILE_DIR = Path(".note_profile")


# ---------------------------------------------------------------- 原稿読み込み
def load_episode(path: Path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        raise SystemExit(f"{path}: 先頭の front matter（--- title: ... ---）が見つかりません")
    title = ""
    for line in m.group(1).splitlines():
        if line.startswith("title:"):
            title = line.split(":", 1)[1].strip()
    if not title:
        raise SystemExit(f"{path}: title が空です")
    return title, text[m.end():].strip()


def inline(s: str) -> str:
    s = html.escape(s)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)


def markdown_to_html(md: str) -> str:
    """note エディタに貼り付ける用の簡易変換（見出し・区切り線・段落・改行・太字）。"""
    out = []
    for block in re.split(r"\n\s*\n", md):
        block = block.strip()
        if not block:
            continue
        if re.fullmatch(r"-{3,}", block):
            out.append("<hr>")
        elif m := re.match(r"^(#{2,3})\s+(.*)", block):
            out.append(f"<h3>{inline(m.group(2))}</h3>")  # note は大見出し=h2 / 小見出し=h3
        else:
            out.append("<p>" + "<br>".join(inline(l.strip()) for l in block.splitlines()) + "</p>")
    return "".join(out)


# ---------------------------------------------------------------- ブラウザ操作
def first_visible(page, selectors, timeout=15000):
    """候補セレクタのうち最初に見つかった要素を返す。"""
    loc = page.locator(", ".join(selectors)).first
    loc.wait_for(state="visible", timeout=timeout)
    return loc


def ensure_login(page, headless: bool):
    page.goto("https://note.com/", wait_until="domcontentloaded")
    page.goto(NEW_ARTICLE_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(2000)
    if "editor.note.com" in page.url and "login" not in page.url:
        print("[note] 既存のログイン状態を使用します")
        return

    email, password = os.environ.get("NOTE_EMAIL"), os.environ.get("NOTE_PASSWORD")
    page.goto(LOGIN_URL, wait_until="domcontentloaded")
    if email and password:
        print("[note] NOTE_EMAIL / NOTE_PASSWORD でログインします")
        first_visible(page, ["#email", "input[type=email]", "input[name=login]"]).fill(email)
        first_visible(page, ["#password", "input[type=password]"]).fill(password)
        page.get_by_role("button", name=re.compile("ログイン")).first.click()
    elif headless:
        raise SystemExit("headless では手動ログインできません。NOTE_EMAIL/NOTE_PASSWORD を設定してください。")
    else:
        print("[note] ブラウザでログインしてください（最大5分待機）...")
    page.wait_for_url(lambda u: "login" not in u, timeout=300_000)
    print("[note] ログイン完了")


def paste_html(page, target, html_str: str, plain: str):
    """ProseMirror エディタへ HTML を貼り付ける（見出し・区切り線を保ったまま入力できる）。"""
    target.click()
    page.evaluate(
        """([html, text]) => {
            const el = document.activeElement;
            const dt = new DataTransfer();
            dt.setData('text/html', html);
            dt.setData('text/plain', text);
            el.dispatchEvent(new ClipboardEvent('paste', {clipboardData: dt, bubbles: true, cancelable: true}));
        }""",
        [html_str, plain],
    )


def upload_header_image(page, image: Path):
    print(f"[note] 見出し画像をアップロード: {image}")
    first_visible(page, [
        "button[aria-label='画像を追加']",
        "button:has-text('画像を追加')",
        "[class*='eyecatch'] button",
    ]).click()
    with page.expect_file_chooser(timeout=15000) as fc:
        first_visible(page, ["button:has-text('画像をアップロード')", "text=画像をアップロード"]).click()
    fc.value.set_files(str(image))
    # トリミングダイアログの「保存」
    try:
        page.locator("[role=dialog] button:has-text('保存'), .ReactModal__Content button:has-text('保存')").first.click(timeout=15000)
    except Exception:  # noqa: BLE001
        pass
    page.wait_for_timeout(3000)


def run(args):
    from playwright.sync_api import sync_playwright

    title, body_md = load_episode(Path(args.episode))
    image = Path(args.image)
    if not image.exists():
        raise SystemExit(f"{image} がありません。先に generate_thumbnail_ep2.py を実行してください。")

    with sync_playwright() as p:
        launch_kwargs = {"headless": args.headless, "locale": "ja-JP", "viewport": {"width": 1280, "height": 900}}
        if os.environ.get("CHROMIUM_PATH"):
            launch_kwargs["executable_path"] = os.environ["CHROMIUM_PATH"]
        ctx = p.chromium.launch_persistent_context(str(PROFILE_DIR), **launch_kwargs)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            ensure_login(page, args.headless)
            if "editor.note.com" not in page.url:
                page.goto(NEW_ARTICLE_URL, wait_until="domcontentloaded")

            print("[note] タイトルを入力")
            first_visible(page, ["textarea[placeholder='記事タイトル']", "textarea[placeholder*='タイトル']"], 30000).fill(title)

            print("[note] 本文を入力")
            editor = first_visible(page, [".ProseMirror[contenteditable=true]", "div[contenteditable=true][role=textbox]"])
            paste_html(page, editor, markdown_to_html(body_md), body_md)
            page.wait_for_timeout(1500)

            upload_header_image(page, image)

            if args.publish:
                print("[note] 「公開に進む」をクリック（最終的な公開ボタンは押しません）")
                page.get_by_role("button", name=re.compile("公開に進む")).first.click()
            else:
                print("[note] 下書き保存")
                page.get_by_role("button", name=re.compile("下書き保存")).first.click()
            page.wait_for_timeout(3000)
            page.screenshot(path="note_result.png", full_page=True)
            print(f"[note] 完了: {page.url}（スクリーンショット: note_result.png）")
            if not args.headless:
                input("確認できたら Enter でブラウザを閉じます > ")
        except Exception:
            page.screenshot(path="note_error.png", full_page=True)
            print("[note] エラー発生。note_error.png を確認してください。", file=sys.stderr)
            raise
        finally:
            ctx.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", default="episode2.md")
    ap.add_argument("--image", default="thumbnail_ep2.png")
    ap.add_argument("--publish", action="store_true", help="下書き保存ではなく公開設定画面へ進む")
    ap.add_argument("--headless", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.dry_run:
        title, body = load_episode(Path(args.episode))
        h = markdown_to_html(body)
        print("タイトル:", title)
        print(f"本文: {len(body)} 文字 / 見出し {h.count('<h3>')} 個 / 区切り線 {h.count('<hr>')} 本")
        print("画像:", args.image, "OK" if Path(args.image).exists() else "（未生成）")
        return
    run(args)


if __name__ == "__main__":
    main()
