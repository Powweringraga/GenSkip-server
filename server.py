import os
import google.genai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Nạp API Key trực tiếp trên Server (Hoặc qua Environment Variable của Server)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6J7TJYfSXSLvT2BbabnskQjxEBibRleEO_W2J7o-8BNOA")
client = genai.Client(api_key=GEMINI_API_KEY)


class LoreRequest(BaseModel):
  text: str


@app.post("/summarize")
def summarize_text(req: LoreRequest):
  if not req.text or len(req.text) < 10:
    return {"summary": "Không tìm thấy đoạn thoại đủ dài để tóm tắt."}

  prompt = (
      "Bạn là trợ lý game Genshin Impact. Hãy tóm tắt ngắn gọn (dưới 25"
      f' từ) nội dung đoạn thoại sau bằng tiếng Việt:\n\n"{req.text}"'
  )

  try:
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt
    )
    summary = response.text.strip() if response.text else "Không có phản hồi."
    return {"summary": summary}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))