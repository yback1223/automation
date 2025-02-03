import json
import asyncio
import pymysql
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# DB_URL = "mysql+asyncmy://ieum:Ieum!2024@14.63.177.168:3306/job_db"
# DB_URL = "mysql+asyncmy://yback_root:0000@10.10.112.148:3306/job_db"
DB_URL = "mysql+asyncmy://root:Tnstjd12%40@10.10.112.113:3306/job_db"
engine = create_async_engine(DB_URL, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def insert_youtube_data(json_file: str):
    async with AsyncSessionLocal() as session:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            query = text("""
                INSERT INTO youtube_job_crawled_data (
                    category, search_keyword, url, title, channel, video_description, 
                    posted_date, views, likes, comments, video_length, video_quality
                ) VALUES (:category, :search_keyword, :url, :title, :channel, :video_description, 
                    :posted_date, :views, :likes, :comments, :video_length, :video_quality)
            """)

            for item in data:
                youtube_data = {
                    "category": item.get("카테고리"),
                    "search_keyword": item.get("검색키워드"),
                    "url": item.get("영상 URL"),
                    "title": item.get("제목"),
                    "channel": item.get("채널명"),
                    "video_description": item.get("설명"),
                    "posted_date": datetime.strptime(item.get("게시일"), "%Y-%m-%dT%H:%M:%SZ"),
                    "views": int(item.get("조회수") or 0),
                    "likes": int(item.get("좋아요 수") or 0),
                    "comments": int(item.get("댓글 수") or 0),
                    "video_length": item.get("영상 길이"),
                    "video_quality": item.get("화질")
                }

                result = await session.execute(query, youtube_data)
                youtube_job_keyword_id = result.lastrowid

                # 고용직업분류코드 연결
                for hir_code in item.get("고용직업분류코드", []):
                    await session.execute(
                        text("""
                        INSERT INTO hir_code_youtubes (job_hir_code, youtube_job_keyword_id)
                        VALUES (:job_hir_code, :youtube_job_keyword_id)
                        """),
                        {"job_hir_code": hir_code[:4], "youtube_job_keyword_id": youtube_job_keyword_id}
                    )

            await session.commit()
            print("✅ Data inserted successfully into youtube_job_crawled_data and hir_code_youtubes!")
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            await session.rollback()

# 실행
if __name__ == "__main__":
    asyncio.run(insert_youtube_data("youtube_results_cleared.json"))
