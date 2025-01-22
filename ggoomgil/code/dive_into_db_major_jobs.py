import json
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Database connection
# DB_URL = "mysql+asyncmy://ieum:Ieum!2024@14.63.177.168:3306/job_db"
DB_URL = "mysql+asyncmy://yback_root:0000@10.10.112.148:3306/cp_plan"
engine = create_async_engine(DB_URL, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# JSON file path
json_file_path = "main_job_crawled_data.json"

# Function to insert data into job_db.ko_university
def normalize_university_name(university_name):
    # Helper function to clean university names
    import re
    return re.sub(r"[\(\[].*?[\)\]]", "", university_name).strip()

async def insert_universities():
    async with AsyncSessionLocal() as session:
        try:
            with open(json_file_path, "r", encoding="utf-8") as file:
                universities = json.load(file)

            # Iterate over JSON objects and insert into database
            for university in universities:
                # Construct the SQL query
                query = text("""
                    INSERT INTO ko_university (
                        university, department, image_url, district, susi_competition, jungsi_competiton,
                        total_recruit_num, type_info, type_competition, recruit_num,
                        last_year_50_percent_grade, last_year_70_percent_grade, type_category_1,
                        type_category_2, educational_object, education_course, career_job_category,
                        department_without_jugan
                    )
                    VALUES (
                        :university, :department, :image_url, :district, :susi_competition, :jungsi_competiton,
                        :total_recruit_num, :type_info, :type_competition, :recruit_num,
                        :last_year_50_percent_grade, :last_year_70_percent_grade, :type_category_1,
                        :type_category_2, :educational_object, :education_course, :career_job_category,
                        :department_without_jugan
                    )
                """)
                print(f'university = {university["department_without_jugan"]}')

                # Execute the query
                await session.execute(query, university)

            # Commit the transaction
            await session.commit()
            print("Data inserted successfully!")

        except Exception as e:
            print(f"An error occurred: {e}")
            await session.rollback()

# Run the insertion function
import asyncio
asyncio.run(insert_universities())
