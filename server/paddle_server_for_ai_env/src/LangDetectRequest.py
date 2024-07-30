from pydantic import BaseModel


class LangDetectRequest(BaseModel):
    text: str

