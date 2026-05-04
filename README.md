# yamaYT-rag-x2

山本さん向けコンテンツ用の **[Claude Code](https://claude.ai/claude-code)** スキルと RAG データをまとめたリポジトリです。

| スキル | 役割 | 正本（手順・制約の詳細） |
|--------|------|---------------------------|
| **X 長文記事** | テーマに沿った **X（Twitter）の「記事」向け長文**を 1 本生成する | `.claude/skills/yamamoto-x-post/SKILL.md` |
| **YouTube 台本** | 同じ RAG と X リサーチを土台に、**長尺台本（目安30分構成＋ Shorts）** を生成する | `.claude/skills/yamamoto-yt-script/SKILL.md` |

この README は **概要・ディレクトリ構成・運用ポリシー要点・セットアップ** です。生成の粒度や承認ステップは各 `SKILL.md` に従います。

## 機能概要（ワークフロー共通イメージ）

1. **テーマを受け取る** → X リサーチの ON/OFF、X API の有無を確認（未設定時は README / スキル内の案内）
2. **X で最新情報をリサーチ**（OFF の場合はスキップ）→ Web 検索 → Nitter → X API の段階的フォールバック（詳細は各スキル）
3. **記事構成 / 台本構成に整理**（リサーチ OFF 時はスキップすることがある）
4. **山本さん RAG** → `insights/_routing.md` に沿って `insights/`（主）と `山本さん/`（補助）から必要箇所だけ読む
5. **成果物を生成**  
   - X 記事: 確定後 `articles/` に Markdown で保存  
   - YouTube 台本: 確定後 `scripts/` に保存（運用により `scripts_tts/` に読み上げ調整版を置くこともあり）

各スキル内ではステップごとにユーザーの確認を挟む想定です。

## 生成物の仕様（概要）

### X「記事」長文（`yamamoto-x-post`）

| 項目 | 内容 |
|------|------|
| 形式 | X の「記事」向け長文（Markdown） |
| 分量の目安 | 約 2,000〜3,000 文字、セクション 7〜12 個 |
| 文体 | タメ口・独り言調。ハッシュタグ・絵文字は使わない |
| 保存先 | `articles/`（例: `260416_theme-short-name.md`） |

### YouTube 台本（`yamamoto-yt-script`）

| 項目 | 内容 |
|------|------|
| 形式 | 本編台本（目安分量・章立て・CTA は `SKILL.md` 参照）と Shorts 案 |
| 保存先 | 主に `scripts/`。TTS・読み分け用の派生ファイルは `scripts_tts/` などに置ける |

※ RAG に載せる具体事例の件数など、記事と台本で上限が異なる場合があります。`_routing.md` と `山本さん/RAG-POLICY.md` を優先してください。

## プロジェクト構成

```
yamaYT-rag-x2/
├── README.md
├── articles/                 ← X 長文記事の保存先
├── scripts/                  ← YouTube 台本（本体）の保存先
├── scripts_tts/              ← 読み上げ／TTS 向けに整理した派生 Markdown（運用により使用）
├── tools/
│   └── rag_retrieval_smoke_test.py  ← RAG ルーティングの簡易スモーク（外部依存なし）
├── insights/                 ← RAG の主ソース（*_analysis.txt 等）
│   ├── _routing.md           ← 仕訳インデックス（grep より先に読む正本）
│   └── video_prompt/         ← 動画／台本系プロンプト断片
├── 山本さん/                  ← 補助 RAG・運用ポリシー（互換・追記ソース）
│   ├── RAG-POLICY.md
│   └── …各種 *_analysis.txt など
└── .claude/
    └── skills/
        ├── yamamoto-x-post/SKILL.md
        └── yamamoto-yt-script/SKILL.md
```

## RAG データ運用ポリシー（重要）

無関係な事例を混ぜないため、**「仕訳（`_routing.md`）を先に見て、必要分だけ読む」** が基本です。補足は `山本さん/RAG-POLICY.md`、カテゴリと優先ファイルの一覧は **`insights/_routing.md`** が正本です（本リポジトリ専用の仕訳表であり、ほかの RAG リポジトリとは同期しません）。

### 原則（抜粋）

1. **grep の前に必ず `insights/_routing.md` を読む**
2. **主カテゴリは 1 つ、補助カテゴリは 0〜1 つまで**
3. **優先ファイルを先に 5〜8 本読む。足りない場合だけ追加 grep**
4. **投稿・台本に反映する具体事例は少数に絞る**（スキル・ポリシーに記載の上限に従う）
5. **1 本作業 1 テーマ**。事例の過剰混在を避ける
6. **元ファイルは移動・改名しない**。新規 `*_analysis.txt` は `_routing.md` に登録する

## `tools/` のスモークテスト

`insights/` の参照やルーティング設定の整合を、依存パッケージなしでざっと確認できます。

```bash
python3 tools/rag_retrieval_smoke_test.py
# 代表テーマのみ: python3 tools/rag_retrieval_smoke_test.py --only outsourcing
```

Claude Code 上の本番ワークフローそのものではありませんが、ローカルで「ルートとファイル名が妥当か」を手早く見る用途です。

## 必要な環境

- [Claude Code](https://claude.ai/claude-code) がインストール済みであること（スキル利用時）
- インターネット接続（X リサーチに使用する場合）

## セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/ai776/yamaYT-rag-x2.git
cd yamaYT-rag-x2
```

### 2. X API の設定（任意）

X API がなくてもスキルは動作します（Web / Nitter 等でのリサーチにフォールバック）。
設定すると X の最新投稿を検索しやすくなり、**リサーチ品質が上がりやすい**です。

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

Claude Code を起動し、テーマと「X 記事を書いて」「YouTube 台本も作って」などと依頼します。起動したスキルに従い、選択肢や確認に答えながら進めてください。

**X 記事の例**

```
プログラミングスクールの話でX記事を書いて
```

おおむねの流れ（`yamamoto-x-post`）: 設定確認 → リサーチ可否 → X リサーチ → 構成整理 → RAG → 長文生成 → `articles/` へ保存。

**YouTube 台本**は `yamamoto-yt-script` の `SKILL.md` に記載の章立て・分量・ Shorts 方針に従います。

## 参考リンク

- [X Developer Portal](https://developer.x.com)
- [X Developer Console](https://console.x.com)
- [X API セットアップ詳細ガイド](https://www.and-and.co.jp/gas-lab/x-twitter-api-start/)
- [503エラー解決ガイド（Pay-Per-Use移行）](https://www.and-and.co.jp/gas-lab/x-twitter-api-503-error/)
- [X API 公式料金ページ](https://docs.x.com/x-api/getting-started/pricing)

## ライセンス

リポジトリは公開されています。スキル定義・ツール・RAG 用テキスト等の利用条件は、利用者の用法に応じて権利者の判断が及ぶ場合があります。**All Rights Reserved**（無断利用・再配布の禁止など、通常の著作権法上の保護）を前提としています。商用利用や再配布が必要な場合は、権利の所在に従って別途確認してください。
