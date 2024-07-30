from pydantic import BaseModel

class LanceDBDeleteRequest(BaseModel):
    key: str
    value: str