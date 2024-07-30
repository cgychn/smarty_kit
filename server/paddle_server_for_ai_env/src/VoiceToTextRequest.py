import os

from pydantic import BaseModel


class VoiceToTextRequest(BaseModel):
    """
    request body example
    {
        "audio": "/root/a.audio",
        "audio_format": "wav",
        "sample_rate": 16000,
        "lang": "zh_cn",
    }
    """
    audio: os.PathLike
    audio_format: str
    sample_rate: int
    lang: str

