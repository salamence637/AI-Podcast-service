import os
import re
import uuid
from fastapi import APIRouter, HTTPException,Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.services import podcast_generator, tts
import openai
router = APIRouter()
import os 
NEXT_PUBLIC_BASE_URL = os.getenv("NEXT_PUBLIC_BASE_URL")
class PodcastRequest(BaseModel):
    topic: str
    tts: bool = False  # 是否生成语音
    


class APIKeyRequest(BaseModel):
    user_api_key: str

@router.post("/validate_api")
async def validate_api_key(request_data: APIKeyRequest):
    """
    使用用户提供的 API Key 调用 OpenAI 接口，验证是否有效。
    """
    try:
        # 这里调用一个简单的 OpenAI API（例如列出引擎）来验证 Key
        openai.Engine.list(api_key=request_data.user_api_key)
        return {"valid": True}
    except Exception as e:
        return {"valid": False, "error": str(e)}
def detect_language(text: str) -> str:
    if re.search(r'[\u3040-\u30ff]', text):
        return 'jp'
    elif re.search(r'[\u4e00-\u9fff]', text):
        return 'zh'
    else:
        return 'en'

def sanitize_filename(topic: str) -> str:
    """
    将 topic 转换为合法的文件名，去除非法字符，空格转换为下划线
    如果结果为空则返回 "podcast"
    """
    sanitized = re.sub(r'[^\w\- ]', '', topic).strip().replace(' ', '_')
    return sanitized if sanitized else "podcast"

@router.post("/generate")
async def generate_podcast_endpoint(request: Request, podcast_request: PodcastRequest):
    try:
        text = podcast_generator.generate_podcast_text(podcast_request.topic)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    result = {"text": text}
    
    if podcast_request.tts:
        lang = detect_language(podcast_request.topic)
        tts_lang = "zh-cn" if lang == "zh" else "ja" if lang == "jp" else "en"
        audio_fp, timestamps = await tts.convert_text_to_speech(text, lang=tts_lang)
        
        
        # 保存音频的文件夹（容器内的 /app/audio，通过 Docker 卷映射到本地主机）
        audio_dir = "audio"
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)
        
        # 使用 topic 名称作为文件名，并确保文件名合法
        base_name = sanitize_filename(podcast_request.topic)
        file_name = f"{base_name}.mp3"
        file_path = os.path.join(audio_dir, file_name)
        
        # 如果文件已存在，可以考虑追加一个唯一标识
        if os.path.exists(file_path):
            file_name = f"{base_name}_{uuid.uuid4().hex[:8]}.mp3"
            file_path = os.path.join(audio_dir, file_name)
        
        with open(file_path, "wb") as f:
            f.write(audio_fp.read())
        
        # 生成访问音频文件的 URL
        # audio_url = str(request.url_for("audio", path=file_name))
        # NEXT_PUBLIC_BASE_URL
        audio_url = f"{NEXT_PUBLIC_BASE_URL}/audio/{file_name}"
        result["audio_file"] = audio_url
        result["timestamps"] = timestamps
    return JSONResponse(content=result)