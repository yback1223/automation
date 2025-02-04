import json
import pandas as pd

# 기존 과목 정보 JSON 파일 로드
with open("full_subjects_data4.json", "r", encoding="utf-8") as f:
    main_subjects = json.load(f)

# 추가 과목 설명 JSON 파일 로드
with open("crawled_data_from_gg_edu.json", "r", encoding="utf-8") as f:
    additional_subjects_info = json.load(f)

# 기존 데이터와 추가 데이터를 과목명을 기준으로 병합
merged_data = []
for subject in main_subjects:
    subject_name = subject["과목명"]
    additional_info = next((item for item in additional_subjects_info if item["과목명"] == subject_name), {})
    merged_subject = {
        **subject, 
        "과목설명": additional_info.get("과목설명"),
        "관련 학과": additional_info.get("관련 학과"),
        "관련 직업": additional_info.get("관련 직업"),
    }
    merged_data.append(merged_subject)

with open("merged_subject_data.json", "w", encoding="utf-8") as json_file:
    json.dump(merged_data, json_file, ensure_ascii=False, indent=4)

# 병합된 데이터를 DataFrame으로 변환 후 엑셀 파일로 저장
df = pd.DataFrame(merged_data)
df.to_excel("merged_subject_data.xlsx", index=False)

print("✅ 병합된 데이터가 JSON 및 Excel 파일로 저장되었습니다.")
