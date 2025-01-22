import json, re
import pandas as pd


def convert_duration(duration):
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    if not match:
        return "00:00:00"

    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0

    return f"{hours:02}:{minutes:02}:{seconds:02}"


def json_to_excel(json_file, excel_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            json_data = json.load(file)

        extracted_data = []

        for category, videos in json_data.items():
            for video in videos:
                snippet = video.get("snippet", {})
                content_details = video.get("contentDetails", {})
                statistics = video.get("statistics", {})

                row = {
                    "카테고리": category,
                    "검색키워드": video.get("search_query", ""),
                    "영상 URL": f'https://www.youtube.com/watch?v={video.get("id", "")}',
                    "제목": snippet.get("title", ""),
                    "채널명": snippet.get("channelTitle", ""),
                    "설명": snippet.get("description", ""),
                    "게시일": snippet.get("publishedAt", ""),
                    "조회수": statistics.get("viewCount", ""),
                    "좋아요 수": statistics.get("likeCount", ""),
                    "댓글 수": statistics.get("commentCount", ""),
                    "영상 길이": convert_duration(content_details.get("duration", "")),
                    "화질": content_details.get("definition", ""),
                    "썸네일 URL": snippet.get("thumbnails", {}).get("high", {}).get("url", "")
                }

                extracted_data.append(row)

        # 데이터프레임 생성
        df = pd.DataFrame(extracted_data, columns=[
            "카테고리", "검색키워드", "영상 URL", "제목", "채널명", "설명", "게시일", "조회수", "좋아요 수", "댓글 수", "영상 길이", "화질", "썸네일 URL"
        ])

        # 엑셀 파일로 저장
        df.to_excel(excel_file, index=False)
        print(f"Excel 파일이 성공적으로 생성되었습니다: {excel_file}")

    except Exception as e:
        print(f"JSON을 Excel로 변환하는 중 오류 발생: {e}")

# JSON 파일과 출력할 엑셀 파일 경로
json_file = 'youtube_results.json'
excel_file = 'youtube_results.xlsx'

# JSON 데이터를 Excel로 변환
json_to_excel(json_file, excel_file)
