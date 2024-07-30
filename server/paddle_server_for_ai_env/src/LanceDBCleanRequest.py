from pydantic import BaseModel

class LanceDBCleanRequest(BaseModel):
    moreThenFileId: int
    phoneId: str