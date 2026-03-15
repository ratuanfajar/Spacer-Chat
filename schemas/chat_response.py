# schemas/models.py
from pydantic import BaseModel, Field
from typing import Optional, List

class ChatResponse(BaseModel):
    content: str = Field(
        description="Gabungkan inti jawaban, penjelasan bertahap, contoh sederhana, ringkasan, dan pertanyaan reflektif."
    )
    suggested_questions: Optional[List[str]] = Field(
        default=None, 
        description="Maksimal 3 pertanyaan lanjutan yang singkat dan relevan terkait materi."
    )