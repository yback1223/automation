import json
import pandas as pd

def load_json(file_path: str) -> list[dict]:
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_json(file_path: str, data: dict) -> None:
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def json_to_excel(json_file, excel_output_file):
    try:
        input_json_data = load_json(json_file)
        extracted_data = []
    # {
    #     "과목명": "공통국어1",
    #     "유형": "공통과목",
    #     "교과(군)": "국어",
    #     "기본학점": 4,
    #     "증감범위": -1,
    #     "편성학점": "3~4",
    #     "성적처리유형": "A/B/C/D/E, 등급○",
    #     "수능출제여부": false,
    #     "석차등급기재여부": false,
    #     "특목고과목여부": false
    # },
        for high_class in input_json_data:
            row = {
                "과목명": high_class.get("과목명", ""),
                "유형": high_class.get("유형", ""),
                "교과(군)": high_class.get("교과(군)", ""),
                "기본학점": high_class.get("기본학점", ""),
                "증감범위": high_class.get("증감범위", ""),
                "편성학점": high_class.get("편성학점", ""),
                "성적처리유형": high_class.get("성적처리유형", ""),
                "수능출제여부": "O" if high_class.get("수능출제여부", "") else "X",
                "석차등급기재여부": "O" if high_class.get("석차등급기재여부", "") else "X",
                "특목고과목여부": "O" if high_class.get("특목고과목여부", "") else "X"
            }
            extracted_data.append(row)
        
        df = pd.DataFrame(extracted_data, columns=[
            "교과(군)", "유형", "과목명", "기본학점", "증감범위", "편성학점", "성적처리유형", "수능출제여부", "석차등급기재여부", "특목고과목여부"
        ])

        df.to_excel(excel_output_file, index=False)
        print(f"Excel 파일이 성공적으로 생성되었습니다: {excel_output_file}")

    except Exception as e:
        print(f"JSON을 Excel로 변환하는 중 오류 발생: {e}")

json_file = "full_subjects_data4.json"
excel_output_file = "full_subjects_data4.xlsx"

json_to_excel(json_file, excel_output_file)