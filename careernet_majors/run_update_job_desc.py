import os
import sys
import asyncio

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_modifier import JobDescriptionUpdater

# DB 연결 정보
DB_URL = "mysql+asyncmy://yback_root:0000@localhost:3306/job_db"

# JSON 파일 경로
JSON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "crawled_program_details_modified.json")

async def main():
    try:
        async with JobDescriptionUpdater(DB_URL) as updater:
            await updater.update_major_field(JSON_FILE)
    except Exception as e:
        print(f"Error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

