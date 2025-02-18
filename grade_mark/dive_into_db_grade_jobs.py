import json
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# 데이터베이스 URL
DB_URL = "mysql+asyncmy://yback_root:0000@10.10.112.148:3306/job_db"

# 데이터베이스 연결 설정
engine = create_async_engine(DB_URL, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# JSON 파일 경로
json_file_path = "merged_subject_data.json"


async def insert_high_school_grade_subject():
    async with AsyncSessionLocal() as session:
        try:
            # JSON 파일 로드
            with open(json_file_path, "r", encoding="utf-8") as file:
                subjects = json.load(file)

            # 직업 정보 가져오기
            job_clf_query = text("SELECT job_clf_id, job_name FROM job_clf")
            job_clf_result = await session.execute(job_clf_query)
            job_clf_data = job_clf_result.fetchall()

            # 직업명을 딕셔너리로 매핑 (공백 제거 및 "등" 제거 후 비교)
            job_mapping = {job_name.replace(" ", "").replace("등", ""): job_id for job_id, job_name in job_clf_data}

            # high_school_grade_subject INSERT 쿼리
            subject_insert_query = text("""
                INSERT INTO high_school_grade_subject (
                    subject, subject_type, subject_category, subject_description,
                    related_major, related_job, grade, grade_variance, grade_range,
                    grade_process_type, is_CSAT_subject, is_rank_record_subject, is_special_high_school_subject
                ) VALUES (
                    :subject, :subject_type, :subject_category, :subject_description,
                    :related_major, :related_job, :grade, :grade_variance, :grade_range,
                    :grade_process_type, :is_CSAT_subject, :is_rank_record_subject, :is_special_high_school_subject
                )
            """)

            # job_grade_subjects INSERT 쿼리
            job_grade_subject_insert_query = text("""
                INSERT INTO job_grade_subjects (job_clf_id, subject_id)
                VALUES (:job_clf_id, :subject_id)
            """)

            for subject in subjects:
                # 관련 직업 필드 정리
                raw_related_jobs = subject.get("관련 직업", "")
                related_jobs = [job.strip().replace("등", "") for job in raw_related_jobs.split(",")]

                # 과목 데이터 삽입
                subject_data = {
                    "subject": subject["과목명"],
                    "subject_type": subject["유형"],
                    "subject_category": subject["교과(군)"],
                    "subject_description": subject.get("과목설명", ""),
                    "related_major": subject.get("관련 학과", ""),
                    "related_job": raw_related_jobs,
                    "grade": subject["기본학점"],
                    "grade_variance": subject["증감범위"],
                    "grade_range": subject["편성학점"],
                    "grade_process_type": subject["성적처리유형"],
                    "is_CSAT_subject": subject["수능출제여부"],
                    "is_rank_record_subject": subject["석차등급기재여부"],
                    "is_special_high_school_subject": subject.get("특목고과목여부", False)
                }

                # 과목 삽입 실행
                result = await session.execute(subject_insert_query, subject_data)
                subject_id = result.lastrowid  # 삽입된 과목 ID 가져오기

                # 관련 직업과 매칭하여 job_grade_subjects 삽입
                for job in related_jobs:
                    job_id = job_mapping.get(job.replace(" ", ""))
                    if job_id:
                        await session.execute(job_grade_subject_insert_query, {"job_clf_id": job_id, "subject_id": subject_id})

            # 커밋 실행
            await session.commit()
            print("✅ 데이터 삽입 완료: high_school_grade_subject & job_grade_subjects")

        except Exception as e:
            print(f"❌ 에러 발생: {e}")
            await session.rollback()

# 실행
if __name__ == "__main__":
    asyncio.run(insert_high_school_grade_subject())
