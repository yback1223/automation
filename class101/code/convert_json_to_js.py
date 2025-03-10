import json

def convert_json_to_js():
    # 입력 JSON 파일 읽기
    with open("class101_hir_code_matched.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # JavaScript 파일 내용 시작
    js_content = '''// 직업 분류별 클래스101 카테고리 매핑
const jobCategories = [
'''

    # 각 직업 카테고리를 JavaScript 객체로 변환
    for job in data:
        # 문자열 이스케이프 처리
        job_class = job["job_std_class"].replace('"', "'").replace(" ", "")
        categories = []
        
        # 카테고리 내의 문자열 처리
        for category in job["class101_categories"]:
            first_cat = category["first_category"].replace('"', "'").replace(" ", "")
            second_cat = category["second_category"].replace('"', "'").replace(" ", "")
            categories.append({
                "first_category": first_cat,
                "second_category": second_cat
            })
        
        # JavaScript 객체 문자열 생성
        job_js = f'''    {{
        job_std_class: "{job_class}",
        class101_categories: {json.dumps(categories, ensure_ascii=False).replace('"', "'")}
    }}'''
        
        js_content += job_js + ",\n"

    # JavaScript 파일 내용 마무리
    js_content = js_content.rstrip(",\n") + '''
];

export default jobCategories;
'''

    # 파일로 저장
    with open("jobCategories.js", "w", encoding="utf-8") as f:
        f.write(js_content)

    print("jobCategories.js 파일이 생성되었습니다!")

if __name__ == "__main__":
    convert_json_to_js() 