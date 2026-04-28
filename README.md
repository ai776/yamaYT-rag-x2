# yamamoto-x-post

テーマを渡すと、山本さんの RAG データ（`insights/`）と X の最新トレンドを組み合わせて、**X（Twitter）の「記事」向け長文投稿を 1 本**生成する [Claude Code](https://claude.ai/claude-code) 用スキルです。

実装の詳細・各ステップの指示は **`.claude/skills/yamamoto-x-post/SKILL.md`** が正本です。この README は概要とセットアップ手順です。

## 機能（ワークフロー）

1. **テーマを受け取る** → X リサーチ ON/OFF、X API の有無を確認（未設定なら案内）
2. **X で最新情報をリサーチ**（OFF の場合はスキップ）→ WebSearch → Nitter → X API の 3 段階フォールバック
3. **記事構成に整理**（リサーチ OFF の場合はスキップ）→ RAG に投げやすい形に構造化
4. **山本さん RAG** → `insights/` から関連知見を抽出
5. **X 記事（長文）を 1 本生成** → 確定後、`articles/` に Markdown で保存

各ステップでユーザーの承認を得てから次に進みます（スキル内では選択肢 UI の利用を想定）。

## 生成物の仕様（概要）

| 項目 | 内容 |
|------|------|
| 形式 | X の「記事」用の長文（マークダウン） |
| 分量の目安 | 約 2,000〜3,000 文字、セクション 7〜12 個 |
| 文体 | タメ口・独り言調。ハッシュタグ・絵文字は使わない |
| 保存先 | `articles/`（ファイル名例: `260416_theme-short-name.md`） |

## プロジェクト構成

```
yamamoto-rag-x/
├── README.md
├── articles/                          ← 生成した X 記事の保存先
├── scripts/                           ← 生成した YouTube 台本の保存先
├── insights/                          ← 山本さんの RAG 用テキスト（主ソース）
│   ├── _routing.md                    ← RAG仕訳インデックス（最初に読む正本）
│   ├── {各事例}_analysis.txt
│   └── video_prompt/                  ← YouTube台本プロンプト
├── 山本さん/                          ← 補助 RAG ソース（旧運用の互換用）
│   ├── RAG-POLICY.md                  ← RAG 運用ポリシー（両スキル共通）
│   └── {各事例}.txt
└── .claude/
    └── skills/
        ├── yamamoto-x-post/
        │   └── SKILL.md               ← X 記事スキル定義
        └── yamamoto-yt-script/
            └── SKILL.md               ← YouTube 台本スキル定義
```

## RAG データ運用ポリシー（重要）

AIがテーマに対して関係ない事例を混ぜないよう、**「仕訳を先に見て、必要分だけ読む」** を基本方針としています。
仕訳の正本は `insights/_routing.md`、補足ポリシーは `山本さん/RAG-POLICY.md`（両スキル共通）を参照。

### 原則

1. **grep前に必ず `insights/_routing.md` を読む**
2. **主カテゴリは1つ、補助カテゴリは0〜1つまで**
3. **優先ファイルを先に5〜8本読む。足りない場合だけ追加grepする**
4. **投稿に反映する具体事例は少数に絞る**
   - X 記事: 1〜2 件（原則 1 件）
   - YouTube 台本: 2〜3 件（体験談 1 件＋実践 1〜2 件）
5. **1 投稿 1 テーマ**を徹底。複数の具体事例を過剰に混在させない
6. **元ファイルは移動・改名しない**。新しい `*_analysis.txt` を追加したら `insights/_routing.md` に登録する

### スキル実行時の自動処理

- RAG 検索ステップで `insights/_routing.md` と `山本さん/RAG-POLICY.md` を Read
- ユーザーテーマから主カテゴリ1つ、補助カテゴリ0〜1つを判定
- `_routing.md` の優先ファイルを先に5〜8本読み、足りない場合だけ `insights/` と `山本さん/` を追加grep
- 反映フェーズで X記事は1〜2件、YouTube台本は2〜3件に絞り込み、AskUserQuestion で承認
- 成果物保存後も RAG 元ファイルは移動・改名しない（使用済みフォルダ・履歴ログは使わない）

## 必要な環境

- [Claude Code](https://claude.ai/claude-code) がインストール済みであること
- インターネット接続（X リサーチに使用）

## セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/ai776/yamamoto-rag-x.git
cd yamamoto-rag-x
```

### 2. X API の設定（任意）

X API がなくてもスキルは動作します（WebSearch + Nitter でリサーチ）。
設定すると X の最新投稿をリアルタイムで検索でき、**リサーチ精度が大幅に向上**します。

---

## X API セットアップ手順

### 料金

| プラン | 料金 | 備考 |
|--------|------|------|
| Pay-Per-Use（従量課金） | 最低 **$5（約750円）** から | 2026年2月〜。使った分だけ課金 |
| ~~Free（無料）~~ | ~~$0~~ | **2026年2月に廃止。** 503エラーが発生 |

> リサーチ用途なら $5 で十分使えます。

### 前提条件

- 有効な X(Twitter) アカウント
- クレジットカード

### STEP 1: Developer Portal でアカウント作成 & Bearer Token 取得

1. **https://developer.x.com** にアクセスし、Xアカウントでサインイン
2. アカウント名を入力
3. 利用目的を入力（**250文字以上**必要）
   <details>
   <summary>入力例を見る</summary>

   > SNSマーケティングのためのトレンドリサーチ・投稿分析ツールとして利用します。特定のテーマに関する最新のツイートを検索し、トレンドや話題の切り口を収集して、効果的なSNS投稿文を生成するために活用します。APIを通じて取得したデータは商用目的には使用せず、投稿内容の企画・リサーチ用途のみに限定して利用します。

   </details>

4. チェックボックスにチェックして「送信」
5. 左メニュー **「Projects & Apps」** → 自分のApp → **「Keys and tokens」** タブ
6. **「Bearer Token」** の **「Generate」** をクリック → トークンをコピー

> **⚠️ Bearer Tokenは一度しか表示されません。** 紛失した場合は「Regenerate」で再発行できます。

### STEP 2: Developer Console で Pay-Per-Use に切り替え

> ⚠️ STEP 1の developer.x.com とは **別の画面** です

1. **https://console.x.com** にアクセス
2. 左メニュー **「アプリ」** を開く
3. Appの下に **「Free」** と表示されている場合 → **「Pay-Per-Use」に変更**

> **⚠️ Freeのままだと `403 Client Forbidden` エラーで検索APIが使えません**

### STEP 3: クレジット購入 & 支出上限設定

1. console.x.com の左メニュー **「請求書作成」→「クレジット」**
2. **「クレジットを購入する」** → **$5** をチャージ
3. **「支出上限を管理」** → 上限を **$5** に設定

> **⚠️ 支出上限のデフォルトは「無制限」です。必ず設定してください。**
> 設定しないとクレジット残高を超えた分が追加請求される可能性があります。

### STEP 4: 環境変数を設定

```bash
echo 'export X_API_BEARER_TOKEN="ここにBearer Tokenを貼り付け"' >> ~/.bashrc
source ~/.bashrc
```

> Mac (zsh) の場合は `~/.bashrc` を `~/.zshrc` に変更

### STEP 5: 動作確認

```bash
# トークンが表示されればOK
echo $X_API_BEARER_TOKEN

# APIテスト（任意）
curl -s -H "Authorization: Bearer ${X_API_BEARER_TOKEN}" \
  "https://api.x.com/2/tweets/search/recent?query=test&max_results=10" \
  | python3 -m json.tool | head -20
```

`"data"` が返ってくれば成功です。

---

## トラブルシューティング

| エラー | 原因 | 解決方法 |
|--------|------|----------|
| `403 Client Forbidden` | Appが Free プランのまま | [STEP 2](#step-2-developer-console-で-pay-per-use-に切り替え) で Pay-Per-Use に切り替え |
| `503 Service Unavailable` | Free プランのAPIキーを使用 | [STEP 2](#step-2-developer-console-で-pay-per-use-に切り替え) で Pay-Per-Use に切り替え |
| `401 Unauthorized` | Bearer Token が無効 | [STEP 1](#step-1-developer-portal-でアカウント作成--bearer-token-取得) で Regenerate して再設定 |
| トークンが表示されない | 環境変数が未設定 | [STEP 4](#step-4-環境変数を設定) を再実行 |

## 使い方

Claude Code を起動し、テーマと「X 記事を書いて」などと依頼します。

```
プログラミングスクールの話でX記事を書いて
```

スキルが起動すると、おおむね次の流れです。

1. X API の設定チェック（未設定なら案内）
2. テーマ・X リサーチ ON/OFF の確認
3. X リサーチ（WebSearch → Nitter → X API）
4. 記事構成の整理
5. RAG 検索（`insights/` から関連情報を抽出）
6. **長文 X 記事を 1 本**生成 → 確定後に `articles/` へ保存

各ステップで選択肢が表示されるので、指示に従って進めてください。

## 参考リンク

- [X Developer Portal](https://developer.x.com)
- [X Developer Console](https://console.x.com)
- [X API セットアップ詳細ガイド](https://www.and-and.co.jp/gas-lab/x-twitter-api-start/)
- [503エラー解決ガイド（Pay-Per-Use移行）](https://www.and-and.co.jp/gas-lab/x-twitter-api-503-error/)
- [X API 公式料金ページ](https://docs.x.com/x-api/getting-started/pricing)

## ライセンス

Private - All Rights Reserved
