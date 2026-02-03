from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi import HTTPException
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, List, Dict

from qwen import generate_dialog_script
from tts import tts_manager

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
    model: Optional[str] = "deepseek-v3.2"


@app.post("/generate-script")
async def generate_script(req: GenerateRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="text 为空")

    try:
        result = generate_dialog_script(req.text, style=req.style or "casual", participants=req.participants or 2, model=req.model or "deepseek-v3.2")
        return {"ok": True, "script": result, "token_usage": result.get("token_usage", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})}
    except Exception as e:
        return {"ok": False, "error": str(e), "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}}


class SaveDialogRequest(BaseModel):
    content: str
    filename: str
    script: dict


class TTSRequest(BaseModel):
    text: str
    speaker_id: str
    audio_format: Optional[str] = "mp3"


class ProcessDialogRequest(BaseModel):
    dialog: List[Dict]


class CreatePodcastRequest(BaseModel):
    dialog: List[Dict]
    podcast_title: str


class UpdateSpeakerRequest(BaseModel):
    speaker_id: str
    voice_id: str
    style: Optional[str] = "default"


@app.post("/save-dialog")
async def save_dialog(req: SaveDialogRequest):
    try:
        # 创建result目录
        result_dir = current_dir.parent / "results"
        result_dir.mkdir(exist_ok=True)
        
        # 保存文本文件
        file_path = result_dir / req.filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(req.content)
        
        return {"ok": True, "message": "对话已保存"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/generate-speech")
async def generate_speech(req: TTSRequest):
    """
    生成语音文件
    """
    try:
        audio_path = tts_manager.generate_speech(req.text, req.speaker_id, req.audio_format)
        if not audio_path:
            raise HTTPException(status_code=500, detail="语音生成失败")
        return {"ok": True, "audio_path": audio_path}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/process-dialog-tts")
async def process_dialog_tts(req: ProcessDialogRequest):
    """
    处理对话，为每个对话生成语音
    """
    try:
        processed_dialog = tts_manager.process_dialog(req.dialog)
        return {"ok": True, "dialog": processed_dialog}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/create-podcast")
async def create_podcast(req: CreatePodcastRequest):
    """
    创建完整的播客节目
    """
    try:
        podcast_path = tts_manager.create_podcast(req.dialog, req.podcast_title)
        if not podcast_path:
            raise HTTPException(status_code=500, detail="播客创建失败")
        return {"ok": True, "podcast_path": podcast_path}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.get("/get-speakers")
async def get_speakers():
    """
    获取可用的说话人列表
    """
    try:
        speakers = tts_manager.get_speakers()
        return {"ok": True, "speakers": speakers}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/update-speaker")
async def update_speaker(req: UpdateSpeakerRequest):
    """
    更新说话人配置
    """
    try:
        success = tts_manager.update_speaker(req.speaker_id, req.voice_id, req.style)
        if not success:
            raise HTTPException(status_code=400, detail="说话人更新失败")
        return {"ok": True, "message": "说话人更新成功"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=914)