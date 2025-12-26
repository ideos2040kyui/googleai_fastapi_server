# GenAI FastAPI Server

Back4Appで簡単にデプロイできるFastAPIサーバー。Google GenAIを使用してテキスト生成を行うAPI。

## セットアップ

### ローカル開発

1. 依存パッケージをインストール
```bash
pip install -r requirements.txt
```

2. `.env` ファイルを作成（`.env.example` を参考に）
```bash
cp .env.example .env
```

3. `.env` にGenAI APIキーを設定
```
GENAI_API_KEY=your_actual_api_key
```

4. サーバーを起動
```bash
python main.py
```

サーバーは `http://localhost:8000` で起動します。

### Back4Appへのデプロイ

Back4AppはDocker コンテナを使用してアプリケーションをデプロイします。

1. Back4Appアカウントを作成・ログイン

2. 新しいコンテナアプリを作成
   - "Create New App" → "Containers" を選択

3. GitHubリポジトリを連携
   - このリポジトリをGitHubに上げ、Back4Appと接続

4. 環境変数を設定
   - Back4Appダッシュボード → Settings → Environment Variables
   - `GENAI_API_KEY` に取得したAPIキーを設定

5. デプロイ（自動）
   - リポジトリにプッシュすると自動的にDockerイメージをビルドしてデプロイされます
   - Dockerfileがプロジェクトルートにあることを確認

## APIエンドポイント

### 1. ヘルスチェック
```
GET /health
```

レスポンス:
```json
{"status": "ok"}
```

### 2. テキスト生成
```
POST /generate
```

リクエスト:
```json
{
    "prompt": "日本の首都は？",
    "max_tokens": 256,
    "temperature": 0.7
}
```

レスポンス:
```json
{
    "result": "日本の首都は東京です..."
}
```

**パラメータ:**
- `prompt` (必須): 生成対象のプロンプト
- `max_tokens` (オプション): 最大トークン数（デフォルト: 256）
- `temperature` (オプション): 出力のランダム性（0.0-1.0、デフォルト: 0.7）

※ 現在のバージョンではモデル側で自動的に最適化されるため、APIレスポンスでパラメータが反映されない場合があります

## テスト方法

```bash
# ヘルスチェック
curl http://localhost:8000/health

# テキスト生成
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, how are you?", "max_tokens": 100}'
```

## 環境変数

- `GENAI_API_KEY`: Google GenAI APIキー（必須）
- `PORT`: サーバーポート（デフォルト: 8000）

## 必要なもの

- Python 3.8以上
- Google GenAI APIキー（https://makersuite.google.com/app/apikey で取得）

## 依存パッケージ

- fastapi: Webフレームワーク
- uvicorn: ASGIサーバー
- pydantic: データバリデーション
- google-genai: Google GenAI API（最新版）
- python-dotenv: 環境変数管理
