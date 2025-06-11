import re
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from llama_cpp import Llama
from config import MODEL_PATH, API_KEY


app = FastAPI()
llm = Llama(model_path=MODEL_PATH, chat_format="chatml", n_ctx=4096)

def remove_think_blocks(text: str) -> str:
    """Удаляет всё между <think>...</think> включая сами теги."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

def verify_token(request: Request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer ") or auth.split(" ")[1] != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/v1/chat/completions")
async def chat(request: Request, authorized: None = Depends(verify_token)):
    body = await request.json()
    messages = body.get("messages", [])
    temperature = body.get("temperature", 0.7)
    max_tokens = body.get("max_tokens", 1024)

    try:
        result = llm.create_chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # 👇 чистим content от <think>...</think>
        if "choices" in result:
            for choice in result["choices"]:
                msg = choice.get("message", {})
                if "content" in msg:
                    msg["content"] = remove_think_blocks(msg["content"])

        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
