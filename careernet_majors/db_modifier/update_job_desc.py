import json
import asyncio
import pymysql
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

class JobDescriptionUpdater:
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

    async def load_major_data(self, json_file: str) -> dict:
        """JSON 파일에서 계열 정보를 로드합니다."""
        with open(json_file, "r", encoding="utf-8") as f:
            return json.load(f)

    async def get_job_descriptions(self):
        """core_major가 있는 job_desc 데이터를 가져옵니다."""
        select_query = text("""
            SELECT id, name, relate_job, relate_qualification, core_major, major_field 
            FROM job_desc 
        """)
        result = await self.session.execute(select_query)
        return result.fetchall()

    async def update_job_major_field(self, job_id: int, major_field: str):
        """job_desc의 major_field를 업데이트합니다."""
        update_query = text("""
            UPDATE job_desc 
            SET major_field = :major_field
            WHERE id = :id
        """)
        await self.session.execute(
            update_query,
            {
                "id": job_id,
                "major_field": major_field
            }
        )

    async def process_job_description(self, job_desc, major_data):
        """개별 job_desc를 처리합니다."""
        job_id, job_name, relate_job, relate_qualification, core_major_str, current_major_field = job_desc

        # 문자열 리스트로 변환하고 모든 공백 제거
        relate_job_list = [job.replace(" ", "") for job in relate_job.replace("[", '').replace("]", '').replace("'", '').split(",")]
        relate_qualification_list = [qual.replace(" ", "") for qual in relate_qualification.replace("[", '').replace("]", '').replace("'", '').split(",")]
        core_major_list = [major.replace(" ", "") for major in core_major_str.replace("[", '').replace("]", '').replace("'", '').split(",")]
        
        def find_value_in_strings(target, strings):
            """주어진 문자열들 중 하나라도 target을 포함하는지 확인합니다."""
            target = target.replace(" ", "")
            for s in strings:
                if target in s.replace(" ", ""):
                    return True
            return False
        
        try:
            # 각 major_data 객체를 순회하면서 조건 확인
            found_majors = set()
            for major_info in major_data:
                # 1. job_name 확인 (major_name과 비교)
                if job_name.replace(" ", "") in major_info['major_name'].replace(" ", ""):
                    found_majors.add(major_info['major_location'])
                    continue
                
                # 2. relate_job_list 확인 (major_related_jobs와 비교)
                major_related_jobs = major_info['major_related_jobs'].split(",")
                for job in relate_job_list:
                    if job and find_value_in_strings(job, major_related_jobs):
                        found_majors.add(major_info['major_location'])
                        break
                
                # 3. relate_qualification_list 확인 (major_related_jobs와 비교)
                for qualification in relate_qualification_list:
                    if qualification and find_value_in_strings(qualification, major_related_jobs):
                        found_majors.add(major_info['major_location'])
                        break
                
                # 4. core_major_list 확인 (major_related_majors와 비교)
                major_related_majors = major_info['major_related_majors'].split(",")
                for major in core_major_list:
                    if major and find_value_in_strings(major, major_related_majors):
                        found_majors.add(major_info['major_location'])
                        break
            
            if found_majors:
                # 찾은 계열들을 major_field에 저장
                major_field = json.dumps(list(found_majors), ensure_ascii=False)
                await self.update_job_major_field(job_id, major_field)
                print(f"Updated {job_name} with major_field: {major_field}")
                return True
            
        except Exception as e:
            print(f"Error processing {job_name}: {str(e)}")
            pass
        
        return False

    async def update_major_field(self, json_file: str):
        """전체 업데이트 프로세스를 실행합니다."""
        try:
            # JSON 파일에서 계열 정보 로드
            major_data = await self.load_major_data(json_file)

            # job_desc 데이터 가져오기
            job_descs = await self.get_job_descriptions()

            updated_count = 0
            for job_desc in job_descs:
                if await self.process_job_description(job_desc, major_data):
                    updated_count += 1

            await self.session.commit()
            print(f"✅ Successfully updated {updated_count} job descriptions with major_field!")

        except Exception as e:
            print(f"❌ An error occurred: {e}")
            await self.session.rollback()
            raise
