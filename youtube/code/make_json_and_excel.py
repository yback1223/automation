import json, re
import pandas as pd


def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def convert_duration(duration):
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    if not match:
        return "00:00:00"

    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0

    return f"{hours:02}:{minutes:02}:{seconds:02}"

def clear_json(youtube_crawled_file, youtube_output_json_file, youtube_output_excel_file, keyword_code_mapped_file):
    try:
        youtube_crawled_data = load_json(youtube_crawled_file)

        keyword_code_mapped_data = load_json(keyword_code_mapped_file)

        extracted_data = []

        for category, videos in youtube_crawled_data.items():
            for video in videos:
                snippet = video.get("snippet", {})
                content_details = video.get("contentDetails", {})
                statistics = video.get("statistics", {})
                search_keyword = video.get("search_query", "")
                job_hir_classes = []

                for keyword_data in keyword_code_mapped_data:
                    if category in keyword_data['category'] and search_keyword in keyword_data['search_keyword']:
                        job_hir_classes = keyword_data['job_hir_classes']
                        break

                row = {
                    "카테고리": category,
                    "검색키워드": search_keyword,
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
                    "썸네일 URL": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                    "고용직업분류코드": job_hir_classes
                }
                extracted_data.append(row)

        df = pd.DataFrame(extracted_data, columns=[
            "카테고리", "고용직업분류코드", "검색키워드", "영상 URL", "제목", "채널명", "설명", "게시일", "조회수", "좋아요 수", "댓글 수", "영상 길이", "화질", "썸네일 URL"
        ])
        df.to_excel(youtube_output_excel_file, index=False)

        save_json(extracted_data, youtube_output_json_file)
    except Exception as e:
        print(f"JSON을 JSON과 Excel로 변환하는 중 오류 발생: {e}")

clear_json(
    youtube_crawled_file='youtube_results.json',
    youtube_output_json_file='youtube_results_cleared.json',
    youtube_output_excel_file='youtube_results_cleared.xlsx',
    keyword_code_mapped_file='keyword_mapping.json'
)