어셋 생성 : 문서파일
Asset 구성하기 : 문서 파일(pdf, txt, word)
‍
‍

챗봇에 문서 파일 형식 데이터를 업로드하여 활용하는 방법을 안내하겠습니다.

챗봇에 문서 파일(PDF, TXT, Word)을 업로드하여 데이터를 가져올 때, 사용자가 문서 안에서 중요한 정보를 지정할 수 있도록 입력해야 할 항목들을 정의하는 것이 중요합니다. 이를 통해 챗봇은 필요한 정보만을 정확하게 추출하고, 적절한 답변을 제공할 수 있습니다. 다음은 사용자가 입력해야 할 주요 항목들입니다.

‍
Asset(데이터) 구성 가이드
‍
1. 문서 파일 준비
문서 수집
챗봇에서 사용할 문서 파일들을 준비합니다. 예를 들어, 패션 관련 챗봇이라면 패션에 대한 트렌드 보고서나 패션 현황 보고서 등의 파일들을 모아야 합니다.
폴더 정리
문서 파일은 확장자별로 동일한 폴더에 저장합니다. 파일 이름은 중복되지 않도록 고유하게 설정합니다.
파일 형식
사용 가능한 문서 파일 형식으로는 .pdf, .txt, .doc등이 있습니다.
‍

2. 메타데이터 구성

메타데이터 파일 생성
문서 파일들과 함께 사용할 파일을 생성합니다. 이 파일은 각 문서에 대한 메타데이터를 포함합니다. (권장 파일 형식 : csv, xlsx)
메타데이터 항목
파일의 각 행은 하나의 문서에 대응되며, 다음과 같은 정보를 포함합니다.
산업명 (Industry): 해당 데이터가 속하는 산업 분야를 나타냅니다. (예: 패션 산업, 의료 산업)
품목명 (Product): 구체적인 품목이나 항목의 이름을 나타냅니다. (예: 니트, 청바지 등)
키워드 (Keywords): 문서에서 중요하게 다룰 키워드를 입력하게 합니다. (예: 디자인, 성능 등)
중요 섹션 (Important Sections): 문서에서 중요하다고 판단되는 섹션의 페이지 번호를 지정합니다. (예: 5-10, 15-20 등)
‍

이와 같은 방식으로 체계적으로 문서를 준비하고 메타데이터를 구성하여 챗봇에서 효과적으로 문서를 활용할 수 있습니다. 준비한 파일을 독갑이에 업로드하는 방법은 "Asset 생성"에서 확인할 수 있습니다.

‍