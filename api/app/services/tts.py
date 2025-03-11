import asyncio
import os
import re
from io import BytesIO

try:
    import edge_tts
    USE_EDGE_TTS = True
except ImportError:
    USE_EDGE_TTS = False

from pydub import AudioSegment

def sync_convert_text_to_speech(text: str, lang: str) -> BytesIO:
    """
    gTTS 同步方式转换文本为语音（回退方案）
    """
    from gtts import gTTS
    tts = gTTS(text=text, lang=lang)
    audio_fp = BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    return audio_fp

def extract_speaker_info(line: str, speakers: dict) -> (str, str, str):
    """
    从一行文本中提取说话人、对话内容和性别。
    
    - 如果匹配 "speaker: content"（支持全角/半角冒号），则提取 speaker_tag 与 content。
    - 如果 speaker_tag 中包含 "男主播" 或 "女主播"，则直接设置 gender，并去除对应前缀。
    - 如果没有明确标记，则检查 speakers 字典；如果该 speaker 之前未出现，
      则默认先出现为 "male"，后出现为 "female"。
    - 如果行中没有冒号，则认为整行为对话内容，speaker 为空字符串，默认 gender 为 "male"。
    
    返回一个元组 (speaker, content, gender)。
    """
    m = re.match(r"^(.*?)[：:]\s*(.*)$", line)
    if m:
        speaker_tag = m.group(1).strip()
        content = m.group(2).strip()
        gender = None
        if "男主播" in speaker_tag:
            gender = "male"
            speaker_tag = speaker_tag.replace("男主播", "").strip()
        elif "女主播" in speaker_tag:
            gender = "female"
            speaker_tag = speaker_tag.replace("女主播", "").strip()
        if not gender:
            if speaker_tag in speakers:
                gender = speakers[speaker_tag]
            else:
                gender = "male" if len(speakers) == 0 else "female"
        speakers[speaker_tag] = gender
        return speaker_tag, content, gender
    else:
        return "", line, "male"

async def convert_text_to_speech(text: str, lang: str) -> (BytesIO, list):
    """
    将包含对话的文本转换为语音，并返回一个元组：
        (合成后的 MP3 音频 BytesIO 对象, 每行的起始时间数组 timestamps)
    
    逻辑说明：
    - 按行拆分文本，每行通过 extract_speaker_info() 提取 speaker、content 与 gender；
    - 使用 edge-tts（如果可用，否则回退到 gTTS）分别合成每行语音，并用 pydub 拼接；
    - 在各段之间加入 300 毫秒的静音（除最后一行外）；
    - 累计各段时长，得到每行起始时间（单位秒）。
    
    参数 lang：
      - 中文传 "zh-cn"
      - 日文传 "ja"
      - 英文传 "en"
    """
    lines = text.splitlines()
    segments = []
    timestamps = []  # 每行起始时间（秒）
    cumulative_time = 0.0
    speakers = {}  # 用于记录每个说话人的性别
    silence_duration_ms = 300
    silence_segment = AudioSegment.silent(duration=silence_duration_ms)
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # 记录当前行起始时间
        timestamps.append(round(cumulative_time, 2))
        
        # 提取 speaker、content 与 gender
        speaker, content, gender = extract_speaker_info(line, speakers)
        if not content:
            continue

        # 根据语言和性别选择语音
        if lang == "zh-cn":
            voice = "zh-CN-YunxiNeural" if gender == "male" else "zh-CN-XiaoxiaoNeural"
        elif lang == "ja":
            voice = "ja-JP-KeitaNeural" if gender == "male" else "ja-JP-NanamiNeural"
        else:
            voice = "en-US-GuyNeural" if gender == "male" else "en-US-JennyNeural"
        
        # 合成这一行的语音
        if USE_EDGE_TTS:
            temp_filename = f"temp_segment_{i}.mp3"
            await edge_tts.Communicate(content, voice).save(temp_filename)
            segment = AudioSegment.from_file(temp_filename, format="mp3")
            os.remove(temp_filename)
        else:
            from gtts import gTTS
            tts_obj = gTTS(text=content, lang=lang)
            temp_bytes = BytesIO()
            tts_obj.write_to_fp(temp_bytes)
            temp_bytes.seek(0)
            segment = AudioSegment.from_file(temp_bytes, format="mp3")
        segments.append(segment)
        cumulative_time += segment.duration_seconds
        
        # 如果不是最后一行，则加上静音
        if i < len(lines) - 1:
            segments.append(silence_segment)
            cumulative_time += silence_duration_ms / 1000.0

    if not segments:
        combined = AudioSegment.silent(duration=1000)
    else:
        combined = segments[0]
        for seg in segments[1:]:
            combined += seg

    out_bytes = BytesIO()
    combined.export(out_bytes, format="mp3")
    out_bytes.seek(0)
    return out_bytes, timestamps
