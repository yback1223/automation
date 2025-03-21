import asyncio
import os
from db_updater.edu_program import EduProgram

async def main():
    # DB URL 설정
    # db_url = "mysql+asyncmy://ieum:Ieum!2024@14.63.177.168:3306/job_db"
    db_url = "mysql+asyncmy://yback_root:0000@10.10.112.174:3306/job_db"
    
    # job_hir_codes.json 파일 경로 확인
    job_hir_codes_path = os.path.join("resources", "job_hir_codes.json")
    if not os.path.exists(job_hir_codes_path):
        print(f"❌ Error: job_hir_codes.json file not found at {job_hir_codes_path}")
        print("Please make sure the file exists before running this script.")
        return
    
    # 업데이터 실행
    async with EduProgram(db_url) as updater:
        await updater.update_hir_job_code()

if __name__ == "__main__":
    asyncio.run(main()) 