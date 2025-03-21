import json
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import re

class BookRelatedJobsUpdater:
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

    async def load_major_data(self, json_file: str) -> list:
        """JSON 파일에서 계열 정보를 로드합니다."""
        with open(json_file, "r", encoding="utf-8") as f:
            return json.load(f)

    async def get_books(self):
        """major_1이 있는 book 데이터를 가져옵니다."""
        select_query = text("""
            SELECT id, major_1, major_2, major_3 
            FROM book 
            WHERE major_1 IS NOT NULL
        """)
        result = await self.session.execute(select_query)
        return result.fetchall()

    async def update_book_related_jobs(self, book_id: int, related_jobs: list):
        """book의 related_jobs를 업데이트합니다."""
        # 리스트를 공백으로 구분된 문자열로 변환
        related_jobs_str = " ".join(related_jobs)
        
        update_query = text("""
            UPDATE book 
            SET related_jobs = :related_jobs
            WHERE id = :id
        """)
        await self.session.execute(
            update_query,
            {
                "id": book_id,
                "related_jobs": related_jobs_str
            }
        )

    def clean_job_string(self, job: str) -> str:
        """직업 문자열에서 괄호와 그 안의 내용을 제거하고 모든 공백을 없앱니다."""
        # 괄호와 그 안의 내용 제거
        job = re.sub(r'\([^)]*\)', '', job)
        # 모든 공백 제거
        job = job.replace(" ", "")
        return job

    def find_value_in_strings(self, target: str, strings: list) -> bool:
        """주어진 문자열들 중 하나라도 target을 포함하는지 확인합니다."""
        target = target.replace(" ", "")
        for s in strings:
            # 괄호와 그 안의 내용을 제거하고 모든 공백을 없앤 문자열과 비교
            cleaned_s = self.clean_job_string(s)
            if target in cleaned_s:
                return True
        return False

    async def process_book(self, book, major_data):
        """개별 book을 처리합니다."""
        book_id, major_1, major_2, major_3 = book
        print(f"Processing book {book_id} with major_1: {major_1}, major_2: {major_2}, major_3: {major_3}")
        try:
            # 1. major_1로 major_location이 일치하는 객체들 찾기
            filtered_data = [data for data in major_data if data['major_location'] == major_1]
            if not filtered_data:
                return False

            # 2. major_2 필터링
            if major_2 and major_2 != "N.C.E.":
                major_2_terms = major_2.split("·")
                major_2_filtered = []
                for term in major_2_terms:
                    term = term.strip()
                    for data in filtered_data:
                        if self.find_value_in_strings(term, data['major_related_jobs'].split(",")):
                            major_2_filtered.append(data)
                if major_2_filtered:
                    filtered_data = major_2_filtered

            # 3. major_3 필터링
            if major_3 and major_3 != "N.C.E.":
                major_3_terms = major_3.split("·")
                major_3_filtered = []
                for term in major_3_terms:
                    term = term.strip()
                    for data in filtered_data:
                        if self.find_value_in_strings(term, data['major_related_jobs'].split(",")):
                            major_3_filtered.append(data)
                if major_3_filtered:
                    filtered_data = major_3_filtered

            # 4. 결과 합치기
            all_related_jobs = set()
            for data in filtered_data:
                jobs = [self.clean_job_string(job.strip()) for job in data['major_related_jobs'].split(",")]
                all_related_jobs.update(jobs)

            if all_related_jobs:
                await self.update_book_related_jobs(book_id, list(all_related_jobs))
                print(f"Updated book {book_id} with {len(all_related_jobs)} related jobs")
                return True

        except Exception as e:
            print(f"Error processing book {book_id}: {str(e)}")
            pass

        return False

    async def update_related_jobs(self, json_file: str):
        """전체 업데이트 프로세스를 실행합니다."""
        try:
            # JSON 파일에서 계열 정보 로드
            major_data = await self.load_major_data(json_file)

            # book 데이터 가져오기
            books = await self.get_books()

            updated_count = 0
            for book in books:
                if await self.process_book(book, major_data):
                    updated_count += 1

            await self.session.commit()
            print(f"✅ Successfully updated {updated_count} books with related_jobs!")

        except Exception as e:
            print(f"❌ An error occurred: {e}")
            await self.session.rollback()
            raise
