import asyncio
import os
from dotenv import load_dotenv
from db_modifier.update_book_related_jobs import BookRelatedJobsUpdater

async def main():
    # 환경 변수 로드
    load_dotenv()
    
    # DB URL 가져오기
    # db_url = "mysql+asyncmy://yback_root:0000@10.10.112.174:3306/job_db"
    db_url = "mysql+asyncmy://ieum:Ieum!2024@14.63.177.168:3306/job_db"
    if not db_url:
        raise ValueError("DB_URL environment variable is not set")
    
    # JSON 파일 경로
    json_file = "resources/crawled_program_details_modified.json"
    
    # 업데이터 실행
    async with BookRelatedJobsUpdater(db_url) as updater:
        await updater.update_related_jobs(json_file)

if __name__ == "__main__":
    asyncio.run(main()) 