from googleapiclient.discovery import build
import json

API_KEY = "AIzaSyADPwBDi4kH7rlaz_lGrvDa-YAyS0FcJoM"

search_queries: dict[str, list[str]] = {
    '공부방법': ['공부 브이로그', '포모도로 기법', '집중 공부 팁'],
    'K-POP 댄스 튜토리얼': ['K-POP 댄스 커버', '아이돌 안무 튜토리얼'],
    'DIY 공예 및 다이어리 꾸미기': ['DIY 공예, 다이어리 꾸미기 아이디어', '핸드메이드 선물'],
    '과학 및 STEM 채널': ['과학 실험', '초보 코딩', 'STEM 상식'],
    '언어 학습 비디오': ['영어 학습', '일본어 기본', '언어 공부'],
    '진로 및 동기부여': ['진로 팁', '대학 지원 도움', '학생 동기부여'],
    '건강 및 웰빙': ['학생 요가', '정신 건강 팁',' 스트레스 완화'],
    '책 리뷰 및 추천': ['청소년 추천 도서', '책 요약', '책 리뷰'],
    '미술 및 디지털 일러스트': ['디지털 페인팅', '드로잉 튜토리얼', '미술 팁'],
    '테크 튜토리얼': ['노션 설정', '초보 코딩', '엑셀 기초'],
    '역사 및 문화': ['한국 역사', '세계 문화 상식', '역사적 사건'],
    '금융 및 재테크': ['저축 팁', '학생 예산 관리', '초보 투자'],
    '환경 지속 가능성': ['친환경 습관', '지속 가능성 아이디어', '업사이클링 프로젝트'],
    '초보 요리': ['쉬운 요리법', '초보 요리', '한국 전통 요리'],
    '자기 계발 및 시간 관리': ['시간 관리 팁', '생산성 팁', '목표 설정'],
    '과학 소설 및 미래학': ['미래 기술', '우주 탐사', '인공지능 설명'],
    '심리학 및 정신 건강': ['자기 인식 팁', '청소년 정신 건강', '심리학 상식'],
    '여행 및 세계 탐험': ['가상 투어', '문화 체험', '여행 브이로그'],
    '공개 연설 및 토론': ['토론 팁', '학생 공개 연설', '설득 기술'],
    '생명 과학 및 건강': ['인체 해부학', '영양 팁', '초보 생물학'],
    '트렌드': ['독파민', '페르소비', 'ai작', '긍생', '친친폼']
}

youtube = build("youtube", "v3", developerKey=API_KEY)

# relevance, viewCount, date, rating

def fetch_videos(search_query, max_results=10, order="relevance"):
    try:
        response = youtube.search().list(
            q=search_query,
            part="snippet",
            type="video",
            maxResults=max_results,
            order=order
        ).execute()

        all_results = []
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]

            # 비디오 상세 정보 가져오기
            video_response = youtube.videos().list(
                part="contentDetails,statistics,snippet",
                id=video_id
            ).execute()

            if video_response["items"]:
                video_details = video_response["items"][0]
                video_details["search_query"] = search_query
                all_results.append(video_details)

        return all_results

    except Exception as e:
        print(f"Error fetching videos for query '{search_query}': {e}")
        return []


def main():
    result_dict = {}

    # 딕셔너리 키별로 검색
    for category, queries in search_queries.items():
        result_dict[category] = []

        for query in queries:
            print(f"Fetching videos for query: {query}")
            videos = fetch_videos(query)
            result_dict[category].extend(videos)

    # JSON 파일로 저장
    with open("youtube_results.json", "w", encoding="utf-8") as json_file:
        json.dump(result_dict, json_file, ensure_ascii=False, indent=4)

    print("Results saved to youtube_results.json")

if __name__ == "__main__":
    main()