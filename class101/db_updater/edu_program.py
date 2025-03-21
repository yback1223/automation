import random
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import json

class EduProgram:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.engine = None
        self.session = None

    async def __aenter__(self):
        self.engine = create_async_engine(self.db_url, pool_pre_ping=True)
        AsyncSessionLocal = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)
        self.session = AsyncSessionLocal()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        if self.engine:
            await self.engine.dispose()

    async def get_total_count(self) -> int:
        """edu_program 테이블의 전체 row 수를 가져옵니다."""
        query = text("SELECT COUNT(*) FROM edu_program")
        result = await self.session.execute(query)
        return result.scalar()

    async def get_all_ids(self) -> list:
        """edu_program 테이블의 모든 id를 가져옵니다."""
        query = text("SELECT id FROM edu_program")
        result = await self.session.execute(query)
        return [row[0] for row in result.fetchall()]

    async def update_ids(self, id_new_id_pairs: list):
        """id를 업데이트합니다."""
        # 1. 먼저 모든 id를 임시로 큰 숫자로 변경
        temp_update_query = text("""
            UPDATE edu_program 
            SET id = id + 1000000
        """)
        await self.session.execute(temp_update_query)
        
        # 2. 새로운 id로 업데이트
        update_query = text("""
            UPDATE edu_program 
            SET id = :new_id
            WHERE id = :old_id + 1000000
        """)
        for old_id, new_id in id_new_id_pairs:
            await self.session.execute(
                update_query,
                {
                    "old_id": old_id,
                    "new_id": new_id
                }
            )

    async def update_ids_random(self):
        """전체 업데이트 프로세스를 실행합니다."""
        try:
            # 전체 row 수 가져오기
            total_count = await self.get_total_count()
            print(f"Total rows: {total_count}")

            # 모든 id 가져오기
            all_ids = await self.get_all_ids()
            
            # 1부터 N까지의 숫자를 랜덤하게 섞기
            new_ids = list(range(1, total_count + 1))
            random.shuffle(new_ids)
            
            # id와 new_id를 매칭
            id_new_id_pairs = list(zip(all_ids, new_ids))
            
            # id 업데이트
            await self.update_ids(id_new_id_pairs)
            
            await self.session.commit()
            print(f"✅ Successfully updated ids for {total_count} rows!")

        except Exception as e:
            print(f"❌ An error occurred: {e}")
            await self.session.rollback()
            raise

    def transform_program_data(self, program: dict) -> dict:
        """프로그램 데이터를 DB 스키마에 맞게 변환합니다."""
        # video_count 처리를 위한 헬퍼 함수
        def parse_video_count(count):
            if not count:
                return 0
            count_str = str(count).replace("영상", "").replace("개", "")
            try:
                return int(count_str)
            except ValueError:
                return 0

        # JSON 필드를 문자열로 변환하는 헬퍼 함수
        def json_to_str(value):
            if value is None:
                return json.dumps([])
            return json.dumps(value, ensure_ascii=False)

        return {
            'program_id': f"{program.get('program_link', '').split('/')[-1]}_class101",
            'data_source': 'class101',
            'location': '온라인',
            'rough_location': '',
            'corp_type': '개인사업장',
            'big_category': program.get('program_first_category', ''),
            'small_category': program.get('program_second_category', ''),
            'image_url': program.get('program_image_url', ''),
            'program_name': program.get('program_name', ''),
            'bookmark_count': program.get('program_bookmark_count', 0),
            'corp_name': program.get('program_creator', ''),
            'apply_date': program.get('program_start_date', ''),
            'language': program.get('program_audio_languages', '한국어'),
            'subtitle': program.get('program_subtitles', '없음'),
            'fee': program.get('program_price', ''),
            'difficulty': program.get('program_difficulty', '초급'),
            'program_time': program.get('program_total_time', ''),
            'video_count': parse_video_count(program.get('program_video_count')),
            'link': program.get('program_link', ''),
            'corp_description': program.get('program_creator_description', ''),
            'description': program.get('program_description_by_gemini', ''),
            'program_curriculum': json_to_str(program.get('program_curriculum')),
            'term': '',
            'days': json_to_str([]),
            'available_times': json_to_str([]),
            'headcount': 0,
            'program_type': '',
            'school_types': json_to_str([]),
            'student_types': json_to_str(['초', '중', '고']),
            'quals_majors': json_to_str([]),
            'notice': '',
            'how_to_go': '',
            'applicable_location': json_to_str([]),
            'elementary_content': json_to_str([]),
            'middle_content': json_to_str([]),
            'high_content': json_to_str([]),
            'code_detail': json_to_str([]),
            'hir_job_claf': ''
        }

    async def check_program_exists(self, program_id: str) -> bool:
        """program_id가 이미 존재하는지 확인합니다."""
        query = text("SELECT COUNT(*) FROM edu_program WHERE program_id = :program_id")
        result = await self.session.execute(query, {"program_id": program_id})
        count = result.scalar()
        return count > 0

    async def add_edu_programs(self, programs: list) -> None:
        """edu_program 테이블에 새로운 프로그램을 추가합니다."""
        try:
            for program in programs:
                # 데이터 변환
                transformed_data = self.transform_program_data(program)
                
                # program_id로 존재 여부 확인
                exists = await self.check_program_exists(transformed_data["program_id"])
                
                if not exists:
                    # INSERT 쿼리 생성
                    columns = ", ".join(transformed_data.keys())
                    values = ", ".join(f":{key}" for key in transformed_data.keys())
                    
                    query = text(f"""
                        INSERT INTO edu_program 
                        ({columns}) 
                        VALUES ({values})
                    """)
                    
                    await self.session.execute(query, transformed_data)
                    print(f"Added new program: {transformed_data['program_name']}")
                else:
                    print(f"Program already exists: {transformed_data['program_name']}")
            
            await self.session.commit()
            print("All programs processed successfully")
        except Exception as e:
            await self.session.rollback()
            print(f"Error adding programs: {str(e)}")
            raise

    async def update_audio_program_time(self):
        """program_time에 '음성'이 포함된 레코드들의 subtitle을 업데이트하고 program_time을 초기화합니다."""
        try:
            # 1. 음성이 포함된 레코드 조회
            select_query = text("""
                SELECT id, program_time 
                FROM edu_program 
                WHERE program_time LIKE '%음성%'
            """)
            result = await self.session.execute(select_query)
            records = result.fetchall()
            
            if not records:
                print("No records found with '음성' in program_time")
                return
            
            # 2. 각 레코드 업데이트
            update_query = text("""
                UPDATE edu_program 
                SET subtitle = :program_time,
                    program_time = '0'
                WHERE id = :id
            """)
            
            for record in records:
                id, program_time = record
                await self.session.execute(
                    update_query,
                    {
                        "id": id,
                        "program_time": program_time
                    }
                )
                print(f"Updated record id {id}: moved '{program_time}' to subtitle")
            
            await self.session.commit()
            print(f"✅ Successfully updated {len(records)} records!")
            
        except Exception as e:
            await self.session.rollback()
            print(f"❌ An error occurred: {e}")
            raise

    async def swap_language_and_subtitle(self):
        """program_time이 0인 레코드들의 language와 subtitle을 서로 바꿉니다."""
        try:
            # 1. program_time이 0인 레코드 조회
            select_query = text("""
                SELECT id, language, subtitle 
                FROM edu_program 
                WHERE program_time = '0'
            """)
            result = await self.session.execute(select_query)
            records = result.fetchall()
            
            if not records:
                print("No records found with program_time = '0'")
                return
            
            # 2. 각 레코드의 language와 subtitle swap
            update_query = text("""
                UPDATE edu_program 
                SET language = :subtitle,
                    subtitle = :language
                WHERE id = :id
            """)
            
            for record in records:
                id, language, subtitle = record
                await self.session.execute(
                    update_query,
                    {
                        "id": id,
                        "language": language,
                        "subtitle": subtitle
                    }
                )
                print(f"Updated record id {id}: swapped language '{language}' with subtitle '{subtitle}'")
            
            await self.session.commit()
            print(f"✅ Successfully swapped language and subtitle for {len(records)} records!")
            
        except Exception as e:
            await self.session.rollback()
            print(f"❌ An error occurred: {e}")
            raise


