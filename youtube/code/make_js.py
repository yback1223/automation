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

js_content = '''
const courses = [
'''

# 각 카테고리별로 처리
for category, videos in youtube_data.items():
    for input_data in videos:
        try:
            # 간단 설명 (description에서 100자 추출)
            description = input_data.get("snippet", {}).get("description", "")
            summarized_description = description[:100] + "..." if len(description) > 100 else description
            # 모든 문자열 필드를 JSON으로 변환하여 특수문자 처리
            summarized_description_json = json.dumps(summarized_description, ensure_ascii=False)
            course_name_json = json.dumps(input_data.get("snippet", {}).get("title", ""), ensure_ascii=False)
            creator_json = json.dumps(input_data.get("snippet", {}).get("channelTitle", ""), ensure_ascii=False)
            category_json = json.dumps(category, ensure_ascii=False)
            image_url_json = json.dumps(input_data.get("snippet", {}).get("thumbnails", {}).get("high", {}).get("url", ""), ensure_ascii=False)
            updated_date_json = json.dumps(input_data.get("snippet", {}).get("publishedAt", ""), ensure_ascii=False)
            lang_json = json.dumps(input_data.get("snippet", {}).get("defaultAudioLanguage", "ko"), ensure_ascii=False)
            subtitles_json = json.dumps("있음" if input_data.get('contentDetails', {}).get('caption') == 'true' else "없음", ensure_ascii=False)
            program_link_json = json.dumps(f"https://www.youtube.com/watch?v={input_data.get('id', '')}", ensure_ascii=False)
            program_time_json = json.dumps(convert_duration_to_hhmmss(input_data.get('contentDetails', {}).get('duration', '')), ensure_ascii=False)
            
            # 구조화된 설명 생성
            structured_description = create_structured_description(input_data)
            # JSON 문자열로 변환하여 이스케이프 처리
            structured_description_json = json.dumps(structured_description, ensure_ascii=False)
            
            # YouTube 데이터에 맞게 필드 매핑
            program_js = f'''    {{
            id: "{input_data.get('id', '')}_youtube",
            data_source: "youtube",
            student_type: ["초", "중", "고"],
            location: "온라인",
            rough_location: "",
            corp_type: "개인사업장",
            bigCategory: {category_json},
            smallCategory: "",
            image: {image_url_json},
            course_name: {course_name_json},
            summarizedDescription: {summarized_description_json},
            bookmarks: {input_data.get('statistics', {}).get('likeCount', '0')},
            creator: {creator_json},
            updated_date: {updated_date_json},
            lang: {lang_json},
            subtitles: {subtitles_json},
            discounted_price: "무료",
            program_difficulty: "초급",
            program_total_time: {program_time_json},
            program_video_count: "1",
            program_bookmark_count: {input_data.get('statistics', {}).get('likeCount', '0')},
            program_link: {program_link_json},
            program_creator_description: "",
            description: {structured_description_json},
            program_curriculum: []
        }}'''
            
            js_content += program_js + ",\n"
            
        except Exception as e:
            print(f"Error processing item {input_data.get('snippet', {}).get('title', 'Unknown')}: {e}")
            continue

# JavaScript 파일 내용 마무리
js_content = js_content.rstrip(",\n") + "\n" + '''];

export default courses;
'''

# 파일로 저장
with open("youtube_courses_tmp.js", "w", encoding="utf-8") as f:
    f.write(js_content)

print("youtube_courses.js 파일이 생성되었습니다!")