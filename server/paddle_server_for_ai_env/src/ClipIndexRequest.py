from pydantic import BaseModel

class ClipIndexRequest(BaseModel):
    appCode: str
    phoneId: str
    time: int
    fileId: int
    vector: list