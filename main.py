import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from google import genai
load_dotenv()  # .env ファイルから環境変数を読み込む

# 環境変数からAPIキーを取得
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
if not GENAI_API_KEY:
    print("WARNING: GENAI_API_KEY environment variable is not set")
    GENAI_API_KEY = "dummy_key"  # ダミーキーでサーバー起動を許可

# CORS設定用のオリジンを環境変数から取得（デフォルトはlocalhost）
default_origins = [
    "http://localhost:50000",
    "http://127.0.0.1",
]
CORS_ORIGINS = os.getenv("CORS_ORIGINS", ",".join(default_origins)).split(",")

# HTTP Basic認証用の認証情報
AUTH_USERNAME = os.getenv("AUTH_USERNAME", "admin")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "password")
security = HTTPBasic()

# GenAIクライアントを初期化
client = genai.Client(api_key=GENAI_API_KEY)

app = FastAPI(title="GenAI FastAPI Server")

# CORS設定（必要に応じて調整）
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    """テキスト生成リクエストモデル"""
    prompt: str


class GenerateResponse(BaseModel):
    """テキスト生成レスポンスモデル"""
    result: str


def verify_auth(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    """
    HTTP Basic認証を検証
    CORS許可オリジンからはスキップ、外部からは認証が必要
    """
    origin = request.headers.get("origin")
    print(f"DEBUG: origin={origin}, CORS_ORIGINS={CORS_ORIGINS}")  # デバッグ出力
    
    # CORS許可オリジンならスキップ
    if origin and origin in CORS_ORIGINS:
        return True
    
    # 外部からのリクエストは認証が必要
    if credentials.username == AUTH_USERNAME and credentials.password == AUTH_PASSWORD:
        return True
    
    raise HTTPException(status_code=401, detail="認証失敗")


@app.get("/health")
def health_check():
    """ヘルスチェック"""
    return {"status": "ok"}


@app.post("/generate", response_model=GenerateResponse)
def generate_text(
    request_body: GenerateRequest,
    request: Request,
    auth: bool = Depends(verify_auth)
):
    """
    GenAIを使用してテキストを生成（最大30回リトライ）
    
    Args:
        request_body: GenerateRequest
        request: HTTPリクエスト
        auth: 認証結果
        
    Returns:
        GenerateResponse
    """
    max_retries = 30
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=request_body.prompt,
            )
            
            return GenerateResponse(result=response.text)
        except Exception as e:
            last_exception = e
            print(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=500, detail=f"Failed after {max_retries} attempts: {str(last_exception)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
