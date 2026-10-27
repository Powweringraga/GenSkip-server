import os
import re
from fastapi import FastAPI, HTTPException
from google import genai
from pydantic import BaseModel

app = FastAPI(title="GenSkip AI Proxy Server", version="1.1.0")

# API Key lấy từ Environment Variables trên Vercel Dashboard
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY) if API_KEY else None


# --- REQUEST SCHEMAS ---
class SummarizeRequest(BaseModel):
  text: str


class SelectChoiceRequest(BaseModel):
  context: str  # Đoạn thoại gần nhất để lấy ngữ cảnh
  options: list[str]  # Danh sách các câu lựa chọn tìm thấy trên màn hình


# --- ENDPOINTS ---


@app.get("/")
def read_root():
  return {"status": "ok", "message": "GenSkip Proxy Server is running on Vercel!"}


@app.post("/summarize")
def summarize_lore(req: SummarizeRequest):
  if not client:
    raise HTTPException(status_code=500, detail="Chưa cấu hình GEMINI_API_KEY!")

  if not req.text or len(req.text.strip()) < 10:
    return {"summary": "Không tìm thấy đoạn thoại đủ dài để tóm tắt."}

  prompt = f"""
    Bạn là trợ lý game Genshin Impact. Hãy tóm tắt ngắn gọn, súc tích (dưới 25 từ) nội dung đoạn thoại sau bằng tiếng Việt:

    "{req.text}"
    """
  try:
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt
    )
    return {
        "summary": response.text.strip() if response.text else "Không có dữ liệu."
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Lỗi gọi Gemini API: {str(e)}")


@app.post("/select_choice")
def select_best_choice(req: SelectChoiceRequest):
  if not client:
    return {"best_index": 1}

  if not req.options:
    return {"best_index": 1}

  formatted_options = "\n".join(
      [f"{i+1}. {opt}" for i, opt in enumerate(req.options)]
  )

  prompt = f"""
    Bạn là một người chơi Genshin Impact thông minh và tinh tế.
    
    Ngữ cảnh đoạn thoại vừa diễn ra:
    "{req.context}"
    
    Các phương án lựa chọn trên màn hình:
    {formatted_options}
    
    Nhiệm vụ: Hãy chọn ra 1 phương án TỐT NHẤT (ưu tiên: đồng ý giúp đỡ, tăng độ thiện cảm, hoặc lịch sự/hài hước).
    Yêu cầu đầu ra: CHỈ trả về duy nhất 1 con số tương ứng với số thứ tự phương án (ví dụ: 1, 2, hoặc 3). KHÔNG viết thêm bất kỳ từ nào khác.
    """
  try:
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt
    )
    raw_text = response.text.strip() if response.text else "1"

    match = re.search(r"\d+", raw_text)
    if match:
      chosen_index = int(match.group())
      if 1 <= chosen_index <= len(req.options):
        return {"best_index": chosen_index}

    return {"best_index": 1}
  except Exception as e:
    print(f"[Select Choice Error] {e}")
    return {"best_index": 1}