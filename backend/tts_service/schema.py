from pydantic import BaseModel, Field

# ---------- Request Model ----------
class TTSRequest(BaseModel):
    text: str
    speed: float = Field(1.0, ge=0.5, le=2.0)