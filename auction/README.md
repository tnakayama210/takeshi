# 中古車オークション 参加登録LP（/auction/）

株式会社delta（https://delta-inc.jp/）の新規事業「業者向け中古車オークション」の参加登録LPです。
既存の新規事業LP（`/recruit-cleaning/`）と同じ **静的HTML ＋ Tailwind CSS（ビルド済みCSS）** の構成です。

## 公開方法
`auction/` ディレクトリ内の次のファイルを、サーバーの `/auction/` にアップロードしてください。

- `index.html`
- `css/style.css`
- `js/main.js`
- `img/`

`src/`、`tailwind.config.js`、`package.json`、`node_modules/` はアップロード不要です（開発用）。

## 編集とビルド
```bash
cd auction
npm install
npm run build    # css/style.css を再生成（index.html のクラスを変えたら必ず実行）
npm run watch    # 編集中の自動ビルド
```

## デザイントークン（既存LPの css/style.css から抽出）
| トークン | 値 | 用途 |
|---|---|---|
| `delta` | `#0060AC`（hover `#004A85`） | CTA・強調 |
| `ink` / `ink-2` / `ink-3` / `ink-4` | `#222` / `#333` / `#666` / `#999` | 文字色 |
| `line` | `#DDD` | 罫線 |
| `paper` | `#F8F8F8` | 背景 |
| フッター | `#515151` | フッター背景 |
| フォント | Hiragino / Meiryo / Noto Sans JP、英字見出しは EB Garamond | |

## 画像の差し替え
`img/` 内の同名ファイルを置き換えれば反映されます（縦長 1200×1600 を想定。表示位置は各 `<img>` の `object-[x_y]` で調整）。
**車両写真は、ナンバープレートや人物の写り込みを必ずぼかしてから使用してください。**
現在の写真は、ナンバー・選挙ポスター・ミラーへの人物の映り込みにぼかしを入れ、EXIF（位置情報など）を削除してあります。

## フォーム送信の接続
- `index.html` の `<form id="entry-form" data-endpoint="">` に送信先URLを設定します。
  - **空のとき**：デモモード（送信せずに完了画面を表示し、送信データをコンソールに出力）
  - **URLを設定したとき**：`FormData` を POST し、2xx 応答で完了画面を表示。失敗時はエラーメッセージを表示します
- 送信処理は `js/main.js` の `submitRegistration()` 1か所にまとめてあります。
- 送信される項目（すべて整形済み。全角は半角に変換）

| name | 内容 |
|---|---|
| `company` | 会社名／屋号 |
| `name` | 担当者名 |
| `tel` | 電話番号 |
| `prefecture` | 都道府県 |
| `email` | メールアドレス |
| `license_status` | `now`（入力済み）／`later`（後日提出） |
| `license_number` | 古物商許可証番号（12桁の数字。後日提出の場合は空） |
| `privacy` | `agree` |
| `website` | ハニーポット（値が入っていたらbotとして破棄） |
| `source` | `auction-lp` |

- 既存の問い合わせフォーム（`/contact/kakunin.php`）と同様のPHPで受ける場合は、上記の項目を受け取ってメールを送信し、JSON（例：`{"ok":true}`）を返すエンドポイントを用意してください。
  **サーバー側でも、必ず同じ内容のバリデーションを行ってください。**
- 送信完了時に `gtag('event','generate_lead')`、または旧GA（`ga('send','event',...)`）が存在すれば計測イベントを送ります。

## 要確認（公開前）
`index.html` 内の `要確認` コメント箇所：
- 「毎週〇〇台以上」の実数
- 「業界最安水準」の根拠（景品表示法上、比較の根拠が必要です。根拠がない場合は表現の変更を推奨）
- FAQ の回答内容（必要書類、手数料、支払方法・期日）
- 連絡目安（「2営業日以内」）
