from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import HTMLResponse

from app.ai import guide_by_name, guide_by_photo

app = FastAPI()

TEMPLATES = Path(__file__).parent / "templates"
MAX_PHOTO_MB = 10


def _is_photo(data):
    return (
        data.startswith((b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n"))
        or (data[:4] == b"RIFF" and data[8:12] == b"WEBP")
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index():
    return (TEMPLATES / "index.html").read_text(encoding="utf-8")


@app.get("/api/guide")
def guide(name: str = ""):
    if not name.strip():
        raise HTTPException(400, "이름을 적어 주세요.")
    result = guide_by_name(name)
    if result is None:
        raise HTTPException(404, "아직 모르는 이름이에요. 다른 이름으로 찾아 보세요.")
    return result


@app.post("/api/photo")
def photo(file: UploadFile | None = None):
    if file is None or not file.size:
        raise HTTPException(400, "사진을 골라 주세요.")
    if file.size > MAX_PHOTO_MB * 1024 * 1024:
        raise HTTPException(413, f"사진이 너무 커요. {MAX_PHOTO_MB}MB까지 올릴 수 있어요.")
    image = file.file.read()
    if not _is_photo(image):
        raise HTTPException(415, "JPG, PNG, WebP 사진만 올릴 수 있어요.")
    result = guide_by_photo(image)
    if result is None:
        raise HTTPException(404, "사진에서 찾지 못했어요. 이름으로 찾아 보세요.")
    return result
