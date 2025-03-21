import asyncio
from db_updater.edu_program import EduProgram

async def main():
    # DB URL 설정
    db_url = "mysql+asyncmy://ieum:Ieum!2024@14.63.177.168:3306/job_db"
    
    # 업데이터 실행
    async with EduProgram(db_url) as updater:
        # 1. program_time에 '음성'이 포함된 레코드 처리
        await updater.update_audio_program_time()
        
        # 2. program_time이 0인 레코드들의 language와 subtitle swap
        await updater.swap_language_and_subtitle()

if __name__ == "__main__":
    asyncio.run(main()) 