from driver import Driver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.remote.webelement import WebElement
from bs4 import BeautifulSoup
from typing import Any, Union

import re, os
import clipboard, time
import pandas as pd
import math, random, json


WORK_TERM_SLEEP = 1
CRAWLED_FILE = "crawled_program_details_tmp.json"

class CareernetMajorJobMatrixCrawler:
    def __init__(self):
        self.driver = Driver().set_chrome()
        self.actions = ActionChains(self.driver)
        self.current_page = 1
        self.driver.get("https://www.career.go.kr/cnet/front/base/job/jobMajor/jobMajorMatrix.do")

    def crawl_jobs(self):
        job_data = []

        try:
            # 페이지가 완전히 로드될 때까지 기다립니다
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "matrix-word-list"))
            )
            
            # 한글 자음 버튼들을 찾습니다
            big_category_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".matrix-word-list li a")
            print(f'len(big_category_buttons): {len(big_category_buttons)}')
            
            for big_category_button in big_category_buttons:
                big_category_button.click()
                time.sleep(WORK_TERM_SLEEP)

                # 직업 목록이 로드될 때까지 기다립니다
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "matrix-job-list"))
                )

                job_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".matrix-job-list li a")

                for job_button in job_buttons:
                    try:
                        job_name = job_button.text
                        job_button.click()
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
            self.crawl_jobs()
            print('end crawl job list')

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


if __name__ == "__main__":
    crawler = CareernetMajorJobMatrixCrawler()
    crawler.run()
