import json
import pandas as pd

def json_to_excel(json_file, excel_file, excel_columns, key_column_mapping):
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            json_data = json.load(file)

        extracted_data = []
        for entry in json_data:
            row = {}
            for json_key, excel_col in key_column_mapping.items():
                row[excel_col] = entry.get(json_key, None)  # Use None if the key is missing
            extracted_data.append(row)

        df = pd.DataFrame(extracted_data, columns=excel_columns)

        df.to_excel(excel_file, index=False)
        print(f"Excel file created successfully: {excel_file}")

    except Exception as e:
        print(f"Error while converting JSON to Excel: {e}")

json_file = 'main_job_crawled_data.json'
excel_file = 'output.xlsx'

# List of Excel column names
excel_columns = [
    "직업",
    "프로그램_이름", 
    "프로그램_링크",
    "체험처_이름", 
    "체험일", 
    "체험주기",
    "체험이수시간",
    "체험가능시간",
    "모집인원",
    "체험유형",
    "체험처유형",
    "대상학교유형",
    "등록일",
    "체험지역",
    "체험대상",
    "체험직무/학과",
    "참가비",
    "초등학교_목표",
    "초등학교_사전준비",
    "초등학교_주요내용_도입",
    "초등학교_주요내용_본활동",
    "초등학교_주요내용_마무리",
    "초등학교_사후활동",
    "중학교_목표",
    "중학교_사전준비",
    "중학교_주요내용_도입",
    "중학교_주요내용_본활동",
    "중학교_주요내용_마무리",
    "중학교_사후활동",
    "고등학교_목표",
    "고등학교_사전준비",
    "고등학교_주요내용_도입",
    "고등학교_주요내용_본활동",
    "고등학교_주요내용_마무리",
    "고등학교_사후활동",
    "유의사항",
    "체험장소_및_찾아가는_방법",
    "신청가능지역"
]

# Mapping of JSON keys to Excel columns
key_column_mapping = {
    "search_keyword": "직업",
    "program_name": "프로그램_이름",
    "link": "프로그램_링크",
    "corp_name": "체험처_이름", 
    "program_term": "체험일", 
    "program_days": "체험주기",
    "program_times": "체험이수시간",
    "available_time": "체험가능시간",
    "headcount": "모집인원",
    "program_type": "체험유형",
    "corp_type": "체험처유형",
    "school_types": "대상학교유형",
    "apply_date": "등록일",
    "program_rough_location": "체험지역",
    "student_types": "체험대상",
    "quals_majors": "체험직무/학과",
    "program_fee": "참가비",
    "elementary_goal": "초등학교_목표",
    "elementary_preparation": "초등학교_사전준비",
    "elementary_beginning": "초등학교_주요내용_도입",
    "elementary_activity": "초등학교_주요내용_본활동",
    "elementary_finale": "초등학교_주요내용_마무리",
    "elementary_after": "초등학교_사후활동",
    "middle_goal": "중학교_목표",
    "middle_preparation": "중학교_사전준비",
    "middle_beginning": "중학교_주요내용_도입",
    "middle_activity": "중학교_주요내용_본활동",
    "middle_finale": "중학교_주요내용_마무리",
    "middle_after": "중학교_사후활동",
    "high_goal": "고등학교_목표",
    "high_preparation": "고등학교_사전준비",
    "high_beginning": "고등학교_주요내용_도입",
    "high_activity": "고등학교_주요내용_본활동",
    "high_finale": "고등학교_주요내용_마무리",
    "high_after": "고등학교_사후활동",
    "notice": "유의사항",
    "how_to_go": "체험장소_및_찾아가는_방법",
    "appliable_location": "신청가능지역"
}

# Convert JSON to Excel
json_to_excel(json_file, excel_file, excel_columns, key_column_mapping)
