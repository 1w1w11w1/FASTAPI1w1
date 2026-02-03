from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi import HTTPException
from pydantic import BaseModel
from pathlib import Path
from typing import Optional

from qwen import generate_dialog_script

current_dir = Path(__file__).parent
static_dir = current_dir / "static"

app = FastAPI(title="播客对话生成器")

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_path = static_dir / "html" / "index.html"
    return FileResponse(str(index_path))

@app.get("/podcast-generator", response_class=HTMLResponse)
async def read_podcast_generator():
    podcast_path = static_dir / "html" / "podcast-generator.html"
    return FileResponse(str(podcast_path))

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "current_dir": str(current_dir),
        "static_dir": str(static_dir)
    }


class GenerateRequest(BaseModel):
    text: str
    style: Optional[str] = "casual"
    participants: Optional[int] = 2


@app.post("/generate-script")
async def generate_script(req: GenerateRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="text 为空")

    try:
        result = generate_dialog_script(req.text, style=req.style or "casual", participants=req.participants or 2)
        return {"ok": True, "script": result}
    except Exception as e:
        return {"ok": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)