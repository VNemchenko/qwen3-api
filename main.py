import re
import logging
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from llama_cpp import Llama
from config import MODEL_PATH, API_KEY


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()
logger.info("Loading model from %s", MODEL_PATH)
llm = Llama(model_path=MODEL_PATH, chat_format="chatml", n_ctx=4096)
logger.info("Model loaded successfully")

def remove_think_blocks(text: str) -> str:
    """Удаляет всё между <think>...</think> включая сами теги."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

def verify_token(request: Request):
    auth = request.headers.get("Authorization", "")
    logger.info("Authorization header received: %s", auth)
    if not auth.startswith("Bearer "):
        logger.warning("Missing or malformed Authorization header")
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = auth.split(" ")[1]
    if token != API_KEY:
        logger.warning("Invalid API token provided")
        raise HTTPException(status_code=401, detail="Unauthorized")

    logger.info("Token verified successfully")

@app.post("/v1/chat/completions")
async def chat(request: Request, authorized: None = Depends(verify_token)):
    body = await request.json()
    logger.info("Received chat request")
    logger.info("Request body: %s", body)

    messages = body.get("messages", [])
    temperature = body.get("temperature", 0.7)
    max_tokens = body.get("max_tokens", 1024)
    logger.info(
        "messages=%s temperature=%s max_tokens=%s",
        messages,
        temperature,
        max_tokens,
    )

    try:
        logger.info("Generating completion with %d message(s)", len(messages))
        result = llm.create_chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        logger.info("Model response: %s", result)

        # 👇 чистим content от <think>...</think>
        if "choices" in result:
            for choice in result["choices"]:
                msg = choice.get("message", {})
                if "content" in msg:
                    msg["content"] = remove_think_blocks(msg["content"])

        logger.info("Returning cleaned completion result")
        return JSONResponse(content=result)

    except Exception as e:
        logger.exception("Error during chat completion")
        return JSONResponse(status_code=500, content={"error": str(e)})
