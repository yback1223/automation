import json

def extract_employment_categories(input_file: str, output_file: str):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    extracted_data = []
    seen = set()  # 중복 확인용 set

    for item in data:
        entry = (
            item.get("고용직업분류_1"),
            item.get("고용직업분류_2"),
            item.get("고용직업분류_3"),
        )
        
        if entry not in seen:
            seen.add(entry)
            extracted_data.append({
                "고용직업분류_1": entry[0],
                "고용직업분류_2": entry[1],
                "고용직업분류_3": entry[2],
            })

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=4)

# 사용 예시
extract_employment_categories("ggoomgil/code/final_merged_data.json", "job_hir_class_list.json")
