from pydantic import BaseModel
from typing import Optional

class ClipSearchRequest(BaseModel):
    vector: list
    appCodes: Optional[list] = None
    startTime: Optional[int] = None
    endTime: Optional[int] = None
    phoneIds: Optional[list] = None
    maxNum: Optional[int] = 25