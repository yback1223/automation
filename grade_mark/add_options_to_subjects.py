import json



def load_json(file_path: str) -> list[dict]:
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)
    
def save_json(file_path: str, data: dict) -> None:
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def add_options_to_subjects(input_data: list[dict], output_file_path: str, added_subjects: list[str], label: str) -> None:
    try:
        for data in input_data:
            if data['과목명'] in added_subjects:
                data[label] = True
            else:
                data[label] = False
        save_json(output_file_path, input_data)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    input_data = load_json("full_subject_data.json")
    수능_subjects = [
        "화법과 언어", "독서와 작문, 문학", "대수, 미적분Ⅰ", "확률과 통계",
        "영어Ⅰ", "영어Ⅱ", "한국사1", "한국사2", "통합사회1", "통합사회2",
        "통합과학1", "통합과학2", "독일어", "프랑스어", "스페인어", "중국어",
        "일본어", "러시아어", "아랍어", "베트남어", "한문"
    ]

    석차등급_미기재_subjects = [
        "여행지리", "역사로 탐구하는 현대 세계", "사회문제 탐구", "금융과 경제생활",
        "윤리문제 탐구", "기후변화와 지속가능한 세계", "과학의 역사와 문화", "기후변화와 환경생태",
        "융합과학 탐구", "진로와 직업", "생태와 환경", "인간과 철학", "논리와 사고",
        "인간과 심리", "교육의 이해", "삶과 종교", "보건", "인간과 경제활동", "논술",
        "체육1", "체육2", "운동과 건강", "스포츠 문화", "스포츠 과학", "스포츠 생활1",
        "스포츠 생활2", "음악", "미술", "연극", "음악 연주와 창작", "음악", "감상과 비평",
        "미술 창작", "미술 감상과 비평", "음악과 미디어", "미술과 매체"
    ]

    특목고_subjects = [
        "전문 수학", "이산 수학", "고급 기하", "고급 대수", "고급 미적",
        "고급 물리학", "고급 화학", "고급 생명과학", "고급 지구과학",
        "과학과제 연구", "물리학 실험", "화학 실험", "생명과학 실험", "지구과학 실험",
        "정보과학", "스포츠 개론", "육상", "체조", "수상" "스포츠", 
        "기초 체육 전공 실기", "심화 체육 전공 실기", "고급 체육 전공 실기", 
        "스포츠 경기 체력", "스포츠 경기 기술", "스포츠 경기 분석", "스포츠 교육", 
        "스포츠 생리의학", "스포츠 행정 및 경영", "음악 이론", "음악사", "시창⋅청음", 
        "음악 전공 실기", "합창⋅합주", "음악 공연 실습", "미술 이론", "드로잉", "미술사", "미술 전공 실기", "조형 탐구", 
        "무용의 이해", "무용과 몸", "무용 기초 실기", "무용 전공 실기", "안무", 
        "무용 제작 실습", "무용 감상과 비평", "문예 창작의 이해", "문장론", "문학 감상과 비평", "시 창작", "소설" 
        "창작", "극 창작", "연극과 몸", "연극과 말", "연기", "무대 미술과 기술", "연극 제작 실습", 
        "연극 감상과 비평", "영화의 이해", "촬영⋅조명", "편집⋅사운드", "영화 제작 실습", 
        "영화 감상과 비평", "사진의 이해", "사진 촬영", "사진 표현 기법", "영상 제작의 이해", 
        "사진 감상과 비평", "음악과 문화", "미술 매체 탐구", "미술과 사회", "무용과 매체"
        "문학과 매체", "연극과 삶", "영화와 삶", "사진과 삶"
    ]

    add_options_to_subjects(input_data, "full_subjects_data2.json", 수능_subjects, "수능출제여부")
    input_data = load_json("full_subjects_data2.json")
    add_options_to_subjects(input_data, "full_subjects_data3.json", 석차등급_미기재_subjects, "석차등급기재여부")
    input_data = load_json("full_subjects_data3.json")
    add_options_to_subjects(input_data, "full_subjects_data4.json", 특목고_subjects, "특목고과목여부")