from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pathlib import Path

# 获取当前文件所在目录（app目录）
current_dir = Path(__file__).parent
static_dir = current_dir / "static"

app = FastAPI(title="播客对话生成器")

# 挂载静态文件目录 - 使用相对路径
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    # HTML文件在 static/html/ 目录下
    index_path = static_dir / "html" / "index.html"
    return FileResponse(str(index_path))

@app.get("/podcast-generator", response_class=HTMLResponse)
async def read_podcast_generator():
    podcast_path = static_dir / "html" / "podcast-generator.html"
    return FileResponse(str(podcast_path))

# 添加健康检查端点
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "current_dir": str(current_dir),
        "static_dir": str(static_dir)
    }

@app.post("/api/generate-podcast")
async def generate_podcast(text: str, style: str = "casual", participants: int = 2):
    return {"message": "API端点已准备就绪", "received": {"text": text, "style": style, "participants": participants}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)