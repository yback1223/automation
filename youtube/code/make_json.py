# youtube/code/make_json.py

import json

def create_structured_description(data):
    sections = []
    
    # 기본 정보 섹션 추가 (YouTube 데이터에 맞게 재정의)
    basic_info = []
    if basic_info:
        sections.append("【기본 정보】\n\n" + "\n\n".join(basic_info) + "\n\n")
    
    # 영상 설명 추가
    if data.get('snippet', {}).get('description'):
        section = "【영상 설명】\n\n"
        section += f"■ 내용\n{data['snippet']['description']}\n\n"
        sections.append(section)
    
    return "".join(sections)

def convert_duration_to_hhmmss(duration):
    # 초기값 설정
    hours = 0
    minutes = 0
    seconds = 0
    
    # "PT" 제거하고 시간 단위 파싱
    if duration.startswith("PT"):
        time_str = duration[2:]  # "PT" 제거
        
        # 시간(H) 추출
        if "H" in time_str:
            h_index = time_str.find("H")
            hours_part = time_str[:h_index]
            if hours_part:
                hours = int(hours_part)
            time_str = time_str[h_index + 1:]
        
        # 분(M) 추출
        if "M" in time_str:
            m_index = time_str.find("M")
            minutes_part = time_str[:m_index]
            if minutes_part:
                minutes = int(minutes_part)
            time_str = time_str[m_index + 1:]
        
        # 초(S) 추출
        if "S" in time_str:
            s_index = time_str.find("S")
            seconds_part = time_str[:s_index]
            if seconds_part:
                seconds = int(seconds_part)
    
    # HH:MM:SS 형식으로 포맷팅
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# JSON 파일 경로 지정
input_file = "youtube_results.json"
output_file = "youtube_courses_to_db.json"

# JSON 파일 읽기
try:
    with open(input_file, "r", encoding="utf-8") as f:
        youtube_data = json.load(f)
    # 딕셔너리인지 확인
    if not isinstance(youtube_data, dict):
        raise ValueError("JSON 파일의 최상위 구조는 딕셔너리여야 합니다.")
except FileNotFoundError:
    print(f"Error: {input_file} 파일을 찾을 수 없습니다.")
    exit(1)
except json.JSONDecodeError:
    print(f"Error: {input_file} 파일의 JSON 형식이 잘못되었습니다.")
    exit(1)
except ValueError as e:
    print(f"Error: {e}")
    exit(1)

courses = []

for category, videos in youtube_data.items():
    for input_data in videos:
        try:
            description = input_data.get("snippet", {}).get("description", "")
            summarized_description = description[:100] + "..." if len(description) > 100 else description
            
            course = {
                "id": f"{input_data.get('id', '')}_youtube",
                "data_source": "youtube",
                "student_type": ["초", "중", "고"],
                "location": "온라인",
                "rough_location": "",
                "corp_type": "개인사업장",
                "bigCategory": category,
                "smallCategory": "",
                "image": input_data.get("snippet", {}).get("thumbnails", {}).get("high", {}).get("url", ""),
                "course_name": input_data.get("snippet", {}).get("title", ""),
                "summarizedDescription": summarized_description,
                "bookmarks": input_data.get('statistics', {}).get('likeCount', 0),
                "creator": input_data.get("snippet", {}).get("channelTitle", ""),
                "updated_date": input_data.get("snippet", {}).get("publishedAt", ""),
                "lang": input_data.get("snippet", {}).get("defaultAudioLanguage", "ko"),
                "subtitles": "있음" if input_data.get('contentDetails', {}).get('caption') == 'true' else "없음",
                "discounted_price": "무료",
                "program_difficulty": "초급",
                "program_total_time": convert_duration_to_hhmmss(input_data.get('contentDetails', {}).get('duration', '')),
                "program_video_count": "1",
                "program_bookmark_count": input_data.get('statistics', {}).get('likeCount', 0),
                "program_link": f"https://www.youtube.com/watch?v={input_data.get('id', '')}",
                "program_creator_description": "",
                "description": create_structured_description(input_data),
                "program_curriculum": []
            }
            
            courses.append(course)
            
        except Exception as e:
            print(f"Error processing item {input_data.get('snippet', {}).get('title', 'Unknown')}: {e}")
            continue

# JSON 파일로 저장
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(courses, f, ensure_ascii=False, indent=2)

print(f"{output_file} 파일이 생성되었습니다!")