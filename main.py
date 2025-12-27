import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
    "http://localhost",
    "http://127.0.0.1",
]
CORS_ORIGINS = os.getenv("CORS_ORIGINS", ",".join(default_origins)).split(",")

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
    max_tokens: int = 256
    temperature: float = 0.7


class GenerateResponse(BaseModel):
    """テキスト生成レスポンスモデル"""
    result: str


@app.get("/health")
def health_check():
    """ヘルスチェック"""
    return {"status": "ok"}


@app.post("/generate", response_model=GenerateResponse)
def generate_text(request: GenerateRequest):
    """
    GenAIを使用してテキストを生成
    
    Args:
        request: GenerateRequest
        
    Returns:
        GenerateResponse
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=request.prompt,
        )
        
        return GenerateResponse(result=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
