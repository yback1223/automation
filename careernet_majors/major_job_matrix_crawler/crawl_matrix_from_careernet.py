from careernet_majors.utils.driver import Driver
from careernet_majors import RESOURCE_DIR

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import os
import time
import json


WORK_TERM_SLEEP = 1

OUTPUT_FILE = os.path.join(RESOURCE_DIR, "careernet_job_matrix.json")

class CareernetMajorJobMatrixCrawler:
    def __init__(self):
        self.driver = Driver().set_chrome()
        self.actions = ActionChains(self.driver)
        self.current_page = 1
        self.driver.get("https://www.career.go.kr/cnet/front/base/job/jobMajor/jobMajorMatrix.do")

    def get_majors_for_job(self, job_name: str) -> list[str]:
        majors = []

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "matrix-table"))
            )

            job_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".matrix-job-list li a")
            target_job_button = None
            for button in job_buttons:
                if button.text.strip() == job_name:
                    target_job_button = button
                    break

            if not target_job_button:
                print(f"직업 '{job_name}'을(를) 찾을 수 없습니다.")
                return majors

            target_job_button.click()
            time.sleep(WORK_TERM_SLEEP)

            thead = self.driver.find_element(By.TAG_NAME, "thead")
            header_rows = thead.find_elements(By.TAG_NAME, "tr")
            job_headers = header_rows[1].find_elements(By.TAG_NAME, "th")  # 두 번째 행에 직업명 있음

            selected_col_index = None
            for idx, header in enumerate(job_headers):
                if "selected" in header.get_attribute("class"):
                    selected_col_index = idx - 2  # th 2개("구분", "학과관련 진출직업")를 빼고 계산
                    break

            if selected_col_index is None:
                print(f"'{job_name}'에 대한 'selected' 열을 찾을 수 없습니다.")
                return majors

            # 테이블 바디에서 "●"가 있는 학과 추출
            tbody_list = self.driver.find_elements(By.TAG_NAME, "tbody")
            for tbody in tbody_list:
                rows = tbody.find_elements(By.TAG_NAME, "tr")
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) > selected_col_index and "●" in cells[selected_col_index].text:
                        major = row.find_element(By.CLASS_NAME, "ta-left").text
                        majors.append(major)

            print(f"'{job_name}'에 대한 관련 학과: {majors}")

        except Exception as e:
            print(f"'{job_name}'의 학과를 찾는 중 오류 발생: {e}")

        return majors


    def crawl_jobs(self):
        job_data = []

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "matrix-word-list"))
            )
            
            big_category_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".matrix-word-list li a")
            print(f'len(big_category_buttons): {len(big_category_buttons)}')
            
            for big_category_button in big_category_buttons:
                big_category_button.click()
                time.sleep(WORK_TERM_SLEEP)

                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "matrix-job-list"))
                )

                job_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".matrix-job-list li a")

                for job_button in job_buttons:
                    try:
                        job_name = job_button.text
                        job_button.click()

                        majors = self.get_majors_for_job(job_name)
                        job_data.append({
                            "job_name": job_name,
                            "majors": majors
                        })

                        print(f"Crawled Job: {job_name}")
                        time.sleep(WORK_TERM_SLEEP)
                    except Exception as e:
                        print(f"Error extracting job link: {e}")

                time.sleep(WORK_TERM_SLEEP)

        except Exception as e:
            print(f"Error crawling job list: {e}")

        return job_data


    def run(self):
        try:
            print('start crawl job list')
            job_data = self.crawl_jobs()
            print('end crawl job list')

            if job_data:
                self.save_to_json(OUTPUT_FILE, job_data)

        except Exception as e:
            print(f"Error running: {e}")
            return []



    def save_to_json(self, crawled_file: str, crawled_data: dict[str, str]) -> None:
        try:
            existing_data = []

            if os.path.exists(crawled_file) and os.path.getsize(crawled_file) > 0:
                with open(crawled_file, "r", encoding="utf-8") as json_file:
                    existing_data = json.load(json_file)

            existing_data.append(crawled_data)

            with open(crawled_file, "w", encoding="utf-8") as json_file:
                json.dump(existing_data, json_file, ensure_ascii=False, indent=4)

            print(f"Data successfully saved to {crawled_file}")
        except Exception as e:
            print(f"Error saving data to JSON: {e}")