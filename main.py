import json
import logging
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, StreamingResponse
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
logger.info("Model loaded successfully: %s", llm)

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

@app.get("/v1/models")
async def list_models(authorized: None = Depends(verify_token)):
    return {
        "object": "list",
        "data": [
            {
                "id": "/models/Qwen3-0.6B-Q8_0.gguf",
                "object": "model",
                "owned_by": "Vitaliy Nemchenko"
            }
        ]
    }


@app.post("/v1/chat/completions")
async def chat(request: Request, authorized: None = Depends(verify_token)):
    body = await request.json()
    logger.info("Received chat request")
    logger.info("Request body: %s", body)

    messages = body.get("messages", [])
    temperature = body.get("temperature", 0.6)
    max_tokens = body.get("max_tokens", 32768)
    stream = body.get("stream", False)
    logger.info(
        "messages=%s temperature=%s max_tokens=%s stream=%s",
        messages,
        temperature,
        max_tokens,
        stream,
    )

    try:
        logger.info("Generating completion with %d message(s)", len(messages))

        if stream:
            def event_stream():
                try:
                    for chunk in llm.create_chat_completion(
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=True
                    ):
                        yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                except Exception as exc:
                    logger.exception("Error during streaming chat completion")
                    yield f"data: {json.dumps({'error': str(exc)}, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(event_stream(), media_type="text/event-stream")

        result = llm.create_chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        logger.info("Model response: %s", result)
        return JSONResponse(content=result)

    except Exception as e:
        logger.exception("Error during chat completion")
        return JSONResponse(status_code=500, content={"error": str(e)})
