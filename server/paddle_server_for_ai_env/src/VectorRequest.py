from pydantic import BaseModel


class VectorRequest(BaseModel):
    audio_file: str

