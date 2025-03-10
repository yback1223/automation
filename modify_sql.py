import re
from bs4 import BeautifulSoup

def process_html_to_output(input_html, big_section="02. 커리어 플랜 도우미", small_section="Custom Section", tutorial_name="Custom Guide"):
    # 1. BeautifulSoup으로 HTML 파싱
    soup = BeautifulSoup(input_html, 'html.parser')

    # 2. 이모지 제거 (유니코드 이모지 패턴)
    def remove_emojis(text):
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # 이모티콘
            "\U0001F300-\U0001F5FF"  # 기호 및 픽토그램
            "\U0001F680-\U0001F6FF"  # 교통 및 지도 기호
            "\U0001F1E0-\U0001F1FF"  # 국기
            "]+",
            flags=re.UNICODE
        )
        return emoji_pattern.sub(r'', text)

    # 3. HTML을 세로 정렬 div로 감싸기
    wrapper_div = soup.new_tag('div')
    wrapper_div['style'] = "display: flex; flex-direction: column; align-items: flex-start; text-align: left;"
    
    # 모든 태그를 wrapper_div 안에 추가
    for tag in soup.find_all(recursive=False):
        # id 속성이 빈 경우 제거
        if tag.get('id') == "":
            del tag['id']
        # 텍스트에서 이모지 제거
        if tag.string:
            tag.string = remove_emojis(tag.string)
        wrapper_div.append(tag)
    
    # 기존 soup 내용을 지우고 wrapper_div로 교체
    soup.clear()
    soup.append(wrapper_div)

    # 4. HTML 문자열로 변환 (줄바꿈 포함)
    formatted_html = str(soup).replace('><', '>\n<').replace('</', '\n</')

    # 5. SQL 쿼리 생성
    # 작은따옴표 이스케이프 처리
    sql_safe_html = formatted_html.replace("'", "\\'")
    sql_query = f"""INSERT INTO `job_db`.`tutorial_html_tag` 
  (`big_section`, `small_section`, `tutorial_name`, `html_tag`) 
VALUES 
  ( 
    '{big_section}', 
    '{small_section}', 
    '{tutorial_name}', 
    '{sql_safe_html}'
  );"""

    # 6. 결과 반환
    return {
        "sql_query": sql_query,
        "html_output": formatted_html
    }

# 테스트용 입력 HTML (당신이 제공한 마지막 예제)
input_html = '''
<h2 id="">‍</h2><p id="">챗봇을 제작하다보면 자신만의 데이터를 업로드하여 사용하거나 특정 웹페이지(url)에 존재하는 데이터를 활용하고 싶은 경우가 있습니다.</p><p id="">그런 경우 데이터를 업로드하거나 웹페이지 url을 입력한 후 해당 데이터가 챗봇에 활용될 수 있는 형태(Asset)으로 변환되어야 합니다.</p><p id="">데이터가 변환되는 과정은 짧게 걸리는 경우도 있고 때에 따라 하루가 넘어가는 경우도 있습니다. 그런 경우 변환 진행상황을 확인하고 해당 과정은 관리하는 기능이 필요할 것 입니다.</p><p id="">독갑이의 "Booster"기능을 통해 관리가 가능합니다.</p><p id="">‍</p><h4 id="">1. Asset 업데이트</h4><h5 id="">1) 데이터 업로드 및 Asset 생성 요청</h5><p id="">- "Asset 생성/편집 &gt; 파일 단위 업로드" 내용을 참고하여 데이터를 업로드 한 후 생성 요청 버튼을 클릭합니다.</p><p id="">‍</p><h5 id="">2) Booster를 통한 진행 상황 관리</h5><ul><li>Asset 생성 진행 상황을 실시간으로 모니터링할 수 있는 인터페이스를 제공합니다.</li><li>작업 내역 조회를 통해 이전에 완료된 Asset 생성 작업의 내역을 확인할 수 있습니다.</li></ul><p id="">‍</p><p id="">‍</p><p id="">‍</p><p id="">‍</p>



'''

# 실행
result = process_html_to_output(
    input_html,
    big_section="09. Launch & Manage",
    small_section="어셋 업데이트",
    tutorial_name="독갑이"
)

# 결과 출력
print("=== SQL Query ===")
print(result["sql_query"])
