import asyncio
import os
from dotenv import load_dotenv
from db_updater.edu_program import EduProgram

async def main():
    # 환경 변수 로드
    load_dotenv()
    
    # DB URL 가져오기
    db_url = "mysql+asyncmy://ieum:Ieum!2024@14.63.177.168:3306/job_db"
    if not db_url:
        raise ValueError("DB_URL environment variable is not set")
    
    # 업데이터 실행
    async with EduProgram(db_url) as edu_program:
        await edu_program.update_ids_random()

if __name__ == "__main__":
    asyncio.run(main())
