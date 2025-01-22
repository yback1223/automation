# YouTube API 데이터 크롤링 결과 변수 설명

이 문서는 YouTube Data API를 통해 얻은 비디오 데이터 결과의 주요 변수와 그 의미를 설명합니다.

## 데이터 구조 및 키 설명

### 1. 상위 키
- **kind**: 리소스의 유형.
  - 예: "youtube#video"는 이 항목이 비디오임을 나타냅니다.
- **etag**: 리소스의 고유 해시 값.
  - API 응답이 변경되었는지 확인하는 데 사용됩니다.
- **id**: 비디오의 고유 ID.
  - 예: `-Bnnr1HyAEY` (YouTube URL 생성에 사용: `https://www.youtube.com/watch?v=-Bnnr1HyAEY`).

### 2. `snippet` (비디오 메타데이터)
비디오의 메타데이터 정보를 포함합니다.

| 키                     | 설명                                                                                     |
|------------------------|------------------------------------------------------------------------------------------|
| `publishedAt`          | 비디오가 게시된 날짜와 시간 (ISO 8601 형식).                                               |
| `channelId`            | 비디오를 업로드한 채널의 고유 ID.                                                        |
| `title`                | 비디오 제목.                                                                             |
| `description`          | 비디오 설명.                                                                             |
| `thumbnails`           | 썸네일 이미지 URL과 크기 (`default`, `medium`, `high`, `standard`, `maxres`).             |
| `channelTitle`         | 비디오를 게시한 채널 이름.                                                               |
| `categoryId`           | 비디오 카테고리 ID (예: 22는 "People & Blogs").                                         |
| `liveBroadcastContent` | 라이브 방송 여부 (`none`: 라이브 아님).                                                  |
| `localized`            | 로컬라이즈된 제목과 설명.                                                                |
| `defaultAudioLanguage` | 비디오의 기본 오디오 언어 (ISO 639-1 코드 형식).                                        |

### 3. `contentDetails` (비디오 콘텐츠 세부 정보)
비디오의 기술적 정보와 상세 콘텐츠 관련 데이터를 포함합니다.

| 키                | 설명                                                                                     |
|-------------------|------------------------------------------------------------------------------------------|
| `duration`        | 비디오 길이 (ISO 8601 형식). 예: `PT5M40S`는 5분 40초.                                    |
| `dimension`       | 비디오 차원 (`2d`, `3d`).                                                                 |
| `definition`      | 비디오 화질 (`hd`, `sd`).                                                                  |
| `caption`         | 자막 여부 (`true`/`false`).                                                              |
| `licensedContent` | 라이선스 콘텐츠 여부.                                                                     |
| `projection`      | 비디오 투영 방식 (`rectangular`: 기본 2D).                                               |

### 4. `statistics` (비디오 통계 데이터)

| 키              | 설명                                                                                     |
|-----------------|------------------------------------------------------------------------------------------|
| `viewCount`     | 비디오 조회 수.                                                                          |
| `likeCount`     | 비디오 좋아요 수.                                                                       |
| `favoriteCount` | 비디오 즐겨찾기 수 (항상 0으로 설정됨).                                                 |
| `commentCount`  | 비디오 댓글 수.                                                                          |

---

## 출처
- [YouTube Data API 문서](https://developers.google.com/youtube/v3/docs)
  - [Search: list](https://developers.google.com/youtube/v3/docs/search/list): 비디오 검색 API.
  - [Videos: list](https://developers.google.com/youtube/v3/docs/videos/list): 비디오 세부 정보 조회 API.

---