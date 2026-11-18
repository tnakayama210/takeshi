# delta-inc.jp 本体サイトの更新ファイル（中古車販売の追加）

本番サイト（2026-11-17時点）から取得したファイルに、**必要な箇所だけ**を追加した差し替え用ファイルです。
フォルダ構成は、サーバーの公開フォルダ（Xserver では `delta-inc.jp/public_html/`）と同じにしてあります。

## 変更内容
| ファイル | 種類 | 内容 |
|---|---|---|
| `index.html` | 上書き | トップのスライダーの先頭に「USED CAR SALES／中古車販売」のスライドを追加（リンク先は `/usedcar/`） |
| `img/main_usedcar.png` | 新規 | スライド画像（960×314、既存スライドと同じ帯のデザイン。ナンバーは写らない範囲で切り抜き） |
| `img/bn_business_domain06.png` | 新規 | トップ「Business domain」の6つ目のバナー「人材事業」（写真は事業内容ページの photo10.jpg）。リンク先は `jinzai/` |
| `img/bn_business_domain05.png` | 新規 | トップ「Business domain」の5つ目のバナー「中古車販売」（228×258、既存バナーと同じ体裁。ナンバーはぼかし済み）。リンク先は `business/?v=20261117#usedcar`（古い事業内容ページのキャッシュを避けるため） |
| `business/index.html` | 上書き | 事業内容ページに「中古車販売事業」の欄を追加し、冒頭の文に「中古車販売」を追記 |
| `business/img/s_title13.png` | 新規 | 見出し画像「中古車販売事業」 |
| `business/img/photo13.jpg` | 新規 | 事業紹介の写真（250×161、ナンバーはぼかし済み） |

あわせて、リポジトリの `usedcar/` フォルダにある `index.html`、`css/`、`js/`、`img/` を、サーバーの `public_html/usedcar/` にアップロードしてください。

## アップロード手順（Xserver ファイルマネージャー）
1. サーバーパネルの「ファイル管理」を開き、`delta-inc.jp/public_html/` に移動します。
2. **バックアップ**：既存の `index.html` と `business/index.html` をダウンロードして保存しておきます。
3. 上の表のファイルを、それぞれ同じ場所にアップロードします（`index.html` 2つは上書き）。
4. `public_html/usedcar/` フォルダを作り、LPのファイルをアップロードします。
5. ブラウザで次の3ページを確認します。
   - https://delta-inc.jp/ （スライダー）
   - https://delta-inc.jp/business/ （中古車販売事業の欄）
   - https://delta-inc.jp/usedcar/ （LP）

## 注意
- アップロードの前にサイトが更新されていた場合、`index.html` などを上書きすると、その更新が消えます。
  その場合は差分（下記）だけを手で反映してください。
  - `index.html`：`<div class="wideslider"><ul>` の直下に、次の1行を追加します。
    `<li><a href="usedcar/"><img src="img/main_usedcar.png" alt="中古車販売"></a></li>`
  - `business/index.html`：「不動産コンサルティング事業」の欄の直後に、`id="usedcar"` の欄を追加します。
