from pydantic import BaseModel
from typing import Optional

class ClipToVectorRequest(BaseModel):
    imagePath: Optional[str] = None
    text: Optional[str] = None