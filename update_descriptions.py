import json
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# MySQL 데이터베이스 연결 설정
# DATABASE_URL = "mysql+pymysql://yback_root:0000@10.10.112.159:3306/job_db"
DATABASE_URL = "mysql+pymysql://ieum:Ieum!2024@14.63.177.168:3306/job_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_structured_description(elementary_content, middle_content, high_content):
    """
    elementary_content, middle_content, high_content 필드를 사용하여 구조화된 설명 생성
    
    Args:
        elementary_content (dict): 초등학생 콘텐츠
        middle_content (dict): 중학생 콘텐츠
        high_content (dict): 고등학생 콘텐츠
    
    Returns:
        str: 구조화된 설명
    """
    sections = []
    
    # 학년별 섹션 생성
    content_map = {
        '초등학생': elementary_content,
        '중학생': middle_content,
        '고등학생': high_content
    }
    
    for level_name, content in content_map.items():
        if not content:
            continue
            
        # 빈 딕셔너리인 경우 건너뛰기
        if not any(content.get(key) for key in ['goal', 'preparation', 'beginning', 'activity', 'finale', 'after']):
            continue
            
        section = f"【{level_name}】\n\n"
        
        # 각 파트별 내용 추가
        parts = {
            'goal': '목표',
            'preparation': '사전 준비',
            'beginning': '도입',
            'activity': '본활동',
            'finale': '마무리',
            'after': '사후활동'
        }
        
        for key, title in parts.items():
            content_value = content.get(key, '')
            if content_value and content_value.strip():
                section += f"■ {title}\n{content_value}\n\n"
        
        sections.append(section)
    
    # 최종 문자열 생성
    return "".join(sections)

def update_descriptions():
    """
    edu_program 테이블에서 ggoomgil 데이터의 description 필드를 업데이트
    """
    session = SessionLocal()
    
    try:
        # ggoomgil 데이터 조회
        query = text("""
            SELECT id, elementary_content, middle_content, high_content 
            FROM edu_program 
            WHERE data_source = 'ggoomgil'
        """)
        
        result = session.execute(query)
        
        update_count = 0
        for row in result:
            try:
                row_id = row[0]
                
                # JSON 문자열을 파이썬 객체로 변환
                elementary_content = json.loads(row[1]) if row[1] else {}
                middle_content = json.loads(row[2]) if row[2] else {}
                high_content = json.loads(row[3]) if row[3] else {}
                
                # 구조화된 설명 생성
                description = create_structured_description(
                    elementary_content, 
                    middle_content, 
                    high_content
                )
                
                # description이 비어있지 않은 경우에만 업데이트
                if description:
                    # 설명 업데이트
                    update_query = text("""
                        UPDATE edu_program 
                        SET description = :description 
                        WHERE id = :id
                    """)
                    
                    session.execute(update_query, {"description": description, "id": row_id})
                    update_count += 1
                    
                    if update_count % 10 == 0:
                        print(f"{update_count}개 레코드 업데이트 완료")
            
            except Exception as e:
                print(f"ID {row[0]} 처리 중 오류 발생: {e}")
                continue
        
        # 변경사항 커밋
        session.commit()
        print(f"총 {update_count}개 레코드의 description이 업데이트되었습니다.")
    
    except Exception as e:
        session.rollback()
        print(f"데이터베이스 업데이트 중 오류 발생: {e}")
    
    finally:
        session.close()

if __name__ == "__main__":
    update_descriptions() 