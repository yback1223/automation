import json
import re
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


# # KT_DB
# KT_DB_DEV_URL=mysql+asyncmy://ieum:Ieum!2024@14.63.177.168:3306/cp_plan
# KT_DB_DEV_SYNC_URL=mysql+pymysql://ieum:Ieum!2024@14.63.177.168:3306/cp_plan
# KT_JOB_DB_DEV_URL=mysql+asyncmy://ieum:Ieum!2024@14.63.177.168:3306/job_db
# KT_JOB_DB_DEV_SYNC_URL=mysql+pymysql://ieum:Ieum!2024@14.63.177.168:3306/job_db

# 데이터베이스 연결
# DB_URL = "mysql+asyncmy://yback_root:0000@10.10.112.148:3306/job_db"
# DB_URL = "mysql+asyncmy://root:Tnstjd12%40@10.10.112.113:3306/job_db"
DB_URL = "mysql+asyncmy://ieum:Ieum!2024@14.63.177.168:3306/job_db"

engine = create_async_engine(DB_URL, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# JSON 파일 경로
json_file_path = "updated_programs_with_classifications.json"

# hir_job_claf 추출 함수 (depth_4의 4자리 숫자만)
def extract_hir_job_claf(classes):
    try:
        if classes and isinstance(classes, list) and "depth_4" in classes[0]:
            return re.findall(r"\d{4}", classes[0]["depth_4"])[0]  # 첫 번째 4자리 숫자만 추출
    except IndexError:
        pass
    return None  # 추출 실패 시 None 반환

# 비동기 데이터 삽입 함수
async def insert_curriculum_ggoomgil():
    async with AsyncSessionLocal() as session:
        try:
            # JSON 파일 로드
            with open(json_file_path, "r", encoding="utf-8") as file:
                programs = json.load(file)

            query = text("""
                INSERT INTO curriculum_ggoomgil (
                    program_name, corp_name, corp_type, link, rough_location, term,
                    apply_date, days, program_time, available_times, headcount, 
                    program_type, fee, school_types, student_types, quals_majors, 
                    notice, how_to_go, applicable_location, elementary_content, 
                    middle_content, high_content, code_detail, hir_job_claf
                ) 
                VALUES (
                    :program_name, :corp_name, :corp_type, :link, :rough_location, :term,
                    :apply_date, :days, :program_time, :available_times, :headcount, 
                    :program_type, :fee, :school_types, :student_types, :quals_majors, 
                    :notice, :how_to_go, :applicable_location, :elementary_content, 
                    :middle_content, :high_content, :code_detail, :hir_job_claf
                )
            """)

            # 데이터 삽입
            for program in programs:
                
                if "," in program.get("headcount"):
                    program["headcount"] = program.get("headcount").replace(",", "")
                elif not program.get("headcount").isdigit():
                    program["headcount"] = "0"

                data = {
                    "program_name": f'[꿈길 진로 체험 프로그램]{program.get("program_name", "")}',
                    "corp_name": program.get("corp_name", ""),
                    "corp_type": program.get("corp_type", ""),
                    "link": program.get("link", ""),
                    "rough_location": program.get("program_rough_location", ""),
                    "term": program.get("program_term", ""),
                    "apply_date": program.get("apply_date", ""),
                    "days": json.dumps(program.get("program_days", [])),  # JSON 필드 변환
                    "program_time": program.get("program_times", ""),
                    "available_times": json.dumps(program.get("available_time", [])),  # JSON 필드 변환
                    "headcount": int(program.get("headcount", 0)),  # 정수 변환
                    "program_type": program.get("program_type", ""),
                    "fee": program.get("program_fee", ""),
                    "school_types": json.dumps(program.get("school_types", [])),  # JSON 필드 변환
                    "student_types": json.dumps(program.get("student_types", [])),  # JSON 필드 변환
                    "quals_majors": json.dumps(program.get("quals_majors", [])),  # JSON 필드 변환
                    "notice": program.get("notice", ""),
                    "how_to_go": program.get("how_to_go", ""),
                    "applicable_location": json.dumps(program.get("appliable_location", [])),  # JSON 필드 변환
                    "elementary_content": json.dumps({
                        "goal": program.get("elementary_goal", ""),
                        "preparation": program.get("elementary_preparation", ""),
                        "beginning": program.get("elementary_beginning", ""),
                        "activity": program.get("elementary_activity", ""),
                        "finale": program.get("elementary_finale", ""),
                        "after": program.get("elementary_after", ""),
                    }),
                    "middle_content": json.dumps({
                        "goal": program.get("middle_goal", ""),
                        "preparation": program.get("middle_preparation", ""),
                        "beginning": program.get("middle_beginning", ""),
                        "activity": program.get("middle_activity", ""),
                        "finale": program.get("middle_finale", ""),
                        "after": program.get("middle_after", ""),
                    }),
                    "high_content": json.dumps({
                        "goal": program.get("high_goal", ""),
                        "preparation": program.get("high_preparation", ""),
                        "beginning": program.get("high_beginning", ""),
                        "activity": program.get("high_activity", ""),
                        "finale": program.get("high_finale", ""),
                        "after": program.get("high_after", ""),
                    }),
                    "code_detail": json.dumps(program.get("classes", [])),  # JSON 필드 변환
                    "hir_job_claf": extract_hir_job_claf(program.get("classes", [])),  # depth_4에서 숫자 4자리 추출
                }

                # SQL 실행
                await session.execute(query, data)

            # 커밋
            await session.commit()
            print("✅ Data inserted successfully into curriculum_ggoomgil!")

        except Exception as e:
            print(f"❌ An error occurred: {e}")
            await session.rollback()

# 실행
if __name__ == "__main__":
    asyncio.run(insert_curriculum_ggoomgil())
