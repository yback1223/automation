from bs4 import BeautifulSoup
import json

university = "서울대학교"

# HTML 테이블 데이터 (여기에 입력)
html_data = """<tbody>
            <tr>
                <td>인문 대학</td>
                <td colspan="2">-</td>
                <td>-</td>
                <td>-</td>
            </tr>
            <tr>
                <td rowspan="8">사회 과학 대학</td>
                <td colspan="2">정치외교학부</td>
                <td rowspan="8">-</td>
                <td>-</td>
            </tr>
            <tr>
                <td colspan="2">경제학부&nbsp;</td>
                <td>미적분, 확률과 통계</td>
            </tr>
            <tr>
                <td colspan="2">사회학과</td>
                <td rowspan="6">-</td>
            </tr>
            <tr>
                <td colspan="2">인류학과</td>
            </tr>
            <tr>
                <td colspan="2">신리학과</td>
            </tr>
            <tr>
                <td colspan="2">지리학과</td>
            </tr>
            <tr>
                <td colspan="2">사회복지학과</td>
            </tr>
            <tr>
                <td colspan="2">언론정보학과</td>
            </tr>
            <tr>
                <td rowspan="7">자연 과학 대학</td>
                <td colspan="2">수리과학부</td>
                <td>미적분, 확률과 통계, 기하</td>
                <td></td>
            </tr>
            <tr>
                <td colspan="2">통계학과</td>
                <td>미적분, 확률과 통계, 기하</td>
                <td></td>
            </tr>
            <tr>
                <td rowspan="2">물리· 천문학부</td>
                <td>물리학전공</td>
                <td>물리학Ⅱ, 미적분, 기하</td>
                <td>확률과 통계</td>
            </tr>
            <tr>
                <td>천문학전공</td>
                <td>지구과학Ⅰ, 미적분, 기하</td>
                <td>지구과학Ⅱ, 물리학Ⅱ, 확률과 통계</td>
            </tr>
            <tr>
                <td colspan="2">화학부</td>
                <td>화학Ⅱ, 미적분</td>
                <td>확률과 통계, 기하</td>
            </tr>
            <tr>
                <td colspan="2">생명과학부</td>
                <td>생명과학Ⅱ, 미적분</td>
                <td>화학Ⅱ, 확률과 통계, 기하</td>
            </tr>
            <tr>
                <td colspan="2">지구환경과학부</td>
                <td width="194">물리학Ⅱ 또는 화학Ⅱ 또는<br>
                    지구과학Ⅱ, 미적분</td>
                <td>확률과 통계, 기하</td>
            </tr>
            <tr>
                <td colspan="3">간호대학</td>
                <td>-</td>
                <td>생명과학Ⅰ, 생명과학Ⅱ</td>
            </tr>
            <tr>
                <td colspan="3">경영대학</td>
                <td>-</td>
                <td>-</td>
            </tr>
            <tr>
                <td rowspan="13">공과 대학</td>
                <td colspan="2">광역</td>
                <td>미적분, 확률과 통계</td>
                <td>기하</td>
            </tr>
            <tr>
                <td colspan="2">건설환경공학부</td>
                <td>미적분, 기하</td>
                <td>확률과 통계</td>
            </tr>
            <tr>
                <td colspan="2">기계공학부</td>
                <td>물리학Ⅱ, 미적분, 기하</td>
                <td>확률과 통계</td>
            </tr>
            <tr>
                <td colspan="2">재료공학부</td>
                <td>미적분, 기하</td>
                <td>물리학Ⅱ, 화학Ⅱ, 확률과 통계</td>
            </tr>
            <tr>
                <td colspan="2">전기·정보공학부</td>
                <td>물리학Ⅱ, 미적분</td>
                <td>확률과 통계, 기하</td>
            </tr>
            <tr>
                <td colspan="2">컴퓨터공학부</td>
                <td>미적분, 확률과 통계</td>
                <td></td>
            </tr>
            <tr>
                <td colspan="2">화학생물공학부</td>
                <td>물리학Ⅱ, 미적분, 기하</td>
                <td>화학Ⅱ 또는 생명과학Ⅱ</td>
            </tr>
            <tr>
                <td colspan="2">건축학과</td>
                <td>-</td>
                <td>미적분</td>
            </tr>
            <tr>
                <td colspan="2">산업공학과</td>
                <td>미적분</td>
                <td>확률과 통계</td>
            </tr>
            <tr>
                <td colspan="2">에너지자원공학과</td>
                <td>물리학Ⅱ, 미적분, 기하</td>
                <td>확률과 통계</td>
            </tr>
            <tr>
                <td colspan="2">원자핵공학과</td>
                <td>물리학Ⅱ, 미적분</td>
                <td></td>
            </tr>
            <tr>
                <td colspan="2">조선해양공학과</td>
                <td>물리학Ⅰ, 미적분, 기하</td>
                <td>확률과 통계</td>
            </tr>
            <tr>
                <td colspan="2">항공우주공학과</td>
                <td>물리학Ⅱ, 미적분, 기하</td>
                <td>지구과학Ⅱ, 확률과 통계</td>
            </tr>
            <tr>
                <td rowspan="7">농업 생명 과학 대학</td>
                <td colspan="2">농경제사회학부</td>
                <td>-</td>
                <td>미적분, 확률과 통계</td>
            </tr>
            <tr>
                <td colspan="2">식물생산과학부</td>
                <td>생명과학Ⅱ</td>
                <td>화학Ⅱ, 미적분, 확률과 통계, 기하</td>
            </tr>
            <tr>
                <td colspan="2">산림과학부</td>
                <td>-</td>
                <td>-</td>
            </tr>
            <tr>
                <td colspan="2">식품·동물생명공학부</td>
                <td>화학Ⅱ, 생명과학Ⅱ</td>
                <td>-</td>
            </tr>
            <tr>
                <td colspan="2">응용생물화학부</td>
                <td>화학Ⅱ, 생명과학Ⅱ</td>
                <td>미적분, 확률과 통계, 기하</td>
            </tr>
            <tr>
                <td colspan="2">조경·지역시스템공학부</td>
                <td>미적분, 기하</td>
                <td>물리학Ⅱ, 확률과 통계</td>
            </tr>
            <tr>
                <td colspan="2">바이오시스템·소재학부</td>
                <td>미적분, 기하</td>
                <td>물리학Ⅱ 또는 화학Ⅱ</td>
            </tr>
            <tr>
                <td>미술 대학</td>
                <td colspan="2">-</td>
                <td>-</td>
                <td>-</td>
            </tr>
            <tr>
                <td rowspan="7">사범 대학</td>
                <td colspan="2">교육학과, 국어, 영어, 독어, 불어, 사회, 역사, 지리, 윤리 교육과</td>
                <td>-</td>
                <td></td>
            </tr>
            <tr>
                <td colspan="2">수학교육과</td>
                <td>미적분, 확률과 통계, 기하</td>
                <td></td>
            </tr>
            <tr>
                <td colspan="2">물리교육과</td>
                <td>물리학Ⅱ</td>
                <td>미적분, 확률과 통계, 기하</td>
            </tr>
            <tr>
                <td colspan="2">화학교육과</td>
                <td>화학Ⅱ</td>
                <td>미적분, 확률과 통계, 기하</td>
            </tr>
            <tr>
                <td colspan="2">생물교육과</td>
                <td>생명과학Ⅱ</td>
                <td>화학Ⅱ, 미적분, 확률과 통계</td>
            </tr>
            <tr>
                <td colspan="2">지구과학교육과</td>
                <td>지구과학Ⅰ</td>
                <td>지구과학Ⅱ, 미적분, 확률과 통계, 기하</td>
            </tr>
            <tr>
                <td colspan="2">체육교육과</td>
                <td>-</td>
                <td>-</td>
            </tr>
            <tr>
                <td rowspan="3">생활 과학 대학</td>
                <td colspan="2">소비자 아동학부</td>
                <td>-</td>
                <td>-</td>
            </tr>
            <tr>
                <td colspan="2">식품영양학과</td>
                <td>화학Ⅰ, 생명과학Ⅰ</td>
                <td>화학Ⅱ 또는 생명과학Ⅱ</td>
            </tr>
            <tr>
                <td colspan="2">의류학과</td>
                <td></td>
                <td>화학Ⅰ, 생명과학Ⅰ</td>
            </tr>
            <tr>
                <td>수의과 대학</td>
                <td colspan="2">수의예과</td>
                <td>생명과학Ⅰ</td>
                <td>미적분, 확률과 통계</td>
            </tr>
            <tr>
                <td>약학 대학</td>
                <td colspan="2">약학계열</td>
                <td>화학Ⅰ, 생명과학Ⅰ</td>
                <td>미적분, 화학Ⅱ 또는 생명과학Ⅱ</td>
            </tr>
            <tr>
                <td>음악 대학</td>
                <td colspan="2">-</td>
                <td>-</td>
                <td>-</td>
            </tr>
            <tr>
                <td>의과 대학</td>
                <td colspan="2">의예과</td>
                <td>생명과학Ⅰ</td>
                <td>생명과학Ⅱ, 미적분, 확률과 통계, 기하</td>
            </tr>
            <tr>
                <td colspan="3">자유전공학부</td>
                <td>-</td>
                <td>미적분, 확률과 통계</td>
            </tr>
            <tr>
                <td colspan="3">첨단융합학부</td>
                <td>미적분</td>
                <td>확률과 통계 또는 물리학Ⅰ 또는 화학Ⅰ</td>
            </tr>
            <tr>
                <td>치의학 대학원</td>
                <td colspan="2">치의학과</td>
                <td>-</td>
                <td>-</td>
            </tr>
        </tbody>"""

# BeautifulSoup을 사용하여 HTML 파싱
soup = BeautifulSoup(html_data, "html.parser")
rows = soup.find_all("tr")

# JSON 변환을 위한 리스트
json_data = []
current_big_major = None  # 현재 대계열 (대학)
current_major = None  # 현재 학과

big_major = None
big_major_length: int = 0

for row in rows:
    td_elements = row.find_all("td")
    if len(td_elements) == 4 and big_major_length == 0:
        big_major_length = td_elements[0]["rowspan"] if td_elements[0].has_attr("rowspan") else 1
        big_major = td_elements[0].text.strip()
        major = td_elements[1].text.strip()
        necessary_classes = td_elements[2].text.strip()
        recommended_classes = td_elements[3].text.strip()
    elif len(td_elements) == 4 and big_major_length > 0:
        major = f"{td_elements[0].text.strip()} - {td_elements[1].text.strip()}" 
        necessary_classes = td_elements[2].text.strip()
        recommended_classes = td_elements[3].text.strip()
    elif len(td_elements) == 3 and big_major_length == 0:
        big_major = td_elements[0].text.strip()
        major = td_elements[0].text.strip()
        necessary_classes = td_elements[1].text.strip()
        recommended_classes = td_elements[2].text
    elif len(td_elements) == 3:
        major = td_elements[0].text.strip()
        necessary_classes = td_elements[1].text.strip()
        recommended_classes = td_elements[2].text.strip()
    
    print(f"대학: {university}, 대계열: {big_major}, 학과: {major}, 필수과목: {necessary_classes}, 추천과목: {recommended_classes}")
    big_major_length -= 1

    json_data.append({
        "대학": university,
        "대계열": big_major,
        "학과": major,
        "필수과목": necessary_classes,
        "추천과목": recommended_classes
    })


# JSON 저장 함수
def save_json(file_path: str, data: list) -> None:
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

save_json("class_major_data2.json", json_data)

# JSON 데이터 출력
print(json.dumps(json_data, indent=4, ensure_ascii=False))
