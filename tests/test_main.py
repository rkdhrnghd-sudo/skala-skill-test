from fastapi.testclient import TestClient

from app.ai import GUIDES, _key
from app.main import app

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
