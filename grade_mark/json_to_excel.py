import json, re
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
 
        # for high_class in input_json_data:
            # row = {
            #     "과목명": high_class.get("과목명", ""),
            #     "유형": high_class.get("유형", ""),
            #     "교과(군)": high_class.get("교과(군)", ""),
            #     "기본학점": high_class.get("기본학점", ""),
            #     "증감범위": high_class.get("증감범위", ""),
            #     "편성학점": high_class.get("편성학점", ""),
            #     "성적처리유형": high_class.get("성적처리유형", ""),
            #     "수능출제여부": "O" if high_class.get("수능출제여부", "") else "X",
            #     "석차등급기재여부": "O" if high_class.get("석차등급기재여부", "") else "X",
            #     "특목고과목여부": "O" if high_class.get("특목고과목여부", "") else "X"
            # }
        for major in input_json_data:
            career = major.get("major_related_career", "")
            if "●" in career:
                jobs = re.findall(r"\((.*?)\)", career)
                career = ', '.join([job for job_group in jobs for job in job_group.split(", ")])
                
            row = {
                "계열": major.get("line_name", ""),
                "계열_관련_학과": major.get("line_related_majors", ""),
                "계열_멘토_설명": major.get("line_mentor_mention", ""),
                "계열_권장_일반_선택_과목": major.get("line_related_normal_subjects", ""),
                "계열_권장_진로_선택_과목": major.get("line_related_career_subjects", ""),
                "학과": major.get("major_name", ""),
                "학과_설명": major.get("major_desc", ""),
                "학생_유형": major.get("major_student_type", ""),
                "학과_권장_선택_과목": major.get("major_normal_subjects", ""),
                "학과_권장_진로_선택_과목": major.get("major_career_subjects", ""),
                "개설_대학_서울": major.get("major_university_in_seoul", ""),
                "개설_대학_수도권": major.get("major_university_near_seoul", ""),
                "개설_대학_지방": major.get("major_university_in_country", ""),
                "유사학과": major.get("major_related_majors", ""),
                "졸업_후_진로": career
            }
            extracted_data.append(row)
        
        # df = pd.DataFrame(extracted_data, columns=[
        #     "계열", "유형", "과목명", "기본학점", "증감범위", "편성학점", "성적처리유형", "수능출제여부", "석차등급기재여부", "특목고과목여부"
        # ])
        df = pd.DataFrame(extracted_data, columns=[
            "계열", "계열_관련_학과", "계열_멘토_설명", "계열_권장_일반_선택_과목", 
            "계열_권장_진로_선택_과목", "학과", "학과_설명", "학생_유형", "학과_권장_선택_과목", 
            "학과_권장_진로_선택_과목", "개설_대학_서울", "개설_대학_수도권", "개설_대학_지방", 
            "유사학과", "졸업_후_진로"
        ])

        df.to_excel(excel_output_file, index=False)
        print(f"Excel 파일이 성공적으로 생성되었습니다: {excel_output_file}")

    except Exception as e:
        print(f"JSON을 Excel로 변환하는 중 오류 발생: {e}")

json_file = "crawled_data_from_seoul_edu.json"
excel_output_file = "crawled_data_from_seoul_edu.xlsx"

json_to_excel(json_file, excel_output_file)