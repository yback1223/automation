import json
import random
import mysql.connector


def load_existing_data(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"Loaded {len(data)} existing entries.")
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        print("No existing data found or file is corrupted. Starting fresh.")
        return []


# root:Tnstjd12%40@10.10.112.75:3306

# MySQL 연결 설정
# connection = mysql.connector.connect(
#     host="10.10.112.75",
#     user="root",
#     password="Tnstjd12@",
#     database="job_db"
# )

# connection = mysql.connector.connect(
#     host="10.10.112.148",
#     user="yback_root",
#     password="0000",
#     database="job_db"
# )

connection = mysql.connector.connect(
    host="14.63.177.168",
    user="ieum",
    password="Ieum!2024",
    database="job_db"
)

major_job_data = load_existing_data("main_job_crawled_data_copy.json")
cursor = connection.cursor(dictionary=True)

job_list = [
    # "교사",
    # "작가",
    # "홈패션",
    # "사회복지사",
    # "큐레이터",
    "청소년지도사",
    # "교수",
    # "디자이너",
    # "연기자",
    # "연주가",
    # "프로그래머",
    # "작곡가",
    # "패션디자이너",
    # "엔지니어",
    # "가정보육사",
    # "상담사",
    # "한의사",
    # "심리학자",
    # "상담심리학자",
    # "웨딩플래너",
    # "임상심리사",
    # "세공사",
    # "네이미스트"
]

mapped_jobs = {}

for job in job_list:
    matching_entries = [entry for entry in major_job_data if entry.get("search_keyword") == job]
    mapped_jobs[job] = matching_entries

with open("mapped_jobs.json", "w", encoding="utf-8") as f:
    json.dump(mapped_jobs, f, indent=4, ensure_ascii=False)
    print("mapped_jobs.json has been created.")

for job in job_list:
    query = "SELECT * FROM job_db.jobs WHERE job LIKE %s"
    cursor.execute(query, (f"%{job}%",))
    result = cursor.fetchall()

    for row in result:
        if "tasks" in row and row["tasks"]:
            try:
                
                data = json.loads(row["tasks"])
                category_names = [category["name"] for category in data["categories"]]

                random_education_data = random.sample(mapped_jobs[job], min(5, len(mapped_jobs[job])))
                

                processed_education_data = [
                    {
                        "name": education["program_name"],
                        "type": "education",
                        "content": f"링크: {education.get('link', '')}, 기관: {education.get('corp_name', '')}, 위치: {education.get('program_rough_location', '')}, 기간: {education.get('program_term', '')}, 요일: {', '.join(education.get('program_days', []))}, 공지사항: {education.get('notice', '')}, 활동 목표: {education.get('high_goal') or education.get('middle_goal', '')}"
                    } for education in random_education_data
                ]

                print(f'{[data.get("name") for data in processed_education_data]}')
                categories = []
                for one_data in data["categories"]:
                    if one_data['name'].endswith("과"):
                        one_data['type'] = 'major'
            
                    if one_data.get('type') == 'major' or one_data['name'].endswith("과"):
                        categories.append({
                            "name": one_data["name"],
                            "type": "major"
                        })
                categories.extend(processed_education_data)
                    
                output = {"categories": categories}

                update_query = """
                UPDATE job_db.jobs
                SET tasks = %s
                WHERE id = %s
                """
                cursor.execute(update_query, (json.dumps(output, ensure_ascii=False), row["id"]))
                connection.commit()
                print(f"Updated row ID {row['id']} with new tasks data.")

            except json.JSONDecodeError as e:
                print(f"JSONDecodeError for row ID {row['id']}: {e}")
            except Exception as e:
                print(f"Error processing row ID {row['id']}: {e}")
        else:
            print(f"No tasks field or empty for row ID {row['id']}")


cursor.close()
connection.close()
