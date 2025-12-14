from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi import HTTPException

app = FastAPI(title="播客对话生成器")

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    return FileResponse("app/static/html/index.html")

@app.get("/podcast-generator", response_class=HTMLResponse)
async def read_podcast_generator():
    return FileResponse("app/static/html/podcast-generator.html")

# 添加API端点（后续可以在这里添加真正的千问API集成）
@app.post("/api/generate-podcast")
async def generate_podcast(text: str, style: str = "casual", participants: int = 2):
    # 这里后续可以集成千问API
    return {"message": "API端点已准备就绪", "received": {"text": text, "style": style, "participants": participants}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)