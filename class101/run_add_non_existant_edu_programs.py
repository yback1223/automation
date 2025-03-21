import json
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
    
    # JSON 파일 경로
    json_file_path = os.path.join("resources", "class101_program_details_gemini.json")
    
    # 업데이터 실행
    async with EduProgram(db_url) as updater:
        # JSON 파일 읽기
        with open(json_file_path, 'r', encoding='utf-8') as f:
            programs = json.load(f)
        
        # 프로그램 추가
        await updater.add_edu_programs(programs)

if __name__ == "__main__":
    asyncio.run(main())
