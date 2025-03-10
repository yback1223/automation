import json
import os
from sqlalchemy import create_engine, Column, Integer, String, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# MySQL 데이터베이스 연결 설정
DATABASE_URL = "mysql+pymysql://yback_root:0000@10.10.112.159:3306/job_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# EduProgram 모델 정의
class EduProgram(Base):
    __tablename__ = 'edu_program'
    
    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(String(100), default="")
    data_source = Column(String(60), default="")
    location = Column(String(60), default="")
    rough_location = Column(String(100), default="")
    corp_type = Column(String(255), default="")
    big_category = Column(String(255), default="")
    small_category = Column(String(255), default="")
    image_url = Column(String(255), default="")
    program_name = Column(String(255), default="")
    bookmark_count = Column(Integer, default=0)
    corp_name = Column(String(255), default="")
    apply_date = Column(String(255), default="")
    language = Column(String(255), default="한국어")
    subtitle = Column(String(255), default="없음")
    fee = Column(String(600), default="")
    difficulty = Column(String(60), default="초급")
    program_time = Column(String(255), default="")
    video_count = Column(Integer, default=0)
    link = Column(String(255), default="")
    corp_description = Column(Text, default="")
    description = Column(Text, default="")
    program_curriculum = Column(JSON, default=[])
    term = Column(String(255), default="")
    days = Column(JSON, default=[])
    available_times = Column(JSON, default=[])
    headcount = Column(Integer, default=0)
    program_type = Column(String(255), default="")
    school_types = Column(JSON, default=[])
    student_types = Column(JSON, default=[])
    quals_majors = Column(JSON, default=[])
    notice = Column(Text, default="")
    how_to_go = Column(Text, default="")
    applicable_location = Column(JSON, default=[])
    elementary_content = Column(JSON, default=[])
    middle_content = Column(JSON, default=[])
    high_content = Column(JSON, default=[])
    code_detail = Column(JSON, default=[])
    hir_job_claf = Column(String(60), default="")

# 테이블 생성은 이미 존재하는 테이블을 사용하므로 주석 처리
# Base.metadata.create_all(bind=engine)

def insert_json_to_db(json_file_path, data_source):
    """
    JSON 파일의 데이터를 데이터베이스에 삽입하는 함수
    
    Args:
        json_file_path (str): JSON 파일 경로
        data_source (str): 데이터 소스 (youtube, class101, ggoomgil 등)
    """
    # JSON 파일 읽기
    with open(json_file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            print(f"{json_file_path} 파일을 성공적으로 로드했습니다.")
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}")
            print(f"파일 내용 확인 중: {f.read()[:100]}...")  # 파일 내용 일부 출력
            return
    
    # 데이터 소스에 따른 매핑 정의
    field_mappings = {
        'youtube': {
            'program_id': lambda item: f"{item.get('id', '')}_youtube",
            'data_source': lambda item: 'youtube',
            'location': lambda item: '온라인',
            'rough_location': lambda item: '',
            'corp_type': lambda item: '개인사업장',
            'big_category': lambda item: item.get('bigCategory', ''),
            'small_category': lambda item: item.get('smallCategory', ''),
            'image_url': lambda item: item.get('image', ''),
            'program_name': lambda item: item.get('course_name', ''),
            'bookmark_count': lambda item: item.get('bookmarks', 0),
            'corp_name': lambda item: item.get('creator', ''),
            'apply_date': lambda item: item.get('updated_date', ''),
            'language': lambda item: item.get('lang', '한국어'),
            'subtitle': lambda item: item.get('subtitles', '없음'),
            'fee': lambda item: item.get('discounted_price', ''),
            'difficulty': lambda item: item.get('program_difficulty', '초급'),
            'program_time': lambda item: item.get('program_total_time', ''),
            'video_count': lambda item: int(item.get('program_video_count', 0)),
            'link': lambda item: item.get('program_link', ''),
            'corp_description': lambda item: item.get('program_creator_description', ''),
            'description': lambda item: item.get('description', ''),
            'program_curriculum': lambda item: item.get('program_curriculum', []),
            'student_types': lambda item: item.get('student_type', []),
        },
        'class101': {
            'program_id': lambda item: f"{item.get('program_link', '').split('/')[-1]}_class101",
            'data_source': lambda item: 'class101',
            'location': lambda item: '온라인',
            'rough_location': lambda item: '',
            'corp_type': lambda item: '개인사업장',
            'big_category': lambda item: item.get('program_first_category', ''),
            'small_category': lambda item: item.get('program_second_category', ''),
            'image_url': lambda item: item.get('program_image_url', ''),
            'program_name': lambda item: item.get('program_name', ''),
            'bookmark_count': lambda item: item.get('program_bookmark_count', 0),
            'corp_name': lambda item: item.get('program_creator', ''),
            'apply_date': lambda item: item.get('program_start_date', ''),
            'language': lambda item: item.get('program_audio_languages', '한국어'),
            'subtitle': lambda item: item.get('program_subtitles', '없음'),
            'fee': lambda item: item.get('program_price', ''),
            'difficulty': lambda item: item.get('program_difficulty', '초급'),
            'program_time': lambda item: item.get('program_total_time', ''),
            'video_count': lambda item: int(item.get('program_video_count', 0).replace("영상","").replace("개","")),
            'link': lambda item: item.get('program_link', ''),
            'corp_description': lambda item: item.get('program_creator_description', ''),
            'description': lambda item: item.get('program_description_by_gemini', ''),
            'program_curriculum': lambda item: item.get('program_curriculum', []),
            'student_types': lambda item: ['초', '중', '고'],
        },
        'ggoomgil': {
            'program_id': lambda item: f"{item.get('id', '')}_ggoomgil",
            'data_source': lambda item: 'ggoomgil',
            'location': lambda item: item.get('location', ''),
            'rough_location': lambda item: item.get('rough_location', ''),
            'corp_type': lambda item: item.get('corp_type', ''),
            'big_category': lambda item: item.get('bigCategory', ''),
            'small_category': lambda item: item.get('smallCategory', ''),
            'image_url': lambda item: item.get('image', ''),
            'program_name': lambda item: item.get('course_name', ''),
            'bookmark_count': lambda item: item.get('bookmarks', 0),
            'corp_name': lambda item: item.get('creator', ''),
            'apply_date': lambda item: item.get('updated_date', ''),
            'language': lambda item: item.get('lang', '한국어'),
            'subtitle': lambda item: item.get('subtitles', '없음'),
            'fee': lambda item: item.get('discounted_price', ''),
            'difficulty': lambda item: item.get('program_difficulty', '초급'),
            'program_time': lambda item: item.get('program_total_time', ''),
            'video_count': lambda item: int(item.get('program_video_count', 0).replace("영상","").replace("개","")),
            'link': lambda item: item.get('program_link', ''),
            'corp_description': lambda item: item.get('program_creator_description', ''),
            'description': lambda item: item.get('description', ''),
            'program_curriculum': lambda item: item.get('program_curriculum', []),
            'student_types': lambda item: item.get('student_type', []),
            'days': lambda item: item.get('program_days', []),
            'available_times': lambda item: item.get('program_times', []),
            'headcount': lambda item: item.get('headcount', 0),
        }
    }
    
    # 데이터 소스에 맞는 매핑 가져오기
    mapping = field_mappings.get(data_source, {})
    
    # 데이터베이스 세션 생성
    session = SessionLocal()
    
    try:
        # 데이터 형식에 따라 처리 (배열 또는 객체)
        items = data
        if not isinstance(data, list):
            # 데이터가 객체인 경우 (예: YouTube 카테고리별 구조)
            if data_source == 'youtube':
                items = []
                for category, videos in data.items():
                    for video in videos:
                        video['bigCategory'] = category
                        items.append(video)
            else:
                items = [data]
        
        print(f"처리할 항목 수: {len(items)}")
        
        # 각 항목을 데이터베이스에 삽입
        for item in items:
            # 새 EduProgram 객체 생성
            edu_program = EduProgram()
            
            # 매핑에 따라 필드 설정
            for db_field, getter_func in mapping.items():
                try:
                    value = getter_func(item)
                    setattr(edu_program, db_field, value)
                except Exception as e:
                    print(f"필드 '{db_field}' 설정 중 오류 발생: {e}")
            
            # 데이터베이스에 추가
            session.add(edu_program)
        
        # 변경사항 커밋
        session.commit()
        print(f"{len(items)}개의 항목이 성공적으로 데이터베이스에 삽입되었습니다.")
    
    except Exception as e:
        session.rollback()
        print(f"데이터베이스 삽입 중 오류 발생: {e}")
    
    finally:
        session.close()

def main():
    # 각 데이터 소스별 파일 처리
    data_sources = {
        'youtube': './youtube/code/youtube_courses_to_db.json',
        # 'class101': './class101/code/crawled_program_details_tmp.json'
        # 'ggoomgil': './ggoomgil/code/ggoomgil_courses.json'
    }
    
    for source, file_path in data_sources.items():
        if os.path.exists(file_path):
            print(f"{source} 데이터 처리 중...")
            
            # 파일 확장자 확인
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.json':
                # JSON 파일은 직접 처리
                insert_json_to_db(file_path, source)
            elif file_ext == '.js':
                # JavaScript 파일에서 JSON 데이터 추출
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # JavaScript 파일에서 JSON 부분 추출
                    start_idx = content.find('const courses = [') + len('const courses = [')
                    end_idx = content.rfind('];')
                    
                    if start_idx > len('const courses = [') - 1 and end_idx > 0:
                        json_str = '[' + content[start_idx:end_idx] + ']'
                        
                        # 임시 JSON 파일 생성
                        temp_json_file = f"{source}_temp.json"
                        with open(temp_json_file, 'w', encoding='utf-8') as temp_f:
                            temp_f.write(json_str)
                        
                        # 데이터베이스에 삽입
                        insert_json_to_db(temp_json_file, source)
                        
                        # 임시 파일 삭제
                        os.remove(temp_json_file)
                    else:
                        print(f"경고: {file_path} 파일에서 JSON 데이터를 추출할 수 없습니다.")
            else:
                print(f"경고: {file_path} 파일 형식을 처리할 수 없습니다.")
        else:
            print(f"경고: {file_path} 파일이 존재하지 않습니다.")

if __name__ == "__main__":
    main() 