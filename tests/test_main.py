from fastapi.testclient import TestClient

from app import ai
from app.ai import GUIDES, _key
from app.main import MAX_PHOTO_MB, app

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_index():
    res = client.get("/")
    assert res.status_code == 200
    assert "분리배출 도우미" in res.text


def test_guide():
    res = client.get("/api/guide", params={"name": "페트병"})
    assert res.status_code == 200
    data = res.json()
    assert set(data) == {"name", "category", "steps", "source"}
    assert data["name"] == "투명 페트병"
    assert data["steps"] and data["source"]


def test_guide_ignores_spaces_and_case():
    for name in [" 투명페트병 ", "pet병"]:
        assert client.get("/api/guide", params={"name": name}).json()["name"] == "투명 페트병"


def test_guide_broken_bottle_is_not_bottle():
    res = client.get("/api/guide", params={"name": "깨진 유리병"})
    assert res.json()["name"] == "깨진 유리"


def test_guide_not_found():
    res = client.get("/api/guide", params={"name": "없는물건"})
    assert res.status_code == 404
    assert isinstance(res.json()["detail"], str)


def test_guide_empty_name():
    for url in ["/api/guide", "/api/guide?name=%20"]:
        assert client.get(url).status_code == 400


def test_guide_names_do_not_overlap():
    words = [_key(w) for g in GUIDES for w in [g["name"], *g["aliases"]]]
    assert len(words) == len(set(words))


def test_photo():
    for image in [b"\xff\xd8\xff\xe0", b"\x89PNG\r\n\x1a\n", b"RIFF\x00\x00\x00\x00WEBP"]:
        res = client.post("/api/photo", files={"file": ("photo", image)})
        assert res.status_code == 200
        data = res.json()
        assert set(data) == {"name", "category", "steps", "source", "fake"}
        assert data["name"] and data["steps"] and data["source"]


def test_photo_missing_or_empty():
    assert client.post("/api/photo").status_code == 400
    assert client.post("/api/photo", files={"file": ("a.jpg", b"")}).status_code == 400


def test_photo_not_a_photo():
    res = client.post("/api/photo", files={"file": ("a.jpg", b"hello", "image/jpeg")})
    assert res.status_code == 415
    assert isinstance(res.json()["detail"], str)


def test_photo_too_big():
    image = b"\xff\xd8\xff" + b"0" * (MAX_PHOTO_MB * 1024 * 1024)
    assert client.post("/api/photo", files={"file": ("a.jpg", image)}).status_code == 413


def test_photo_unknown(monkeypatch):
    monkeypatch.setattr(ai, "_name_from_photo", lambda image: "없는물건")
    assert client.post("/api/photo", files={"file": ("a.jpg", b"\xff\xd8\xff")}).status_code == 404
