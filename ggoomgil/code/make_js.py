import json

def create_structured_description(data):
    sections = []
    
    # 기본 정보 섹션 추가
    basic_info = []
    if data.get('program_days'):
        days = data['program_days']
        if isinstance(days, list):
            days = ', '.join(days)
        basic_info.append(f"■ 체험요일\n{days}")
    if data.get('program_times'):
        basic_info.append(f"■ 체험시간\n{data['program_times']}")
    if data.get('headcount'):
        basic_info.append(f"■ 정원\n{data['headcount']}명")
    
    if basic_info:
        sections.append("【기본 정보】\n\n" + "\n\n".join(basic_info) + "\n\n")
    
    # 학년별 섹션 생성
    for level in ['elementary', 'middle', 'high']:
        if any(data.get(f"{level}_{part}") for part in ['goal', 'preparation', 'beginning', 'activity', 'finale', 'after']):
            section = f"【{'초등학생' if level == 'elementary' else '중학생' if level == 'middle' else '고등학생'}】\n\n"
            
            # 각 파트별 내용 추가
            parts = {
                'goal': '목표',
                'preparation': '사전 준비dcdc',
                'beginning': '도입',
                'activity': '본활동',
                'finale': '마무리',
                'after': '사후활동'
            }
            
            for key, title in parts.items():
                content = data.get(f"{level}_{key}")
                if content:
                    section += f"■ {title}\n{content}\n\n"
            
            sections.append(section)
    
    # 최종 문자열 생성 시 실제 줄바꿈 사용
    return "".join(sections)

input_file = "ggoomgil_data_tmp.json"

try:
    with open(input_file, "r", encoding="utf-8") as f:
        input_data_list = json.load(f)
except FileNotFoundError:
    print(f"Error: {input_file} 파일을 찾을 수 없습니다.")
    exit(1)
except json.JSONDecodeError:
    print(f"Error: {input_file} 파일의 JSON 형식이 잘못되었습니다.")
    exit(1)

js_content = '''
const courses = [
'''

for input_data in input_data_list:
    try:
        description = (input_data.get("elementary_goal", "") + "\n" + 
                      input_data.get("middle_goal", "") + "\n" + 
                      input_data.get("high_goal", "")).replace('"', '\\"').replace("\n", "\\n")
        
        program_id = input_data.get("link", "").split("=")[-1]
        
        # 구조화된 설명 생성 및 이스케이프 처리
        structured_description = create_structured_description(input_data)
        # JSON 문자열로 변환하여 이스케이프 처리
        structured_description_json = json.dumps(structured_description, ensure_ascii=False)
        
        program_js = f'''    {{
        id: "{program_id}",
        data_source: "ggoomgil",
        student_type: {json.dumps(input_data.get("student_types", []), ensure_ascii=False)},
        location: "{input_data.get('program_rough_location', '')}",
        rough_location: "{input_data.get('program_rough_location', '')}",
        corp_type: "{input_data.get('corp_type', '')}",
        bigCategory: "",
        smallCategory: "",
        image: "ggoomgil_image.png",
        course_name: "{input_data.get('program_name', '')}",
        summarizedDescription: "{description[:100] + '...' if description else ''}",
        bookmarks: 0,
        creator: "{input_data.get('corp_name', '')}",
        updated_date: "{input_data.get('apply_date', '')}",
        lang: "한국어",
        subtitles: "없음",
        discounted_price: "{input_data.get('program_fee', '')}",
        program_difficulty: "초급",
        program_total_time: "",
        program_video_count: "0",
        program_bookmark_count: 0,
        program_link: "{input_data.get('link', '')}",
        program_creator_description: "",
        description: {structured_description_json},
        program_curriculum: []
    }}'''
        
        js_content += program_js + ",\n"
        
    except Exception as e:
        print(f"Error processing item {input_data.get('program_name', 'Unknown')}: {e}")
        continue

# JavaScript 파일 내용 마무리 (마지막 쉼표 제거를 위해 strip 후 추가)
js_content = js_content.rstrip(",\n") + "\n" + '''];

export default courses;
'''

# 파일로 저장
with open("ggoomgil_courses.js", "w", encoding="utf-8") as f:
    f.write(js_content)

print("ggoomgil_courses.js 파일이 생성되었습니다!")