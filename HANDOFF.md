# 引き継ぎ：delta-inc.jp への中古車販売コンテンツのアップロード

ブランチ：`claude/used-car-auction-lp-xf0f47`（リポジトリ `tnakayama210/takeshi`）

## やること
Xserver のファイル管理（ユーザーはChromeでサーバーパネルにログイン済み）を使い、次のファイルを
`delta-inc.jp/public_html/` にアップロードする。**バックアップはユーザーが取得済み。**

| リポジトリ内のファイル | アップロード先（public_html/ からの相対パス） | 種類 |
|---|---|---|
| `site-update/index.html` | `index.html` | 上書き |
| `site-update/img/main_usedcar.png` | `img/main_usedcar.png` | 新規 |
| `site-update/img/bn_business_domain05.png` | `img/bn_business_domain05.png` | 新規 |
| `site-update/business/index.html` | `business/index.html` | 上書き |
| `site-update/business/img/s_title13.png` | `business/img/s_title13.png` | 新規 |
| `site-update/business/img/photo13.jpg` | `business/img/photo13.jpg` | 新規 |
| `usedcar/index.html` | `usedcar/index.html` | 新規（`usedcar` フォルダを作成） |
| `usedcar/css/style.css` | `usedcar/css/style.css` | 新規 |
| `usedcar/js/main.js` | `usedcar/js/main.js` | 新規 |
| `usedcar/img/*`（7ファイル） | `usedcar/img/` | 新規 |

`usedcar/src/`、`tailwind.config.js`、`package*.json`、`node_modules/`、`README.md` はアップロードしない。

ファイル管理の画面：https://secure.xserver.ne.jp/xapanel/xserver/index →「ファイル管理」→ `delta-inc.jp/public_html/`

## 手順
1. `git fetch origin claude/used-car-auction-lp-xf0f47 && git checkout claude/used-car-auction-lp-xf0f47`
2. **上書き前の確認**：本番の `https://delta-inc.jp/` と `https://delta-inc.jp/business/` を取得し、
   2026-11-17時点の内容（`site-update/` のファイルから追加箇所を除いたもの）と比べる。
   本番がその後に更新されていた場合は、ファイルごと上書きせず、ユーザーに確認してから次の差分だけを反映する。
   - `index.html`：`<div class="wideslider">` 内の `<ul>` の直下に
     `<li><a href="usedcar/"><img src="img/main_usedcar.png" alt="中古車販売"></a></li>`
   - `business/index.html`：「不動産コンサルティング事業」の欄の直後に、`id="usedcar"` の欄を追加し、
     冒頭の文を「不動産コンサルティングからシェアハウスの運営、中古車販売まで。…」にする
3. 上の表のとおりにアップロードする（文字コードUTF-8。`business/index.html` は改行がCRLFなのでそのまま）。
4. 確認する：
   - https://delta-inc.jp/ ：スライダーの先頭が「USED CAR SALES／中古車販売」で、クリックすると /usedcar/ に移動する
   - https://delta-inc.jp/business/ ：「中古車販売事業」の欄が表示される
   - https://delta-inc.jp/usedcar/ ：LPが表示され、CSSと画像が読み込まれ、コンソールにエラーがない

## これまでの経緯（要点）
- 当初の依頼はオークションLPだったが、「単なる中古車販売。オークションはやらない」とのことで、中古車販売LP（`usedcar/`）に作り替えた。
- ユーザーの指示：価格は出さない／中古車販売事業そのものだけをアピール／余計な文言は削除／メール問い合わせ（customer@delta-inc.jp）のボタンを付ける。
- 古物商許可：東京都公安委員会許可 第303272009420号（自動車商）。LPのファーストビューとフッター、事業内容ページに記載している。
- 写真はナンバー・選挙ポスター・ミラーへの人物の映り込みにぼかしを入れ、EXIFを削除済み。ぼかし前の元写真は使わないこと。
- デザインは既存LP `/recruit-cleaning/` のトークン（`#0060AC` ほか）に揃えている。

## 2026-11-17 アップロード後の追加対応（本番反映済み）
- トップの「Business domain」に中古車販売のバナー（`bn_business_domain05.png`）を追加。リンク先は `business/?v=20261117#usedcar`（古い事業内容ページがブラウザにキャッシュされ、中古車販売の欄が見えない問題への対策）。
- LPの問い合わせフォームを削除（電話・メールのみ）。フォーム用のJSも削除。
- LPから会社情報・代表者の記載を削除し、「古物商許可」の欄だけにした（ユーザー指示）。

## 2026-11-18 人材事業LP（本番反映済み）
- `jinzai/` を https://delta-inc.jp/jinzai/ に公開（特定技能外国人の派遣・ご紹介）。詳しくは `jinzai/README.md`。
- `business/index.html` の「人材事業」欄に `../jinzai/` へのリンクを追加。

## 未対応（ユーザーに伝える）
- 労働者派遣法の情報提供（マージン率・派遣労働者数など）の公開先が未確認。厚労省サイトの該当欄は空。
- 定休日の表記が食い違っている：既存サイトのヘッダー画像は「水曜・日曜」、LPはユーザーの指示どおり「水曜」。

## 2026-11-18 追記（トップページ）

- スライダーの先頭を「不動産コンサルティング」に変更（中古車販売は2枚目）
- 「Business domain」に6つ目「人材事業」（`img/bn_business_domain06.png` → `jinzai/`）を追加
- アップロード：`site-update/index.html` → `index.html`、`site-update/img/bn_business_domain06.png` → `img/`
