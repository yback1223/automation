import json
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# 데이터베이스 연결
# DB_URL = "mysql+asyncmy://yback_root:0000@10.10.112.148:3306/job_db"
DB_URL = "mysql+asyncmy://ieum:Ieum!2024@14.63.177.168:3306/job_db"

engine = create_async_engine(DB_URL, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# JSON 파일 경로
json_file_path = "final_merged_data.json"

# 비동기 데이터 삽입 함수
async def insert_work_carrier_job():
    async with AsyncSessionLocal() as session:
        try:
            # JSON 파일 로드
            with open(json_file_path, "r", encoding="utf-8") as file:
                jobs = json.load(file)

            query = text("""
                INSERT INTO work_career_job (
                    job_name, job_desc, todo, learning_period, mastering_period, 
                    skill, difficulty, physical_work, work_place, work_environment, 
                    similar_name, relate_job, relate_qual, hir_job_claf, std_job_claf, 
                    std_ind_claf, hir_job_desc, analized_year, relate_major, refer_from, 
                    core_skill, aptitude_and_interest, note, tag
                ) 
                VALUES (
                    :job_name, :job_desc, :todo, :learning_period, :mastering_period, 
                    :skill, :difficulty, :physical_work, :work_place, :work_environment, 
                    :similar_name, :relate_job, :relate_qual, :hir_job_claf, :std_job_claf, 
                    :std_ind_claf, :hir_job_desc, :analized_year, :relate_major, :refer_from, 
                    :core_skill, :aptitude_and_interest, :note, :tag
                )
            """)

            # 데이터 삽입
            for job in jobs:
                # 필드 매핑
                data = {
                    "job_name": job.get("직업명", ""),
                    "job_desc": job.get("직업설명", ""),
                    "todo": job.get("수행직무/하는일", ""),
                    "learning_period": job.get("정규교육", ""),
                    "mastering_period": job.get("숙련기간", ""),
                    "skill": job.get("직무기능", ""),
                    "difficulty": job.get("작업강도", ""),
                    "physical_work": job.get("육체활동", ""),
                    "work_place": job.get("작업장소", ""),
                    "work_environment": job.get("작업환경", ""),
                    "similar_name": job.get("유사명칭", ""),
                    "relate_job": job.get("관련직업", ""),
                    "relate_qual": job.get("관련자격_면허", ""),
                    "hir_job_claf": job.get("고용직업분류_세분류", ""),  # 4자리 숫자
                    "std_job_claf": job.get("표준직업분류_세분류", ""),  # 4자리 숫자
                    "std_ind_claf": job.get("표준산업분류_세분류", ""),  # 4자리 코드
                    "hir_job_desc": job.get("고용직업분류_3_설명", ""),
                    "analized_year": job.get("조사연도", ""),
                    "relate_major": job.get("관련학과", ""),
                    "refer_from": job.get("출처", ""),
                    "core_skill": job.get("핵심능력", ""),
                    "aptitude_and_interest": job.get("적성 및 흥미", ""),
                    "note": job.get("비고", ""),
                    "tag": job.get("태그", ""),
                }

                # SQL 실행
                await session.execute(query, data)

            # 커밋
            await session.commit()
            print("✅ Data inserted successfully into work_carrier_job!")

        except Exception as e:
            print(f"❌ An error occurred: {e}")
            await session.rollback()

# 실행
if __name__ == "__main__":
    asyncio.run(insert_work_carrier_job())
