from pydantic import BaseModel


class TranslateRequest(BaseModel):
    from_lang: str
    to_lang: str
    text: str

