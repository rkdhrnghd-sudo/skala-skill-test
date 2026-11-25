# 분리배출 도우미

사진을 올리거나 이름을 적으면 분리배출 방법을 알려 주는 앱. 팀원 A가 바꾼 소개: 사진 없이 이름으로 찾습니다. 팀원 B가 바꾼 소개: 정부 지침을 근거로 알려 줍니다.

## 약속 (초안)

| 주소 | 보내는 값 | 받는 값 |
|---|---|---|
| `GET /` | 없음 | 첫 화면 |
| `GET /health` | 없음 | `{"status": "ok"}` |
| `GET /api/guide` | `?name=페트병` | `name`, `category`, `steps`(목록), `source` |
| `POST /api/photo` | 사진 파일 `file` | 위와 같음 |

`GET /api/guide`: 이름이 비면 400, 모르는 이름이면 404이고 `{"detail": "안내 문구"}`를 받음.
`POST /api/photo`는 아직 없음.

함수 (`app/ai.py`): `guide_by_name(name)`, `guide_by_photo(image)`

## 파일 담당

| 파일 | 담당 |
|---|---|
| `app/main.py` | 백엔드 |
| `app/ai.py` | AI |
| `app/templates/` | 프론트엔드 |
| `README.md` | 기획 |

## 만들 순서

이름으로 찾기 → 사진으로 찾기(가짜 답) → 진짜 AI 연결
