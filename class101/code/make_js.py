import json

# 입력 JSON 파일 경로
input_file = "crawled_program_details_tmp_100.json"

# JSON 파일 읽기
with open(input_file, "r", encoding="utf-8") as f:
    data_list = json.load(f)

# JavaScript 파일 내용 시작
js_content = '''import { course_images } from "./images";

const courses = [
'''

for data in data_list:
    try:
        # 문자열 이스케이프 처리
        description = data.get("program_description_by_gemini", "").replace('"', '\\"').replace("\n", "\\n")
        creator_description = data.get("program_creator_description", "").replace('"', '\\"').replace("\n", "\\n")
        curriculum = json.dumps(data.get("program_curriculum", []), ensure_ascii=False)
        
        # 프로그램 ID 추출
        program_id = data.get("program_link", "").split("/")[-1]
        
        # JavaScript 객체 문자열 생성
        program_js = f'''    {{
        id: "{program_id}",
        data_source: "class101",
        student_type: ["초", "중", "고"],
        location: "online",
        rough_location: "",
        corp_type: "개인사업장",
        bigCategory: "{data.get('program_first_category', '').replace(' ', '')}",
        smallCategory: "{data.get('program_second_category', '').replace(' ', '')}",
        image: "{data.get('program_image_url', '')}",
        course_name: "{data.get('program_name', '')}",
        summarizedDescription: "{description[:100] + '...' if description else ''}",
        bookmarks: {data.get('program_bookmark_count', 0)},
        creator: "{data.get('program_creator', '')}",
        updated_date: "{data.get('program_start_date', '')}",
        lang: "{data.get('program_audio_languages', '')}",
        subtitles: "{data.get('program_subtitles', '')}",
        discounted_price: "{data.get('program_price', '')}",
        program_difficulty: "{data.get('program_difficulty', '')}",
        program_total_time: "{data.get('program_total_time', '')}",
        program_video_count: "{data.get('program_video_count', '')}",
        program_bookmark_count: {data.get('program_bookmark_count', 0)},
        program_link: "{data.get('program_link', '')}",
        program_creator_description: "{creator_description}",
        description: `{description}`,
        program_curriculum: {curriculum}
    }}'''
        
        js_content += program_js + ",\n"
        
    except Exception as e:
        print(f"Error processing item: {e}")
        continue

# JavaScript 파일 내용 마무리
js_content += '''];

export default courses;
'''

# 파일로 저장
with open("courses.js", "w", encoding="utf-8") as f:
    f.write(js_content)

print("courses.js 파일이 생성되었습니다!")