from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from app.ai import guide_by_name

app = FastAPI()

TEMPLATES = Path(__file__).parent / "templates"


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
